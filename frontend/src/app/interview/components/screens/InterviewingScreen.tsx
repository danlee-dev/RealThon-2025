'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, Volume2, PhoneOff, Video, Settings, X } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Question {
    id: string;
    text: string;
    order: number;
    type: string;
    source: string;
}

interface InterviewingScreenProps {
    onEnd: () => void;
    questions: Question[];
    sessionId: string;
}

export default function InterviewingScreen({ onEnd, questions: initialQuestions, sessionId }: InterviewingScreenProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const audioRecorderRef = useRef<MediaRecorder | null>(null);
    const [volume, setVolume] = useState(75);
    const [isRecording, setIsRecording] = useState(false);
    const [showProgress, setShowProgress] = useState(true);
    const [questions, setQuestions] = useState<Question[]>(initialQuestions);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [isLoadingTTS, setIsLoadingTTS] = useState(false);
    const [isProcessingAnswer, setIsProcessingAnswer] = useState(false);
    const [answerCount, setAnswerCount] = useState(0); // 총 답변 횟수 (홀수: 메인 질문, 짝수: 꼬리 질문)

    // 카메라 시작
    useEffect(() => {
        const startCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 1280, height: 720 },
                    audio: true
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (error) {
                console.error('Camera access error:', error);
            }
        };

        startCamera();

        return () => {
            if (videoRef.current?.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // TTS: 질문이 바뀔 때마다 음성 재생
    useEffect(() => {
        const playQuestionAudio = async () => {
            if (questions.length === 0 || currentQuestionIndex >= questions.length) return;

            const currentQuestion = questions[currentQuestionIndex];
            setIsLoadingTTS(true);

            try {
                console.log('[TTS] Fetching audio for question:', currentQuestion.id);
                const response = await fetch(`${API_URL}/api/interviews/questions/${currentQuestion.id}/tts`);

                if (!response.ok) {
                    throw new Error('TTS failed');
                }

                const data = await response.json();
                // 백엔드가 전체 URL을 반환하면 그대로 사용, 아니면 API_URL 붙이기
                const audioUrl = data.audio_url.startsWith('http')
                    ? data.audio_url
                    : `${API_URL}${data.audio_url}`;

                console.log('[TTS] Audio URL:', audioUrl);

                // 오디오 재생
                if (audioRef.current) {
                    audioRef.current.pause();
                }

                const audio = new Audio(audioUrl);
                audio.volume = volume / 100;
                audioRef.current = audio;

                audio.play().catch(err => {
                    console.error('[TTS] Audio play error:', err);
                });

                console.log('[TTS] Audio playing:', audioUrl);
            } catch (error) {
                console.error('[TTS] Error:', error);
            } finally {
                setIsLoadingTTS(false);
            }
        };

        playQuestionAudio();
    }, [currentQuestionIndex, questions, volume]);

    // 음성 녹음 시작
    const startAudioRecording = () => {
        if (!videoRef.current?.srcObject) return;

        const stream = videoRef.current.srcObject as MediaStream;
        const audioStream = new MediaStream(stream.getAudioTracks());

        const audioRecorder = new MediaRecorder(audioStream, {
            mimeType: 'audio/webm'
        });

        const chunks: Blob[] = [];

        audioRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
            }
        };

        audioRecorder.onstop = async () => {
            setIsProcessingAnswer(true);

            try {
                const audioBlob = new Blob(chunks, { type: 'audio/webm' });
                const currentQuestion = questions[currentQuestionIndex];
                const newAnswerCount = answerCount + 1; // 1부터 시작

                console.log(`[ANSWER] Processing answer #${newAnswerCount}`);

                // 1. STT: 음성 → 텍스트 변환
                console.log('[STT] Converting audio to text...');
                const sttFormData = new FormData();
                sttFormData.append('audio', audioBlob, 'answer.webm');

                const sttResponse = await fetch(`${API_URL}/api/interviews/stt`, {
                    method: 'POST',
                    body: sttFormData,
                });

                if (!sttResponse.ok) {
                    throw new Error('STT failed');
                }

                const sttData = await sttResponse.json();
                const answerText = sttData.text;
                console.log('[STT] Transcribed text:', answerText);

                // 2. 답변 저장
                console.log('[SAVE] Saving answer...');
                const answerResponse = await fetch(`${API_URL}/api/interviews/questions/${currentQuestion.id}/answers`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question_id: currentQuestion.id,
                        text: answerText,
                    }),
                });

                if (!answerResponse.ok) {
                    throw new Error('Answer save failed');
                }

                console.log('[SAVE] Answer saved');

                // 3. 답변 횟수 증가
                setAnswerCount(newAnswerCount);

                // 4. 꼬리 질문 생성 여부 결정
                // 홀수 번째(1, 3, 5): 메인 질문 → 꼬리 질문 생성
                // 짝수 번째(2, 4, 6): 꼬리 질문 → 생성 안 함
                const isOddAnswer = newAnswerCount % 2 === 1;

                if (isOddAnswer && newAnswerCount < 6) {
                    // 홀수 번째이고 6번째 전이면 꼬리 질문 생성
                    console.log('[FOLLOWUP] Generating followup question...');
                    const followupResponse = await fetch(
                        `${API_URL}/api/interviews/questions/${currentQuestion.id}/followup?answer_text=${encodeURIComponent(answerText)}`,
                        { method: 'POST' }
                    );

                    if (followupResponse.ok) {
                        const followupQuestion = await followupResponse.json();
                        console.log('[FOLLOWUP] New question:', followupQuestion.text);

                        // 꼬리 질문을 questions 배열에 추가 (현재 질문 바로 다음에)
                        setQuestions(prev => {
                            const newQuestions = [...prev];
                            newQuestions.splice(currentQuestionIndex + 1, 0, followupQuestion);
                            return newQuestions;
                        });
                    } else {
                        console.warn('[FOLLOWUP] Failed to generate followup question');
                    }
                } else {
                    console.log(`[FOLLOWUP] Skipping followup (answer #${newAnswerCount} is even)`);
                }

                // 5. 다음 질문으로 이동 또는 면접 종료
                if (newAnswerCount >= 6) {
                    // 6번째 답변 완료 → 면접 종료
                    console.log('[INTERVIEW] 6 answers completed, ending interview');
                    setTimeout(() => {
                        onEnd();
                    }, 1000);
                } else {
                    setCurrentQuestionIndex(prev => prev + 1);
                }
            } catch (error) {
                console.error('[ANSWER PROCESSING] Error:', error);
                alert('답변 처리 중 오류가 발생했습니다.');
            } finally {
                setIsProcessingAnswer(false);
            }
        };

        audioRecorderRef.current = audioRecorder;
        audioRecorder.start();
        setIsRecording(true);
        console.log('[RECORDING] Started');
    };

    // 음성 녹음 중지
    const stopAudioRecording = () => {
        if (audioRecorderRef.current && isRecording) {
            audioRecorderRef.current.stop();
            setIsRecording(false);
            console.log('[RECORDING] Stopped');
        }
    };

    // 질문이 없는 경우
    if (questions.length === 0) {
        return (
            <motion.div
                className="flex-1 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
            >
                <div className="text-center">
                    <p className="text-gray-600">질문을 불러오는 중 오류가 발생했습니다.</p>
                    <button
                        onClick={onEnd}
                        className="mt-4 px-6 py-2 bg-primary text-white rounded-xl hover:bg-brand-purple transition-colors"
                    >
                        돌아가기
                    </button>
                </div>
            </motion.div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];

    return (
        <motion.div
            className="flex-1 flex flex-col overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
        >
            <div className="flex-1 flex gap-6 p-6" style={{ backgroundColor: 'rgb(250, 250, 248)' }}>
                {/* Left Column - Video */}
                <div className="flex-[2] flex flex-col gap-4 min-h-0">
                    <div className="bg-white rounded-3xl p-6 shadow-sm flex-1 flex flex-col min-h-0 overflow-hidden" style={{ border: '1px solid #E5E5EC' }}>
                        {/* Question and Recording Controls */}
                        <div className="mb-3 p-4 bg-gradient-to-r from-primary/10 to-brand-purple-light/10 border-l-4 border-primary flex-shrink-0" style={{ borderRadius: '0.375rem' }}>
                            <div className="flex items-center justify-between gap-4">
                                <div className="flex items-center gap-3">
                                    <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded whitespace-nowrap">
                                        질문 {currentQuestionIndex + 1} / {questions.length}
                                    </span>
                                    <p className="text-gray-900 font-medium text-sm">
                                        {currentQuestion.text}
                                        {isLoadingTTS && <span className="ml-2 text-xs text-gray-500">(음성 로딩 중...)</span>}
                                    </p>
                                </div>
                                <div className="flex-shrink-0">
                                    {!isRecording ? (
                                        <button
                                            onClick={startAudioRecording}
                                            disabled={isProcessingAnswer}
                                            className="px-4 py-2 bg-primary text-white hover:bg-brand-purple transition-colors flex items-center gap-2 shadow-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                            style={{ borderRadius: '0.375rem' }}
                                        >
                                            <Mic className="w-4 h-4" />
                                            <span>녹음 시작</span>
                                        </button>
                                    ) : (
                                        <button
                                            onClick={stopAudioRecording}
                                            className="px-4 py-2 bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center gap-2 shadow-lg animate-pulse text-sm"
                                            style={{ borderRadius: '0.375rem' }}
                                        >
                                            <div className="w-2 h-2 bg-white rounded-full"></div>
                                            <span>중지</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                            {isProcessingAnswer && (
                                <div className="mt-2 text-xs text-gray-600">답변 처리 중... (STT 변환 → 저장 → 꼬리 질문 생성)</div>
                            )}
                        </div>

                        {/* Video Area */}
                        <motion.div
                            layoutId="main-interview-area"
                            className="relative bg-gray-900 rounded-2xl overflow-hidden flex-1 min-h-0"
                        >
                            {/* Main Video - Avatar Background */}
                            <img
                                src="/avatar.png"
                                alt="Interview Avatar"
                                className="absolute inset-0 w-full h-full object-cover"
                            />

                            {/* User Camera */}
                            <motion.div
                                layoutId="user-camera"
                                className="absolute top-4 right-4 w-64 h-36 bg-gray-800 rounded-xl overflow-hidden shadow-lg border-2 border-gray-700"
                                transition={{ type: "spring", stiffness: 120, damping: 30 }}
                            >
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className="w-full h-full object-cover"
                                />
                            </motion.div>

                            {/* Volume Slider */}
                            <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-3">
                                <div className="bg-gray-800/80 backdrop-blur-sm rounded-full p-3 shadow-lg">
                                    <Volume2 className="w-5 h-5 text-white" />
                                </div>
                                <div
                                    className="relative h-32 w-6 bg-gray-700 rounded-full overflow-hidden cursor-pointer"
                                    onClick={(e) => {
                                        const rect = e.currentTarget.getBoundingClientRect();
                                        const y = e.clientY - rect.top;
                                        const newVolume = Math.max(0, Math.min(100, 100 - (y / rect.height) * 100));
                                        setVolume(Math.round(newVolume));
                                        if (audioRef.current) {
                                            audioRef.current.volume = newVolume / 100;
                                        }
                                    }}
                                >
                                    <div
                                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-primary to-brand-purple-light rounded-full transition-all duration-150"
                                        style={{ height: `${volume}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4">
                                <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
                                    <Mic className="w-5 h-5" />
                                </button>
                                <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
                                    <Volume2 className="w-5 h-5" />
                                </button>
                                <button
                                    onClick={onEnd}
                                    className="w-14 h-14 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white"
                                >
                                    <PhoneOff className="w-6 h-6" />
                                </button>
                                <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
                                    <Video className="w-5 h-5" />
                                </button>
                                <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
                                    <Settings className="w-5 h-5" />
                                </button>
                            </div>
                        </motion.div>
                    </div>
                </div>

                {/* Floating Progress Popup */}
                {showProgress && (
                    <motion.div
                        className="fixed bottom-6 right-6 bg-white rounded-2xl p-4 shadow-lg border border-gray-200"
                        style={{ border: '1px solid #E5E5EC' }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold text-gray-900 text-sm">면접 진행 상황</h3>
                            <button
                                onClick={() => setShowProgress(false)}
                                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                            >
                                <X className="w-4 h-4 text-gray-500" />
                            </button>
                        </div>
                        <div className="space-y-2 w-48">
                            <div className="flex justify-between text-xs">
                                <span className="text-gray-600">현재 질문</span>
                                <span className="font-semibold">{currentQuestionIndex + 1} / {questions.length}</span>
                            </div>
                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary rounded-full transition-all"
                                    style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
}
