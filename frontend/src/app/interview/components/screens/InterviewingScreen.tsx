'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Mic, Volume2, PhoneOff, Video, Settings, X } from 'lucide-react';
import { saveVideoToIndexedDB } from '@/lib/indexedDB';
import { videoApi, interviewApi } from '@/lib/auth-client';
import { InterviewQuestion } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface InterviewingScreenProps {
    onEnd: (videoId?: string) => void;
    questions: InterviewQuestion[];
    sessionId: string;
}

export default function InterviewingScreen({ onEnd, questions: initialQuestions, sessionId }: InterviewingScreenProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const videoRecorderRef = useRef<MediaRecorder | null>(null);
    const audioRecorderRef = useRef<MediaRecorder | null>(null);
    const videoChunksRef = useRef<Blob[]>([]);
    const isEndingRef = useRef(false);

    const [volume, setVolume] = useState(75);
    const [isAudioRecording, setIsAudioRecording] = useState(false);
    const [showProgress, setShowProgress] = useState(true);
    
    const MAX_QUESTIONS = 10;
    const [questions, setQuestions] = useState<InterviewQuestion[]>(initialQuestions);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
    const [isLoadingTTS, setIsLoadingTTS] = useState(false);
    const [videoId, setVideoId] = useState<string | null>(null);

    const uploadVideo = useCallback(async (videoBlob: Blob): Promise<string | null> => {
        try {
            await saveVideoToIndexedDB(videoBlob);
            console.log('[DEBUG] Video saved to IndexedDB');

            const response = await videoApi.uploadVideo(sessionId, videoBlob);

            if (response.success && response.data) {
                console.log('[DEBUG] Video uploaded successfully, video_id:', response.data.video_id);
                return response.data.video_id;
            } else {
                console.error('[DEBUG] Video upload failed:', response.error);
                return null;
            }
        } catch (error) {
            console.error('[DEBUG] Video upload error:', error);
            return null;
        }
    }, [sessionId]);

    const handleInterviewComplete = useCallback(async () => {
        console.log('[DEBUG] Handling interview completion');
        isEndingRef.current = true;

        if (videoRecorderRef.current && videoRecorderRef.current.state === 'recording') {
            videoRecorderRef.current.stop();
        } else {
            console.log('[DEBUG] Video recorder not active, ending immediately');
            onEnd(videoId || undefined);
        }
    }, [onEnd, videoId]);

    const submitAnswer = useCallback(async (audioBlob: Blob) => {
        if (isSubmittingAnswer) return;
        
        setIsSubmittingAnswer(true);
        
        try {
            const currentQuestion = questions[currentQuestionIndex];
            if (!currentQuestion) throw new Error("Question not found");

            const questionId = currentQuestion.id || `temp-${currentQuestionIndex}`;
            console.log(`[DEBUG] Submitting answer for question ${currentQuestionIndex + 1} (ID: ${questionId})`);

            const response = await interviewApi.submitAnswer(sessionId, questionId, audioBlob);

            if (response.success && response.data) {
                const { next_question, is_final } = response.data;

                if (next_question && questions.length < MAX_QUESTIONS && !is_final) {
                    console.log('[DEBUG] Received next question:', next_question);
                    setQuestions(prev => [...prev, next_question]);
                    setCurrentQuestionIndex(prev => prev + 1);
                } else {
                    console.log('[DEBUG] No more questions or limit reached, ending interview');
                    await handleInterviewComplete();
                }
            } else {
                console.error('Failed to submit answer:', response.error);
                alert('답변 제출에 실패했습니다. 잠시 후 다시 시도해주세요.');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            alert('오류가 발생했습니다.');
        } finally {
            setIsSubmittingAnswer(false);
        }
    }, [isSubmittingAnswer, questions, currentQuestionIndex, sessionId, handleInterviewComplete, MAX_QUESTIONS]);

    useEffect(() => {
        let stream: MediaStream | null = null;

        const startCamera = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 1280, height: 720 },
                    audio: true
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }

                const videoRecorder = new MediaRecorder(stream, {
                    mimeType: 'video/webm;codecs=vp9'
                });

                videoChunksRef.current = [];

                videoRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        videoChunksRef.current.push(event.data);
                    }
                };

                videoRecorder.onstop = async () => {
                    console.log('[DEBUG] Video recording stopped, uploading...');
                    const videoBlob = new Blob(videoChunksRef.current, { type: 'video/webm' });
                    const uploadedVideoId = await uploadVideo(videoBlob);
                    
                    if (uploadedVideoId) setVideoId(uploadedVideoId);

                    if (isEndingRef.current) {
                        onEnd(uploadedVideoId || undefined);
                    }
                };

                videoRecorderRef.current = videoRecorder;
                videoRecorder.start();

            } catch (error) {
                console.error('Camera access error:', error);
                alert('카메라 또는 마이크 권한이 필요합니다.');
            }
        };

        startCamera();

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            if (videoRecorderRef.current && videoRecorderRef.current.state !== 'inactive') {
                videoRecorderRef.current.stop();
            }
        };
    }, [uploadVideo, onEnd]);

    useEffect(() => {
        if (!questions || questions.length === 0 || currentQuestionIndex >= questions.length) return;

        const currentQuestion = questions[currentQuestionIndex];
        let audio: HTMLAudioElement | null = null;

        const playQuestionAudio = async () => {
            setIsLoadingTTS(true);
            try {
                const response = await fetch(`${API_URL}/api/interviews/questions/${currentQuestion.id}/tts`);
                if (!response.ok) throw new Error('TTS fetch failed');

                const data = await response.json();
                const audioUrl = data.audio_url.startsWith('http') ? data.audio_url : `${API_URL}${data.audio_url}`;

                if (audioRef.current) {
                    audioRef.current.pause();
                    audioRef.current.currentTime = 0;
                }

                audio = new Audio(audioUrl);
                audio.volume = volume / 100;
                audioRef.current = audio;

                await audio.play();
            } catch (error) {
                console.warn('[TTS] Playback failed:', error);
            } finally {
                setIsLoadingTTS(false);
            }
        };

        playQuestionAudio();

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.currentTime = 0;
            }
        };
    }, [currentQuestionIndex, questions, volume]);

    const startAudioRecording = () => {
        if (!videoRef.current?.srcObject) {
            console.error('No video stream available for audio extraction');
            return;
        }

        try {
            const stream = videoRef.current.srcObject as MediaStream;
            const audioStream = new MediaStream(stream.getAudioTracks());

            const audioRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
            const chunks: Blob[] = [];

            audioRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunks.push(e.data);
            };

            audioRecorder.onstop = async () => {
                console.log(`[DEBUG] Audio recording finished for Q${currentQuestionIndex + 1}`);
                const audioBlob = new Blob(chunks, { type: 'audio/webm' });
                await submitAnswer(audioBlob);
            };

            audioRecorderRef.current = audioRecorder;
            audioRecorder.start();
            setIsAudioRecording(true);
        } catch (e) {
            console.error('Failed to start audio recording:', e);
        }
    };

    const stopAudioRecording = () => {
        if (audioRecorderRef.current && audioRecorderRef.current.state === 'recording') {
            audioRecorderRef.current.stop();
            setIsAudioRecording(false);
        }
    };

    if (!questions || questions.length === 0) {
        return (
            <motion.div className="flex-1 flex items-center justify-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <p className="text-gray-600">질문을 불러오는 중입니다...</p>
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
                
                <div className="flex-[2] flex flex-col gap-4 min-h-0">
                    <div className="bg-white rounded-3xl p-6 shadow-sm flex-1 flex flex-col min-h-0 overflow-hidden border border-[#E5E5EC]">
                        
                        {currentQuestion && (
                            <div className="mb-3 p-4 bg-gradient-to-r from-primary/10 to-brand-purple-light/10 border-l-4 border-primary rounded-md flex-shrink-0">
                                <div className="flex items-center justify-between gap-4">
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded whitespace-nowrap">
                                            질문 {currentQuestionIndex + 1} / {questions.length < MAX_QUESTIONS ? '?' : MAX_QUESTIONS}
                                        </span>
                                        <p className="text-gray-900 font-medium text-sm">
                                            {currentQuestion.text}
                                            {isLoadingTTS && <span className="ml-2 text-xs text-gray-500 animate-pulse">(음성 로딩...)</span>}
                                        </p>
                                    </div>
                                    
                                    <div className="flex-shrink-0">
                                        {!isAudioRecording ? (
                                            <button
                                                onClick={startAudioRecording}
                                                disabled={isSubmittingAnswer}
                                                className="px-4 py-2 bg-primary text-white hover:bg-brand-purple transition-colors flex items-center gap-2 shadow-lg text-sm rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                <Mic className="w-4 h-4" />
                                                <span>{isSubmittingAnswer ? '처리 중...' : '녹음 시작'}</span>
                                            </button>
                                        ) : (
                                            <button
                                                onClick={stopAudioRecording}
                                                className="px-4 py-2 bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center gap-2 shadow-lg animate-pulse text-sm rounded-md"
                                            >
                                                <div className="w-2 h-2 bg-white rounded-full"></div>
                                                <span>중지</span>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {isSubmittingAnswer && (
                             <div className="mb-2 text-xs text-center text-gray-600 animate-pulse">
                                답변을 저장하고 다음 질문을 생성하고 있습니다...
                             </div>
                        )}

                        <motion.div layoutId="main-interview-area" className="relative bg-gray-900 rounded-2xl overflow-hidden flex-1 min-h-0">
                            <img src="/avatar.png" alt="Avatar" className="absolute inset-0 w-full h-full object-cover" />

                            <motion.div 
                                layoutId="user-camera"
                                className="absolute top-4 right-4 w-64 h-36 bg-gray-800 rounded-xl overflow-hidden shadow-lg border-2 border-gray-700"
                                transition={{ type: "spring", stiffness: 120, damping: 30 }}
                            >
                                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                            </motion.div>

                            <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-3">
                                <div className="bg-gray-800/80 backdrop-blur-sm rounded-full p-3 shadow-lg">
                                    <Volume2 className="w-5 h-5 text-white" />
                                </div>
                                <div
                                    className="relative h-32 w-6 bg-gray-700 rounded-full overflow-hidden cursor-pointer"
                                    onClick={(e) => {
                                        const rect = e.currentTarget.getBoundingClientRect();
                                        const newVolume = Math.max(0, Math.min(100, 100 - ((e.clientY - rect.top) / rect.height) * 100));
                                        setVolume(Math.round(newVolume));
                                    }}
                                >
                                    <div 
                                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-primary to-brand-purple-light rounded-full transition-all"
                                        style={{ height: `${volume}%` }}
                                    />
                                </div>
                            </div>

                            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4">
                                <button className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white"><Mic className="w-5 h-5" /></button>
                                <button className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white"><Volume2 className="w-5 h-5" /></button>
                                <button onClick={handleInterviewComplete} className="w-14 h-14 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white shadow-lg">
                                    <PhoneOff className="w-6 h-6" />
                                </button>
                                <button className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white"><Video className="w-5 h-5" /></button>
                                <button className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white"><Settings className="w-5 h-5" /></button>
                            </div>
                        </motion.div>
                    </div>
                </div>

                {showProgress && (
                    <motion.div
                        className="fixed bottom-6 right-6 bg-white rounded-2xl p-4 shadow-lg border border-gray-200"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold text-gray-900 text-sm">면접 진행 상황</h3>
                            <button onClick={() => setShowProgress(false)} className="p-1 hover:bg-gray-100 rounded-full">
                                <X className="w-4 h-4 text-gray-500" />
                            </button>
                        </div>
                        <div className="space-y-2 w-48">
                            <div className="flex justify-between text-xs">
                                <span className="text-gray-600">진행률</span>
                                <span className="font-semibold">{currentQuestionIndex + 1} / {questions.length < MAX_QUESTIONS ? '?' : MAX_QUESTIONS}</span>
                            </div>
                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${((currentQuestionIndex + 1) / MAX_QUESTIONS) * 100}%` }} />
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
}