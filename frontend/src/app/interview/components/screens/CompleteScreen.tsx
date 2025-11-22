'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactPlayer from 'react-player';
import {
    Mic,
    Volume2,
    PhoneOff,
    Video,
    Settings,
    HelpCircle,
    Paperclip,
    Smile,
    Play,
    Pause
} from 'lucide-react';
import { ResponsiveRadar } from '@nivo/radar';
import { ResponsivePie } from '@nivo/pie';
import { AnalysisResults } from '../../types';
import { getVideoFromIndexedDB } from '@/lib/indexedDB';

interface CompleteScreenProps {
    analysisResults: AnalysisResults;
}

interface TimestampRange {
    start: number;
    end: number;
}

export default function CompleteScreen({ analysisResults }: CompleteScreenProps) {
    const playerRef = useRef<ReactPlayer>(null);
    const [activeTimestamp, setActiveTimestamp] = useState<TimestampRange | null>(null);

    const handleTimestampClick = (timestamp: TimestampRange) => {
        setActiveTimestamp(timestamp);
        if (playerRef.current) {
            playerRef.current.seekTo(timestamp.start, 'seconds');
        }
    };

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
                <VideoSection playerRef={playerRef} activeTimestamp={activeTimestamp} />

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
                <ChatSection onTimestampClick={handleTimestampClick} />
            </motion.div>
        </motion.div>
    );
}

interface VideoSectionProps {
    playerRef: React.RefObject<ReactPlayer>;
    activeTimestamp: TimestampRange | null;
}

