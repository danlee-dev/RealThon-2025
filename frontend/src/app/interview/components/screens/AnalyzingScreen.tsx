'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, TrendingUp, BookOpen, AlertCircle, RefreshCw } from 'lucide-react';
import { AnalysisResults } from '../../types';
import { videoApi } from '@/lib/auth-client';

interface AnalyzingScreenProps {
    onComplete: (results: AnalysisResults) => void;
    videoId?: string;
    sessionId?: string;
}

export default function AnalyzingScreen({ onComplete, videoId, sessionId }: AnalyzingScreenProps) {
    const [status, setStatus] = useState<string>('initializing'); // initializing, analyzing, polling, completed, error
    const [error, setError] = useState<string | null>(null);
    const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        const startAnalysis = async () => {
            if (!videoId) {
                console.error('No video ID provided for analysis');
                setError('비디오 ID가 없습니다. 분석을 시작할 수 없습니다.');
                setStatus('error');
                return;
            }

            try {
                setStatus('analyzing');
                console.log(`[AnalyzingScreen] Starting analysis for video ${videoId}`);

                // 1. Trigger analysis
                const analyzeResponse = await videoApi.analyzeVideo(videoId);

                if (!analyzeResponse.success) {
                    throw new Error(analyzeResponse.error || '분석 요청 실패');
                }

                console.log('[AnalyzingScreen] Analysis triggered successfully');
                setStatus('polling');

                // 2. Poll for results
                pollResults(videoId);

            } catch (err) {
                console.error('[AnalyzingScreen] Analysis error:', err);
                setError(err instanceof Error ? err.message : '분석 중 오류가 발생했습니다.');
                setStatus('error');
            }
        };

        startAnalysis();

        return () => {
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
            }
        };
    }, [videoId]);

    const pollResults = (vid: string) => {
        let attempts = 0;
        const maxAttempts = 60; // 2 minutes max (2s interval)

        pollingIntervalRef.current = setInterval(async () => {
            attempts++;
            try {
                console.log(`[AnalyzingScreen] Polling results (attempt ${attempts})`);
                const response = await videoApi.getResults(vid);

                if (response.success && response.data) {
                    const result = response.data;

                    if (result.status === 'completed') {
                        console.log('[AnalyzingScreen] Analysis completed:', result);
                        if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
                        setStatus('completed');

                        // Transform API result to AnalysisResults format
                        // Assuming the API returns data matching or similar to AnalysisResults
                        // We might need to map it if the structure is different
                        const analysisResults: AnalysisResults = {
                            capabilities: result.capabilities || [],
                            suggestions: result.suggestions || [],
                            videoScore: result.metrics?.confidence_score || 0, // Example mapping
                            workmapScore: result.metrics?.fluency_score || 0, // Example mapping
                        };

                        // Add a small delay for better UX
                        setTimeout(() => {
                            onComplete(analysisResults);
                        }, 1000);
                    } else if (result.status === 'failed') {
                        throw new Error(result.error || '분석 실패');
                    }
                    // If processing or pending, continue polling
                }
            } catch (err) {
                console.error('[AnalyzingScreen] Polling error:', err);
                // Don't stop polling immediately on network error, but maybe track consecutive errors
            }

            if (attempts >= maxAttempts) {
                if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
                setError('분석 시간이 초과되었습니다.');
                setStatus('error');
            }
        }, 2000);
    };

    const handleRetry = () => {
        setError(null);
        setStatus('initializing');
        // Re-trigger effect by forcing a re-mount or just calling the logic again?
        // Since useEffect depends on videoId which doesn't change, we need to manually trigger.
        // But simpler is to just reload page or ask user to go back.
        // For now, let's just try to restart the polling if videoId exists.
        if (videoId) {
            // We can just call pollResults directly if we assume analysis was triggered
            // Or better, re-trigger the whole flow?
            // Let's just reload the component logic by toggling a key or something?
            // Actually, calling startAnalysis again is best but it's inside useEffect.
            // Let's just refresh the page for now as a fallback or provide a simple retry button that calls a function.
            window.location.reload();
        }
    };

    const improvementCards = [
        {
            icon: Lightbulb,
            title: '리더십 역량 강화',
            description: '팀을 이끄는 경험을 쌓고 의사결정 능력을 향상시키세요',
            color: 'from-purple-500 to-purple-600'
        },
        {
            icon: TrendingUp,
            title: '창의성 개발',
            description: '새로운 관점에서 문제를 바라보는 연습을 해보세요',
            color: 'from-blue-500 to-blue-600'
        },
        {
            icon: BookOpen,
            title: '전문성 향상',
            description: '관련 분야의 최신 트렌드와 기술을 학습하세요',
            color: 'from-green-500 to-green-600'
        }
    ];

    return (
        <motion.div
            className="flex-1 flex gap-6 p-6 overflow-auto"
            style={{ backgroundColor: 'rgb(250, 250, 248)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
        >
            <div className="flex-[2] flex flex-col gap-6 min-h-0">
                <div className="bg-white rounded-3xl p-6 shadow-sm flex-1 min-h-0" style={{ border: '1px solid #E5E5EC' }}>
                    {/* Removed layoutId to disable 3->4 transition */}
                    <motion.div
                        layoutId="main-interview-area"
                        className="relative bg-gray-900 rounded-2xl overflow-hidden h-full"
                    >
                        <img
                            src="/avatar.png"
                            alt="Interview Avatar"
                            className="absolute inset-0 w-full h-full object-cover opacity-30"
                        />

                        {/* Analysis Overlay */}
                        <motion.div
                            className="absolute inset-0 bg-gradient-to-b from-primary/90 to-brand-purple/90 backdrop-blur-sm flex items-center justify-center"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3, duration: 0.5 }}
                        >
                            <div className="text-center text-white max-w-2xl px-6">
                                {status === 'error' ? (
                                    <div className="mb-6">
                                        <div className="w-20 h-20 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-4">
                                            <AlertCircle className="w-10 h-10 text-red-200" />
                                        </div>
                                        <h3 className="text-2xl font-bold mb-2">분석 중 오류가 발생했습니다</h3>
                                        <p className="text-white/80 mb-8">{error}</p>
                                        <button
                                            onClick={handleRetry}
                                            className="px-6 py-2 bg-white text-primary rounded-full font-semibold hover:bg-gray-100 transition-colors flex items-center gap-2 mx-auto"
                                        >
                                            <RefreshCw className="w-4 h-4" />
                                            다시 시도
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <div className="mb-6">
                                            <div className="w-20 h-20 mx-auto bg-white/20 rounded-full flex items-center justify-center mb-4">
                                                <Lightbulb className="w-10 h-10 animate-pulse" />
                                            </div>
                                        </div>
                                        <h3 className="text-2xl font-bold mb-2">AI가 면접을 분석하고 있습니다</h3>
                                        <p className="text-white/80 mb-8">
                                            {status === 'initializing' && '분석을 준비하고 있습니다...'}
                                            {status === 'analyzing' && '영상을 분석 서버로 전송 중입니다...'}
                                            {status === 'polling' && 'AI가 답변 내용을 분석하고 피드백을 생성 중입니다...'}
                                            {status === 'completed' && '분석이 완료되었습니다!'}
                                        </p>
                                    </>
                                )}
                            </div>
                        </motion.div>
                    </motion.div>
                </div>

                {/* Improvement Cards */}
                <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">직무 역량 강화를 위한 정보</h3>
                    <div className="grid grid-cols-3 gap-4">
                        {improvementCards.map((card, index) => (
                            <div
                                key={index}
                                className="p-4 rounded-xl bg-gradient-to-br ${card.color} text-white transform hover:scale-105 transition-transform"
                                style={{
                                    background: `linear-gradient(135deg, ${index === 0 ? '#9333ea, #7c3aed' :
                                        index === 1 ? '#3b82f6, #2563eb' :
                                            '#10b981, #059669'
                                        })`
                                }}
                            >
                                <card.icon className="w-8 h-8 mb-3" />
                                <h4 className="font-semibold mb-1 text-sm">{card.title}</h4>
                                <p className="text-xs text-white/90">{card.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
