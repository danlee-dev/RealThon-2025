'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, Volume2, PhoneOff, Video, Settings, X } from 'lucide-react';
import { saveVideoToIndexedDB } from '@/lib/indexedDB';
import { videoApi, interviewApi } from '@/lib/auth-client';
import { InterviewQuestion } from '@/types';

interface InterviewingScreenProps {
    onEnd: (videoId?: string) => void;
    questions: InterviewQuestion[];
    sessionId: string;
}

export default function InterviewingScreen({ onEnd, questions: initialQuestions, sessionId }: InterviewingScreenProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioRecorderRef = useRef<MediaRecorder | null>(null);
    const videoRecorderRef = useRef<MediaRecorder | null>(null);
    const videoChunksRef = useRef<Blob[]>([]);
    const [volume, setVolume] = useState(75);
    const [isRecording, setIsRecording] = useState(false);
    const [isAudioRecording, setIsAudioRecording] = useState(false);
    const [isVideoRecording, setIsVideoRecording] = useState(false);
    const [showProgress, setShowProgress] = useState(true);

    // Dynamic question management
    const MAX_QUESTIONS = 10;
    const [questions, setQuestions] = useState<InterviewQuestion[]>(initialQuestions);
    const [questionIds, setQuestionIds] = useState<string[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
    const [videoId, setVideoId] = useState<string | null>(null);
    const isEndingRef = useRef(false);

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

                // Start video recording
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
                    console.log('[DEBUG] Video recording stopped, preparing to upload');
                    const videoBlob = new Blob(videoChunksRef.current, { type: 'video/webm' });
                    const uploadedVideoId = await uploadVideo(videoBlob);

                    if (uploadedVideoId) {
                        setVideoId(uploadedVideoId);
                    }

                    // Only trigger onEnd if we are intentionally ending the interview
                    if (isEndingRef.current) {
                        console.log('[DEBUG] Interview ending, triggering onEnd with videoId:', uploadedVideoId);
                        onEnd(uploadedVideoId || undefined);
                    }
                };

                videoRecorderRef.current = videoRecorder;
                videoRecorder.start();
                setIsVideoRecording(true);
                console.log('[DEBUG] Video recording started');
            } catch (error) {
                console.error('Camera access error:', error);
            }
        };

        startCamera();

        return () => {
            if (videoRecorderRef.current && isVideoRecording) {
                videoRecorderRef.current.stop();
            }
            if (videoRef.current?.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Upload video to backend
    const uploadVideo = async (videoBlob: Blob): Promise<string | null> => {
        try {
            // Save to IndexedDB first for local playback
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
    };

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
            console.log(`[DEBUG] Question ${currentQuestionIndex + 1} audio recorded`);

            // Submit audio and get next question
            const audioBlob = new Blob(chunks, { type: 'audio/webm' });
            await submitAnswer(audioBlob);
        };

        audioRecorderRef.current = audioRecorder;
        audioRecorder.start();
        setIsAudioRecording(true);
        console.log(`[DEBUG] Recording answer for question ${currentQuestionIndex + 1}`);
    };

    const handleInterviewComplete = async () => {
        console.log('[DEBUG] Handling interview completion');
        isEndingRef.current = true;

        if (videoRecorderRef.current && videoRecorderRef.current.state === 'recording') {
            videoRecorderRef.current.stop();
        } else {
            console.log('[DEBUG] Video recorder not active, ending immediately');
            onEnd(videoId || undefined);
        }
    };

    const submitAnswer = async (audioBlob: Blob) => {
        setIsSubmittingAnswer(true);
        try {
            const currentQuestion = questions[currentQuestionIndex];
            // Fallback for initial questions if they don't have IDs (shouldn't happen with correct API usage)
            const questionId = currentQuestion?.id || `temp-${currentQuestionIndex}`;

            console.log(`[DEBUG] Submitting answer for question ${currentQuestionIndex + 1} (ID: ${questionId})`);

            const response = await interviewApi.submitAnswer(sessionId, questionId, audioBlob);

            if (response.success && response.data) {
                const { next_question, is_final } = response.data;

                if (next_question && questions.length < MAX_QUESTIONS) {
                    console.log('[DEBUG] Received next question:', next_question);
                    setQuestions(prev => [...prev, next_question]);
                    setCurrentQuestionIndex(prev => prev + 1);
                } else {
                    console.log('[DEBUG] No more questions or limit reached, ending interview');
                    await handleInterviewComplete();
                }
            } else {
                console.error('Failed to submit answer:', response.error);
                // If submission fails, we might want to let user retry or just move on?
                // For now, let's try to move to next if possible or end.
                // But we don't have a next question if the API failed.
                // Maybe just end?
                alert('답변 제출에 실패했습니다. 다시 시도하거나 면접을 종료해주세요.');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            alert('오류가 발생했습니다.');
        } finally {
        }
    };

    const stopAudioRecording = async () => {
        if (audioRecorderRef.current && isAudioRecording) {
            audioRecorderRef.current.stop();
            setIsAudioRecording(false);
            // The onstop handler calls submitAnswer
        }
    };

    // 질문이 없는 경우 처리
    if (!questions || questions.length === 0) {
        return (
            <motion.div
                className="flex-1 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
            >
                <div className="text-center">
                    <p className="text-gray-600">질문을 불러오는 중입니다...</p>
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
                        {currentQuestion && (
                            <div className="mb-3 p-4 bg-gradient-to-r from-primary/10 to-brand-purple-light/10 border-l-4 border-primary flex-shrink-0" style={{ borderRadius: '0.375rem' }}>
                                <div className="flex items-center justify-between gap-4">
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded whitespace-nowrap">
                                            질문 {currentQuestionIndex + 1} / {questions.length < MAX_QUESTIONS ? '?' : MAX_QUESTIONS}
                                        </span>
                                        <p className="text-gray-900 font-medium text-sm">
                                            {currentQuestion.text}
                                        </p>
                                    </div>
                                    <div className="flex-shrink-0">
                                        {!isAudioRecording ? (
                                            <button
                                                onClick={startAudioRecording}
                                                disabled={isSubmittingAnswer}
                                                className="px-4 py-2 bg-primary text-white hover:bg-brand-purple transition-colors flex items-center gap-2 shadow-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                                style={{ borderRadius: '0.375rem' }}
                                            >
                                                <Mic className="w-4 h-4" />
                                                <span>{isSubmittingAnswer ? '제출 중...' : '녹음 시작'}</span>
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
                            </div>
                        )}

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

                            {/* User Camera - Horizontal Card with layoutId */}
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
                                <button className="w-14 h-14 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white">
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

                {/* Floating Progress Popup - Bottom Right */}
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
                                <span className="font-semibold">{currentQuestionIndex + 1} / {questions.length < MAX_QUESTIONS ? '?' : MAX_QUESTIONS}</span>
                            </div>
                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary rounded-full transition-all"
                                    style={{ width: `${((currentQuestionIndex + 1) / MAX_QUESTIONS) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div >
    );
}
