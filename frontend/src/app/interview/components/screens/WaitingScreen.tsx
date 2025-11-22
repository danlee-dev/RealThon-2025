'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Mic, Video, Play } from 'lucide-react';

interface WaitingScreenProps {
    onStart: () => void;
    isLoading?: boolean;
}

export default function WaitingScreen({ onStart, isLoading = false }: WaitingScreenProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [cameraReady, setCameraReady] = useState(false);
    const [micReady, setMicReady] = useState(false);

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
                setCameraReady(true);
                setMicReady(true);
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

    const handleStartClick = () => {
        console.log('[WaitingScreen] 면접 시작 버튼 클릭됨');
        onStart();
    };

    return (
        <motion.div
            className="flex-1 flex items-center justify-center p-4 overflow-auto"
            style={{ backgroundColor: 'rgb(250, 250, 248)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
        >
            <div className="max-w-3xl w-full my-auto">
                <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                    {/* Title */}
                    <div className="text-center mb-4">
                        <h2 className="text-2xl font-bold text-gray-900 mb-1">면접 준비</h2>
                        <p className="text-sm text-gray-600">카메라와 마이크를 확인한 후 면접을 시작하세요</p>
                    </div>

                    {/* Camera Preview with layoutId */}
                    <motion.div
                        layoutId="user-camera"
                        className="relative bg-gray-900 rounded-2xl overflow-hidden mb-4"
                        style={{ aspectRatio: '16/9' }}
                        transition={{ type: "spring", stiffness: 120, damping: 30 }}
                    >
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full h-full object-cover"
                        />
                        <div className="absolute bottom-3 left-3 right-3 flex justify-center gap-3">
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${cameraReady ? 'bg-green-500/80' : 'bg-gray-500/80'} backdrop-blur-sm`}>
                                <Video className="w-4 h-4 text-white" />
                                <span className="text-white text-xs font-medium">
                                    {cameraReady ? '카메라 준비됨' : '카메라 확인 중...'}
                                </span>
                            </div>
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${micReady ? 'bg-green-500/80' : 'bg-gray-500/80'} backdrop-blur-sm`}>
                                <Mic className="w-4 h-4 text-white" />
                                <span className="text-white text-xs font-medium">
                                    {micReady ? '마이크 준비됨' : '마이크 확인 중...'}
                                </span>
                            </div>
                        </div>
                    </motion.div>

                    {/* Interview Info */}
                    <div className="grid grid-cols-3 gap-3 mb-4">
                        <div className="bg-gray-50 rounded-xl p-3 text-center">
                            <p className="text-xs text-gray-600 mb-0.5">면접 시간</p>
                            <p className="text-base font-semibold text-gray-900">약 15분</p>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-3 text-center">
                            <p className="text-xs text-gray-600 mb-0.5">질문 개수</p>
                            <p className="text-base font-semibold text-gray-900">4개</p>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-3 text-center">
                            <p className="text-xs text-gray-600 mb-0.5">평가 방식</p>
                            <p className="text-base font-semibold text-gray-900">AI 분석</p>
                        </div>
                    </div>

                    {/* Start Button */}
                    <button
                        onClick={handleStartClick}
                        disabled={!cameraReady || !micReady || isLoading}
                        type="button"
                        className="w-full py-3 bg-primary hover:bg-brand-purple text-white rounded-xl font-semibold text-base flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                질문 로드 중...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5" />
                                면접 시작하기
                            </>
                        )}
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
