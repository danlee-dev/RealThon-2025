'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, TrendingUp, BookOpen } from 'lucide-react';
import { AnalysisResults } from '../../types';

interface AnalyzingScreenProps {
    onComplete: (results: AnalysisResults) => void;
}

export default function AnalyzingScreen({ onComplete }: AnalyzingScreenProps) {
    useEffect(() => {
        // 3초 후 자동 전환
        const timer = setTimeout(() => {
            const mockResults: AnalysisResults = {
                capabilities: [
                    { skill: 'Professionalism', value: 75 },
                    { skill: 'Attitude', value: 80 },
                    { skill: 'Creativity', value: 70 },
                    { skill: 'Communication', value: 85 },
                    { skill: 'Leadership', value: 65 },
                    { skill: 'Teamwork', value: 75 },
                    { skill: 'Sociability', value: 80 },
                ],
                suggestions: [],
                videoScore: 80,
                workmapScore: 75,
            };
            onComplete(mockResults);
        }, 3000);

        return () => clearTimeout(timer);
    }, [onComplete]);

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
        >
            <div className="flex-[2] flex flex-col gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
                    {/* Removed layoutId to disable 3->4 transition */}
                    <motion.div
                        layoutId="main-interview-area"
                        className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video"
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
                                <div className="mb-6">
                                    <div className="w-20 h-20 mx-auto bg-white/20 rounded-full flex items-center justify-center mb-4">
                                        <Lightbulb className="w-10 h-10 animate-pulse" />
                                    </div>
                                </div>
                                <h3 className="text-2xl font-bold mb-2">AI가 면접을 분석하고 있습니다</h3>
                                <p className="text-white/80 mb-8">직무 역량 강화를 위한 맞춤형 피드백을 준비 중입니다...</p>
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
