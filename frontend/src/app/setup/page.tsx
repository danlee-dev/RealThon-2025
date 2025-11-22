'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Mic, Video, Volume2, Play } from 'lucide-react';
import Sidebar from '../interview/components/layout/Sidebar';

export default function SetupPage() {
    const router = useRouter();
    const videoRef = useRef<HTMLVideoElement>(null);
    
    // State
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const [isSignLanguageMode, setIsSignLanguageMode] = useState(false);
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [cameraReady, setCameraReady] = useState(false);
    const [micReady, setMicReady] = useState(false);
    const [speakerReady, setSpeakerReady] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        startCamera();
        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    const startCamera = async () => {
        setIsLoading(true);
        setError('');
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: true
            });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
            setCameraReady(true);
            setMicReady(true);
        } catch (err) {
            console.error('Media access error:', err);
            setError('카메라 또는 마이크 접근에 실패했습니다. 권한을 확인해주세요.');
            setCameraReady(false);
        } finally {
            setIsLoading(false);
        }
    };

    const testSpeaker = () => {
        const audio = new Audio('/test-sound.mp3');
        audio.play().catch(() => {
            console.log('Speaker test sound played');
        });
        setSpeakerReady(true);
    };

    const handleStart = () => {
        if (cameraReady && micReady) {
            router.push('/interview');
        }
    };

    // We consider ready if camera and mic are ready. Speaker is optional but recommended.
    const isReady = cameraReady && micReady;

    return (
        <div className="flex h-screen bg-sidebar">
            {/* Sidebar - Active Item set to 'Setting' */}
            <Sidebar
                isCollapsed={isSidebarCollapsed}
                onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                isSignLanguageMode={isSignLanguageMode}
                onSignLanguageToggle={() => setIsSignLanguageMode(!isSignLanguageMode)}
                activeItem="Setting"
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden bg-white relative z-10">
                {/* Header */}
                <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center gap-4">
                    <h1 className="text-lg font-semibold text-gray-900">환경 설정</h1>
                </div>

                {/* Content Area - Mimicking WaitingScreen design */}
                <motion.div
                    className="flex-1 flex items-center justify-center p-4 overflow-auto"
                    style={{ backgroundColor: 'rgb(250, 250, 248)' }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.15 }}
                >
                    <div className="max-w-3xl w-full my-auto">
                        <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                            {/* Title */}
                            <div className="text-center mb-4">
                                <h2 className="text-2xl font-bold text-gray-900 mb-1">면접 환경 체크</h2>
                                <p className="text-sm text-gray-600">정확한 분석을 위해 카메라, 마이크, 스피커를 확인해주세요</p>
                            </div>

                            {/* Camera Preview */}
                            <motion.div
                                layoutId="user-camera"
                                className="relative bg-gray-900 rounded-2xl overflow-hidden mb-4"
                                style={{ aspectRatio: '16/9' }}
                            >
                                {stream ? (
                                    <video
                                        ref={videoRef}
                                        autoPlay
                                        playsInline
                                        muted
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                                        {isLoading ? '카메라 연결 중...' : '카메라를 찾을 수 없습니다'}
                                    </div>
                                )}
                                
                                {/* Status Badges */}
                                <div className="absolute bottom-3 left-3 right-3 flex justify-center gap-3 flex-wrap">
                                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${cameraReady ? 'bg-green-500/80' : 'bg-gray-500/80'} backdrop-blur-sm`}>
                                        <Video className="w-4 h-4 text-white" />
                                        <span className="text-white text-xs font-medium">
                                            {cameraReady ? '카메라 정상' : '카메라 확인 필요'}
                                        </span>
                                    </div>
                                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${micReady ? 'bg-green-500/80' : 'bg-gray-500/80'} backdrop-blur-sm`}>
                                        <Mic className="w-4 h-4 text-white" />
                                        <span className="text-white text-xs font-medium">
                                            {micReady ? '마이크 정상' : '마이크 확인 필요'}
                                        </span>
                                    </div>
                                    <button 
                                        onClick={testSpeaker}
                                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${speakerReady ? 'bg-green-500/80' : 'bg-gray-500/80'} backdrop-blur-sm hover:bg-opacity-90 transition-all`}
                                    >
                                        <Volume2 className="w-4 h-4 text-white" />
                                        <span className="text-white text-xs font-medium">
                                            {speakerReady ? '스피커 정상' : '스피커 테스트'}
                                        </span>
                                    </button>
                                </div>
                            </motion.div>

                            {/* Error Message */}
                            {error && (
                                <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-xl text-center font-medium">
                                    {error}
                                </div>
                            )}

                            {/* Info Grid / Tips */}
                            <div className="grid grid-cols-3 gap-3 mb-4">
                                <div className="bg-gray-50 rounded-xl p-3 text-center">
                                    <p className="text-xs text-gray-600 mb-0.5">조명</p>
                                    <p className="text-sm font-semibold text-gray-900">밝은 곳 권장</p>
                                </div>
                                <div className="bg-gray-50 rounded-xl p-3 text-center">
                                    <p className="text-xs text-gray-600 mb-0.5">소음</p>
                                    <p className="text-sm font-semibold text-gray-900">조용한 곳 권장</p>
                                </div>
                                <div className="bg-gray-50 rounded-xl p-3 text-center">
                                    <p className="text-xs text-gray-600 mb-0.5">화면</p>
                                    <p className="text-sm font-semibold text-gray-900">정면 응시</p>
                                </div>
                            </div>

                            {/* Start Button */}
                            <button
                                onClick={handleStart}
                                disabled={!isReady}
                                type="button"
                                className="w-full py-3 bg-primary hover:bg-brand-purple text-white rounded-xl font-semibold text-base flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Play className="w-5 h-5" />
                                설정 완료 및 면접 시작
                            </button>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}