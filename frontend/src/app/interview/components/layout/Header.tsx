'use client';

import { ChevronLeft } from 'lucide-react';
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

    return (
        <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center gap-4">
            {stage !== InterviewStage.WAITING && (
                <button className="p-2 hover:bg-gray-100 rounded-full flex-shrink-0">
                    <ChevronLeft className="w-5 h-5" />
                </button>
            )}
            <h1 className="text-lg font-semibold text-gray-900">{getStageTitle()}</h1>
        </div>
    );
}