function VideoSection({ playerRef, activeTimestamp }: VideoSectionProps) {
    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [playing, setPlaying] = useState(false);
    const [volume, setVolume] = useState(0.75);
    const [muted, setMuted] = useState(false);
    const [played, setPlayed] = useState(0);
    const [duration, setDuration] = useState(0);
    const [seeking, setSeeking] = useState(false);
    const [showControls, setShowControls] = useState(true);
    const [isHoveringProgress, setIsHoveringProgress] = useState(false);
    const hideControlsTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        // Load video from IndexedDB
        const loadVideo = async () => {
            try {
                const blob = await getVideoFromIndexedDB();
                if (blob) {
                    const url = URL.createObjectURL(blob);
                    setVideoUrl(url);
                    console.log('[CompleteScreen] Video loaded from IndexedDB');
                } else {
                    console.log('[CompleteScreen] No video found in IndexedDB');
                }
            } catch (error) {
                console.error('[CompleteScreen] Error loading video:', error);
            }
        };

        loadVideo();

        // Cleanup
        return () => {
            if (videoUrl) {
                URL.revokeObjectURL(videoUrl);
            }
        };
    }, []);

    const handleMouseMove = () => {
        setShowControls(true);
        if (hideControlsTimeoutRef.current) {
            clearTimeout(hideControlsTimeoutRef.current);
        }
        hideControlsTimeoutRef.current = setTimeout(() => {
            if (playing) {
                setShowControls(false);
            }
        }, 3000);
    };

    const handleSeekChange = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const newPlayed = x / rect.width;
        setPlayed(newPlayed);
        if (playerRef.current) {
            playerRef.current.seekTo(newPlayed);
        }
    };

    const handleProgress = (state: { played: number; playedSeconds: number; loaded: number; loadedSeconds: number }) => {
        if (!seeking) {
            setPlayed(state.played);
        }
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Calculate timestamp range position on progress bar
    const getTimestampPosition = () => {
        if (!activeTimestamp || duration === 0) return null;
        return {
            left: `${(activeTimestamp.start / duration) * 100}%`,
            width: `${((activeTimestamp.end - activeTimestamp.start) / duration) * 100}%`,
        };
    };

    const toggleMute = () => {
        setMuted(!muted);
    };


    return (
        <div className="bg-white rounded-3xl p-6 shadow-sm" style={{ border: '1px solid #E5E5EC' }}>
            {/* Video Area */}
            <div
                className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video group"
                onMouseMove={handleMouseMove}
                onMouseLeave={() => playing && setShowControls(false)}
            >
                {videoUrl ? (
                    <ReactPlayer
                        ref={playerRef}
                        url={videoUrl}
                        playing={playing}
                        volume={muted ? 0 : volume}
                        width="100%"
                        height="100%"
                        onProgress={handleProgress}
                        onDuration={setDuration}
                        config={{
                            file: {
                                attributes: {
                                    style: { objectFit: 'cover' }
                                }
                            }
                        }}
                    />
                ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-white">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
                            <p className="text-sm font-medium">영상을 불러오는 중...</p>
                        </div>
                    </div>
                )}

                {/* Overlay gradient for better control visibility */}
                <div
                    className={`absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent pointer-events-none transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'
                        }`}
                />

                {/* Bottom Controls */}
                <motion.div
                    className="absolute bottom-0 left-0 right-0 p-6 z-20"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: showControls ? 1 : 0, y: showControls ? 0 : 20 }}
                    transition={{ duration: 0.3 }}
                >
                    <div className="flex items-center gap-4">
                        {/* Play/Pause */}
                        <button
                            onClick={() => setPlaying(!playing)}
                            className="w-11 h-11 bg-white/95 hover:bg-white backdrop-blur-md rounded-full flex items-center justify-center text-gray-900 shadow-lg hover:scale-105 active:scale-95 transition-all"
                        >
                            {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                        </button>

                        {/* Time Display */}
                        <div className="flex items-center gap-2 text-white font-semibold text-sm bg-black/50 backdrop-blur-sm px-4 py-2 rounded-full">
                            <span>{formatTime(played * duration)}</span>
                            <span className="text-white/50">/</span>
                            <span className="text-white/90">{formatTime(duration)}</span>
                        </div>

                        <div className="flex-1" />

                        {/* Volume Control */}
                        <button
                            onClick={toggleMute}
                            className="w-11 h-11 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-full flex items-center justify-center text-white shadow-lg hover:scale-105 active:scale-95 transition-all"
                        >
                            {muted || volume === 0 ? (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                                </svg>
                            ) : (
                                <Volume2 className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                </motion.div>
            </div>

            {/* Progress Bar - Enhanced */}
            <div className="mt-3 px-1">
                <div
                    className="relative h-2 bg-gray-200 rounded-full cursor-pointer overflow-visible group hover:h-2.5 transition-all"
                    onClick={handleSeekChange}
                    onMouseEnter={() => setIsHoveringProgress(true)}
                    onMouseLeave={() => setIsHoveringProgress(false)}
                >
                    {/* Active Timestamp Range Highlight */}
                    {activeTimestamp && getTimestampPosition() && (
                        <div
                            className="absolute top-0 h-full bg-amber-500/60 rounded-full z-10 border-2 border-amber-400"
                            style={getTimestampPosition()!}
                        />
                    )}

                    {/* Played Progress */}
                    <div
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-violet-600 to-purple-600 rounded-full transition-all z-20"
                        style={{ width: `${played * 100}%` }}
                    />

                    {/* Progress thumb */}
                    <div
                        className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-violet-600 transition-all z-30 ${isHoveringProgress ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
                            }`}
                        style={{ left: `calc(${played * 100}% - 8px)` }}
                    />
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
        <div className="bg-white rounded-lg p-3 flex flex-col items-center" style={{ border: '1px solid #E5E5EC' }}>
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

interface ChatSectionProps {
    onTimestampClick: (timestamp: TimestampRange) => void;
}

function ChatSection({ onTimestampClick }: ChatSectionProps) {
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
            message: 'Why you choose this company? Please refer to 00:15~00:32 in your answer.',
            time: '08:45 AM',
            isMe: false,
        },
        {
            id: 5,
            sender: 'You',
            message: 'I discussed my background at 00:45~01:12 and my motivation at 01:15~01:45.',
            time: '08:46 AM',
            isMe: true,
        },
    ];

    // Parse timestamps from message text
    const parseTimestamps = (text: string, onTimestampClick: (timestamp: TimestampRange) => void) => {
        // Regex to match timestamps in format MM:SS~MM:SS or HH:MM:SS~HH:MM:SS
        const timestampRegex = /(\d{1,2}:\d{2}(?::\d{2})?)~(\d{1,2}:\d{2}(?::\d{2})?)/g;

        const convertToSeconds = (timeStr: string): number => {
            const parts = timeStr.split(':').map(Number);
            if (parts.length === 2) {
                // MM:SS
                return parts[0] * 60 + parts[1];
            } else if (parts.length === 3) {
                // HH:MM:SS
                return parts[0] * 3600 + parts[1] * 60 + parts[2];
            }
            return 0;
        };

        const parts: (string | JSX.Element)[] = [];
        let lastIndex = 0;
        let match;
        let keyCounter = 0;

        while ((match = timestampRegex.exec(text)) !== null) {
            // Add text before the timestamp
            if (match.index > lastIndex) {
                parts.push(text.substring(lastIndex, match.index));
            }

            const startTime = convertToSeconds(match[1]);
            const endTime = convertToSeconds(match[2]);
            const timestampText = match[0];

            // Add clickable timestamp
            parts.push(
                <button
                    key={`timestamp-${keyCounter++}`}
                    onClick={() => onTimestampClick({ start: startTime, end: endTime })}
                    className="text-blue-600 hover:text-blue-800 hover:underline font-medium transition-colors"
                    style={{ cursor: 'pointer' }}
                >
                    {timestampText}
                </button>
            );

            lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < text.length) {
            parts.push(text.substring(lastIndex));
        }

        return parts.length > 0 ? parts : text;
    };

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
                                    <p className="text-sm">{parseTimestamps(msg.message, onTimestampClick)}</p>
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
