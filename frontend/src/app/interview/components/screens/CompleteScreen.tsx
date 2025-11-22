'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';
import {
    Mic,
    Volume2,
    PhoneOff,
    Video,
    Settings,
    HelpCircle,
    Paperclip,
    Smile
} from 'lucide-react';
import { ResponsiveRadar } from '@nivo/radar';
import { ResponsivePie } from '@nivo/pie';
import { AnalysisResults } from '../../types';

interface CompleteScreenProps {
    analysisResults: AnalysisResults;
}

export default function CompleteScreen({ analysisResults }: CompleteScreenProps) {
    return (
        <motion.div
            className="flex-1 flex gap-6 p-6 overflow-auto"
            style={{ backgroundColor: 'rgb(250, 250, 248)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
        >
            {/* Left Column - Video & Charts */}
            <motion.div
                className="flex-[2] flex flex-col gap-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.4 }}
            >
                {/* Video Section */}
                <VideoSection />

                {/* Charts Section */}
                <motion.div
                    className="grid grid-cols-2 gap-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4, duration: 0.4 }}
                >
                    <AIVideoScoreChart data={analysisResults.capabilities} />
                    <WorkmapScoreChart />
                </motion.div>
            </motion.div>

            {/* Right Column - Scores & Chat */}
            <motion.div
                className="flex-[1] flex flex-col gap-6"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
            >
                <ScoreCards
                    videoScore={analysisResults.videoScore}
                    workmapScore={analysisResults.workmapScore}
                />
                <ChatSection />
            </motion.div>
        </motion.div>
    );
}

function VideoSection() {
    const videoRef = useRef<HTMLVideoElement>(null);

    return (
        <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
            {/* Video Area */}
            <div className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video">
                {/* Main Video - Avatar Background */}
                <img
                    src="/avatar.png"
                    alt="Interview Avatar"
                    className="absolute inset-0 w-full h-full object-cover"
                />

                {/* Volume Slider */}
                <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-3">
                    <div className="bg-gray-800/80 backdrop-blur-sm rounded-full p-3 shadow-lg">
                        <Volume2 className="w-5 h-5 text-white" />
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
        </div>
    );
}

function AIVideoScoreChart({ data }: { data: { skill: string; value: number }[] }) {
    return (
        <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">AI Video Score</h3>
                <HelpCircle className="w-5 h-5 text-gray-400" />
            </div>
            <p className="text-xs text-gray-500 mb-6">Based on Accurate Value from Video</p>
            <div className="h-64">
                <ResponsiveRadar
                    data={data}
                    keys={['value']}
                    indexBy="skill"
                    maxValue={100}
                    margin={{ top: 40, right: 60, bottom: 40, left: 60 }}
                    borderColor={{ from: 'color' }}
                    gridLabelOffset={16}
                    dotSize={8}
                    dotColor={{ theme: 'background' }}
                    dotBorderWidth={2}
                    colors={['#7c3aed']}
                    fillOpacity={0.25}
                    blendMode="multiply"
                    animate={true}
                    motionConfig="gentle"
                />
            </div>
        </div>
    );
}

function WorkmapScoreChart() {
    const scores = [
        { label: 'Presentation', value: 90, color: '#7c3aed' },
        { label: 'Opportunistic', value: 60, color: '#dc2626' },
        { label: 'Business Acumen', value: 85, color: '#7c3aed' },
        { label: 'Closing Technique', value: 40, color: '#dc2626' },
    ];

    return (
        <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Workmap Score</h3>
                <HelpCircle className="w-5 h-5 text-gray-400" />
            </div>
            <p className="text-xs text-gray-500 mb-6">Based on Accurate Value from Video</p>
            <div className="space-y-4">
                {scores.map((score) => (
                    <div key={score.label}>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-700">{score.label}</span>
                            <span className="font-semibold">{score.value}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full transition-all"
                                style={{
                                    width: `${score.value}%`,
                                    backgroundColor: score.color
                                }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function ScoreCards({ videoScore, workmapScore }: { videoScore: number; workmapScore: number }) {
    return (
        <div className="bg-white rounded-2xl p-3 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">스코어</h3>
            <div className="grid grid-cols-2 gap-3">
                <ScoreCard
                    title="AI Video Score"
                    score={videoScore}
                    color="#7c3aed"
                />
                <ScoreCard
                    title="Workmap Score"
                    score={workmapScore}
                    color="#ea580c"
                />
            </div>
        </div>
    );
}

function ScoreCard({ title, score, color }: { title: string; score: number; color: string }) {
    const data = [
        { id: 'score', value: score },
        { id: 'remaining', value: 100 - score },
    ];

    return (
        <div className="bg-gray-50 rounded-lg p-3 flex flex-col items-center">
            <div className="h-16 w-16 relative">
                <ResponsivePie
                    data={data}
                    margin={{ top: 2, right: 2, bottom: 2, left: 2 }}
                    innerRadius={0.75}
                    padAngle={0}
                    cornerRadius={0}
                    colors={[color, '#F0F0F0']}
                    enableArcLinkLabels={false}
                    enableArcLabels={false}
                    isInteractive={false}
                />
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-xs font-bold" style={{ color }}>{score}%</div>
                    </div>
                </div>
            </div>
            <p className="text-xs text-gray-700 text-center mt-1.5">{title}</p>
        </div>
    );
}

function ChatSection() {
    const messages = [
        {
            id: 1,
            sender: 'Richard Gomez',
            avatar: 'RG',
            message: 'Hello everyone, Good Morning :)',
            time: '08:42 AM',
            isMe: false,
        },
        {
            id: 2,
            sender: 'You',
            message: 'Hi Richard, Goodmorning too. Let\'s start this interview yourself!',
            time: '08:43 AM',
            isMe: true,
        },
        {
            id: 3,
            type: 'system',
            message: 'We announce that you accepted this call',
        },
        {
            id: 4,
            sender: 'Richard Gomez',
            avatar: 'RG',
            message: 'Why you choose this company?',
            time: '08:45 AM',
            isMe: false,
        },
    ];

    return (
        <div className="bg-white rounded-3xl shadow-sm flex-1 flex flex-col overflow-hidden" style={{ border: '1px solid #E5E5EC' }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((msg: any) => {
                    if (msg.type === 'system') {
                        return (
                            <div key={msg.id} className="flex justify-center">
                                <p className="text-xs text-gray-500 bg-gray-100 px-4 py-2 rounded-full">
                                    {msg.message}
                                </p>
                            </div>
                        );
                    }

                    return (
                        <div key={msg.id} className={`flex gap-3 ${msg.isMe ? 'flex-row-reverse' : ''}`}>
                            {!msg.isMe && (
                                <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold flex-shrink-0">
                                    {msg.avatar}
                                </div>
                            )}
                            <div className={`flex-1 ${msg.isMe ? 'flex flex-col items-end' : ''}`}>
                                {!msg.isMe && (
                                    <p className="text-sm font-medium text-gray-900 mb-1">{msg.sender}</p>
                                )}
                                <div className={`inline-block px-4 py-2 rounded-2xl ${msg.isMe
                                    ? 'bg-blue-900 text-white rounded-tr-none'
                                    : 'bg-gray-100 text-gray-900 rounded-tl-none'
                                    }`}>
                                    <p className="text-sm">{msg.message}</p>
                                </div>
                                <p className="text-xs text-gray-400 mt-1">{msg.time}</p>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-100">
                <div className="flex items-center gap-3 bg-gray-50 rounded-full px-4 py-3">
                    <button className="text-gray-400 hover:text-gray-600">
                        <Paperclip className="w-5 h-5" />
                    </button>
                    <input
                        type="text"
                        placeholder="Type a message..."
                        className="flex-1 bg-transparent outline-none text-sm"
                    />
                    <button className="text-gray-400 hover:text-gray-600">
                        <Smile className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
