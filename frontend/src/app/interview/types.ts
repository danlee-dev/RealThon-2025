export enum InterviewStage {
    WAITING = 'waiting',
    INTERVIEWING = 'interviewing',
    ANALYZING = 'analyzing',
    COMPLETE = 'complete'
}

export interface Capability {
    skill: string;
    value: number;
}

export interface ImprovementSuggestion {
    id: string;
    capability: string;
    currentScore: number;
    title: string;
    description: string;
    actionItems: string[];
}

export interface AnalysisResults {
    capabilities: Capability[];
    suggestions: ImprovementSuggestion[];
    videoScore: number;
    workmapScore: number;
}
