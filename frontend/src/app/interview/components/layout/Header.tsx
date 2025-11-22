'use client';

import { Bell, ChevronLeft } from 'lucide-react';
import { InterviewStage } from '../../types';

interface HeaderProps {
    stage: InterviewStage;
}

export default function Header({ stage }: HeaderProps) {
    const getStageTitle = () => {
        switch (stage) {
            case InterviewStage.WAITING:
                return '면접 준비';
            case InterviewStage.INTERVIEWING:
                return 'Interview for UI/UX Designer';
            case InterviewStage.ANALYZING:
                return '면접 분석 중...';
            case InterviewStage.COMPLETE:
                return '면접 분석 완료';
            default:
                return 'Interview';
        }
    };

    const getStageSubtitle = () => {
        switch (stage) {
            case InterviewStage.WAITING:
                return '면접을 시작하기 전에 카메라와 마이크를 확인해주세요';
            case InterviewStage.INTERVIEWING:
                return 'Sans Brother';
            case InterviewStage.ANALYZING:
                return 'AI가 면접 내용을 분석하고 있습니다';
            case InterviewStage.COMPLETE:
                return '면접 결과를 확인하세요';
            default:
                return '';
        }
    };

    return (
        <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
                {stage !== InterviewStage.WAITING && (
                    <button className="p-2 hover:bg-gray-100 rounded-full">
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                )}
                <div>
                    <h1 className="text-lg font-semibold text-gray-900">{getStageTitle()}</h1>
                    <p className="text-sm text-gray-500">{getStageSubtitle()}</p>
                </div>
            </div>
            <div className="flex items-center gap-4">
                <button className="p-2 hover:bg-gray-100 rounded-full relative">
                    <Bell className="w-5 h-5 text-gray-600" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-200">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        ZM
                    </div>
                    <span className="text-sm font-medium">Zaim Maulana</span>
                </button>
            </div>
        </div>
    );
}
