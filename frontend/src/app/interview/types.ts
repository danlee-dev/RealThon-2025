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

export interface VideoMetadata {
    id: string;
    user_id: string;
    session_id: string;
    question_id: string;
    duration_sec: number;
    created_at: string;
}

export interface AnalysisMetrics {
    center_gaze_ratio: number;
    smile_ratio: number;
    nod_count: number;
    nod_rate_per_min: number;
    wpm: number;
    filler_count: number;
    primary_emotion: string;
    emotion_distribution: Record<string, number>;
    metadata?: any;
}

export interface AnalysisFeedback {
    id: string;
    title: string;
    message: string;
    severity: 'info' | 'warning' | 'suggestion';
    level: 'video' | 'segment';
}

export interface AnalysisAlert {
    start_t: number;
    end_t: number;
    severity: number;
    message: string;
}

export interface TimelineFrame {
    t: number;
    valid: boolean;
    gaze: string;
    smile: number;
    emotion: string;
    pitch: number;
    yaw: number;
    roll: number;
}

export interface DetailedAnalysisResult {
    video: VideoMetadata;
    metrics: AnalysisMetrics;
    feedbacks: AnalysisFeedback[];
    alerts: AnalysisAlert[];
    transcript: string;
    timeline: TimelineFrame[];
    timeline_available: boolean;
}

export interface AnalysisResults {
    capabilities: Capability[];
    suggestions: ImprovementSuggestion[];
    videoScore: number;
    workmapScore: number;
    detailedResult?: DetailedAnalysisResult;
}
