// User types
export interface User {
  id: string;
  email: string;
  name: string;
  role?: string;
  level?: string;
  github_username?: string;
  jobTitle?: string; // Frontend convenience field (maps to role)
}

// Authentication tokens
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Portfolio (사용자의 포트폴리오/이력서)
export interface Portfolio {
  id: string;
  user_id: string;
  file_url: string;
  filename: string;
  parsed_text: string;
  summary: string;
}

// JobPosting (채용 공고 - 면접 대상)
export interface JobPosting {
  id: string;
  user_id: string;
  company_name: string;
  title: string;
  source_url: string;
  raw_text: string;
  parsed_skills: string;
  created_at: Date;
}

// Auth request/response types
export interface SignupRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// Capability types (for feedback page)
export interface Capability {
  skill: string;
  value: number;
  [key: string]: string | number;
}

export interface ImprovementSuggestion {
  id: string;
  capability: string;
  currentScore: number;
  title: string;
  description: string;
  actionItems: string[];
}

// Interview Session types
export interface InterviewSession {
  id: string;
  user_id: string;
  job_posting_id?: string;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
  completed_at?: string;
}

export interface InterviewQuestion {
  id: string;
  session_id: string;
  text: string;
  type: string;
  source: string;
  order: number;
  created_at: string;
  parent_question_id?: string;
}

// Video Analysis types
export interface VideoAnalysisResult {
  video_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  metrics?: {
    confidence_score: number;
    fluency_score: number;
    engagement_score: number;
  };
  feedback?: string;
  transcript?: string;
  capabilities?: Capability[];
}

// Answer submission types
export interface AnswerResponse {
  success: boolean;
  next_question?: InterviewQuestion;
  is_final?: boolean;
}
