// User types
export interface User {
  id: string;
  email: string;
  name: string;
  jobTitle?: string;
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
