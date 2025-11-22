'use client';

import { useState, useEffect } from 'react';
import {
    Bell,
    TrendingUp,
    Target,
    CheckCircle2
} from 'lucide-react';
import { ResponsiveRadar } from '@nivo/radar';
import Sidebar from '../interview/components/layout/Sidebar';
import { capabilityApi } from '@/lib/auth-client';
import { Capability, ImprovementSuggestion } from '@/types';

export default function GraphPage() {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const [capabilities, setCapabilities] = useState<Capability[]>([]);
    const [suggestions, setSuggestions] = useState<ImprovementSuggestion[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [capabilitiesRes, suggestionsRes] = await Promise.all([
                    capabilityApi.getCapabilities(),
                    capabilityApi.getImprovementSuggestions()
                ]);

                if (capabilitiesRes.success && capabilitiesRes.data) {
                    setCapabilities(capabilitiesRes.data);
                }

                if (suggestionsRes.success && suggestionsRes.data) {
                    setSuggestions(suggestionsRes.data);
                }
            } catch (error) {
                console.error('Failed to fetch capability data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <div className="flex h-screen bg-sidebar">
            {/* Sidebar */}
            <Sidebar
                isCollapsed={isSidebarCollapsed}
                onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden bg-white relative z-10">
                {/* Header */}
                <Header />

                {/* Content Area */}
                <div className="flex-1 flex gap-6 p-6 overflow-auto bg-light-grey">
                    {/* Left Column - Radar Chart */}
                    <div className="flex-[2] flex flex-col gap-6">
                        <CapabilityRadarChart data={capabilities} loading={loading} />
                    </div>

                    {/* Right Column - Improvement Cards */}
                    <div className="flex-[1] flex flex-col gap-6">
                        <ImprovementSuggestionsSection suggestions={suggestions} loading={loading} />
                    </div>
                </div>
            </div>
        </div>
    );
}



function Header() {
    return (
        <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
                <div>
                    <h1 className="text-lg font-semibold text-gray-900">역량 분석 피드백</h1>
                    <p className="text-sm text-gray-500">AI가 분석한 나의 역량 평가 결과</p>
                </div>
            </div>
            <div className="flex items-center gap-4">
                <button className="p-2 hover:bg-gray-100 rounded-full relative">
                    <Bell className="w-5 h-5 text-gray-600" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-200">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        김철
                    </div>
                    <span className="text-sm font-medium">김철수</span>
                </button>
            </div>
        </div>
    );
}

function CapabilityRadarChart({ data, loading }: { data: Capability[], loading: boolean }) {
    if (loading) {
        return (
            <div className="bg-white rounded-3xl p-8 shadow-sm flex items-center justify-center h-[500px]">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-500">역량 데이터를 불러오는 중...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-3xl p-8 shadow-sm">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-xl font-semibold text-gray-900">나의 역량 평가</h3>
                    <p className="text-sm text-gray-500 mt-1">면접 및 포트폴리오 분석 기반</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    <span className="text-sm font-medium text-primary">AI 분석 완료</span>
                </div>
            </div>

            <div className="h-[400px]">
                <ResponsiveRadar
                    data={data}
                    keys={['value']}
                    indexBy="skill"
                    maxValue={100}
                    margin={{ top: 60, right: 80, bottom: 60, left: 80 }}
                    borderColor={{ from: 'color' }}
                    gridLabelOffset={20}
                    dotSize={10}
                    dotColor={{ theme: 'background' }}
                    dotBorderWidth={2}
                    colors={['#7C5CFC']}
                    fillOpacity={0.3}
                    blendMode="multiply"
                    animate={true}
                    motionConfig="gentle"
                    theme={{
                        text: {
                            fontSize: 12,
                            fill: '#333333',
                            fontWeight: 500
                        },
                        grid: {
                            line: {
                                stroke: '#e5e7eb',
                                strokeWidth: 1
                            }
                        }
                    }}
                />
            </div>

            {/* Legend */}
            <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
                {data.map((item) => (
                    <div key={item.skill} className="text-center">
                        <div className="text-2xl font-bold text-primary">{item.value}</div>
                        <div className="text-xs text-gray-600 mt-1">{item.skill}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function ImprovementSuggestionsSection({ suggestions, loading }: { suggestions: ImprovementSuggestion[], loading: boolean }) {
    if (loading) {
        return (
            <div className="bg-white rounded-3xl p-6 shadow-sm flex items-center justify-center h-[500px]">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-500">개선 방안을 불러오는 중...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-3xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                    <Target className="w-6 h-6 text-primary" />
                    <h3 className="text-lg font-semibold text-gray-900">역량 개선 방안</h3>
                </div>
                <p className="text-sm text-gray-600">
                    AI가 분석한 부족한 역량을 향상시키기 위한 맞춤형 개선 방안입니다.
                </p>
            </div>

            {suggestions.map((suggestion) => (
                <ImprovementCard key={suggestion.id} suggestion={suggestion} />
            ))}
        </div>
    );
}

function ImprovementCard({ suggestion }: { suggestion: ImprovementSuggestion }) {
    return (
        <div className="bg-white rounded-3xl p-6 shadow-sm border-2 border-gray-100 hover:border-primary/30 transition-colors">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="text-lg font-bold text-primary">{suggestion.currentScore}</span>
                    </div>
                    <div>
                        <h4 className="font-semibold text-gray-900">{suggestion.capability}</h4>
                        <p className="text-xs text-gray-500">현재 점수</p>
                    </div>
                </div>
            </div>

            {/* Title & Description */}
            <div className="mb-4 pb-4 border-b border-gray-100">
                <h5 className="font-semibold text-gray-900 mb-2">{suggestion.title}</h5>
                <p className="text-sm text-gray-600 leading-relaxed">{suggestion.description}</p>
            </div>

            {/* Action Items */}
            <div>
                <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium text-gray-700">실천 방안</span>
                </div>
                <ul className="space-y-2">
                    {suggestion.actionItems.map((item, index) => (
                        <li key={index} className="flex items-start gap-3 text-sm text-gray-600">
                            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center mt-0.5 font-medium">
                                {index + 1}
                            </span>
                            <span className="flex-1">{item}</span>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
