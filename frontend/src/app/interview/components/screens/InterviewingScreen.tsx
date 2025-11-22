'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, Volume2, PhoneOff, Video, Settings } from 'lucide-react';

interface InterviewingScreenProps {
    onEnd: () => void;
}

export default function InterviewingScreen({ onEnd }: InterviewingScreenProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioRecorderRef = useRef<MediaRecorder | null>(null);
    const [volume, setVolume] = useState(75);
    const [isRecording, setIsRecording] = useState(false);
    const [isAudioRecording, setIsAudioRecording] = useState(false);
    const [questions, setQuestions] = useState<string[]>([
        '자기소개를 해주세요.',
        '이 회사에 지원한 동기는 무엇인가요?',
        '본인의 강점과 약점을 말씀해주세요.',
        '5년 후 자신의 모습은 어떨 것 같나요?'
    ]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [audioRecordings, setAudioRecordings] = useState<Blob[][]>([]);

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

        audioRecorder.onstop = () => {
            setAudioRecordings(prev => {
                const newRecordings = [...prev];
                newRecordings[currentQuestionIndex] = chunks;
                return newRecordings;
            });

            console.log(`[DEBUG] Question ${currentQuestionIndex + 1} audio saved`);
        };

        audioRecorderRef.current = audioRecorder;
        audioRecorder.start();
        setIsAudioRecording(true);
        console.log(`[DEBUG] Recording answer for question ${currentQuestionIndex + 1}`);
    };

    const stopAudioRecording = () => {
        if (audioRecorderRef.current && isAudioRecording) {
            audioRecorderRef.current.stop();
            setIsAudioRecording(false);

            // 마지막 질문이면 면접 종료
            if (currentQuestionIndex === questions.length - 1) {
                console.log('[DEBUG] Last question completed, ending interview');
                onEnd();
            } else {
                setCurrentQuestionIndex(prev => prev + 1);
            }
        }
    };

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 flex gap-6 p-6 overflow-auto" style={{ backgroundColor: 'rgb(250, 250, 248)' }}>
                {/* Left Column - Video */}
                <div className="flex-[2] flex flex-col gap-6">
                    <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="text-sm text-gray-600">Digital Interview has Live</span>
                            </div>
                            <div className="flex items-center gap-3">
                                {isRecording && (
                                    <div className="flex items-center gap-2 px-3 py-1 bg-red-100 rounded-full">
                                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                                        <span className="text-sm text-red-600 font-medium">녹화 중</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                                    <span className="text-sm text-primary">Also joined in this call</span>
                                </div>
                            </div>
                        </div>

                        {/* Question and Recording Controls */}
                        {questions.length > 0 && (
                            <div className="mb-4 p-4 bg-gradient-to-r from-primary/10 to-brand-purple-light/10 rounded-xl border-l-4 border-primary">
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                                                질문 {currentQuestionIndex + 1} / {questions.length}
                                            </span>
                                        </div>
                                        <p className="text-gray-900 font-medium text-lg">
                                            {questions[currentQuestionIndex]}
                                        </p>
                                    </div>
                                    <div className="ml-4">
                                        {!isAudioRecording ? (
                                            <button
                                                onClick={startAudioRecording}
                                                className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-brand-purple transition-colors flex items-center gap-2 shadow-lg"
                                            >
                                                <Mic className="w-5 h-5" />
                                                <span>답변 녹음 시작</span>
                                            </button>
                                        ) : (
                                            <button
                                                onClick={stopAudioRecording}
                                                className="px-6 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors flex items-center gap-2 shadow-lg animate-pulse"
                                            >
                                                <div className="w-3 h-3 bg-white rounded-full"></div>
                                                <span>녹음 중지</span>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Video Area */}
                        <div className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video">
                            {/* Main Video - Avatar Background */}
                            <img
                                src="/avatar.png"
                                alt="Interview Avatar"
                                className="absolute inset-0 w-full h-full object-cover"
                            />

                            {/* User Camera - Horizontal Card */}
                            <div className="absolute top-4 right-4 w-64 h-36 bg-gray-800 rounded-xl overflow-hidden shadow-lg border-2 border-gray-700">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className="w-full h-full object-cover"
                                />
                            </div>

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
                        </div>

                        {/* Caption */}
                        <div className="mt-4 flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
                            <div className="flex gap-0.5 mt-1">
                                {[...Array(5)].map((_, i) => (
                                    <div key={i} className="w-1 h-4 bg-primary rounded-full animate-pulse" style={{ animationDelay: `${i * 0.1}s` }}></div>
                                ))}
                            </div>
                            <p className="text-sm text-gray-700">
                                <span className="font-medium">Conversation now:</span> {questions[currentQuestionIndex]}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Right Column - Info */}
                <div className="flex-[1] flex flex-col gap-6">
                    <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                        <h3 className="font-semibold text-gray-900 mb-4">면접 진행 상황</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">현재 질문</span>
                                <span className="font-semibold">{currentQuestionIndex + 1} / {questions.length}</span>
                            </div>
                            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary rounded-full transition-all"
                                    style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
