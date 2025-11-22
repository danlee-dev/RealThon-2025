import { ApiResponse, AuthResponse, User, Portfolio, InterviewSession, InterviewQuestion } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Token storage
export const TokenStorage = {
    setTokens: (tokens: { accessToken: string; refreshToken?: string }) => {
        if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', tokens.accessToken);
            if (tokens.refreshToken) {
                localStorage.setItem('refreshToken', tokens.refreshToken);
            }
        }
    },

    getAccessToken: (): string | null => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('accessToken');
        }
        return null;
    },

    clearTokens: () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        }
    },
};

// API client helper
async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
    try {
        const token = TokenStorage.getAccessToken();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string> || {}),
        };

        if (token && !headers['Authorization']) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return {
                success: false,
                error: errorData.detail || `Request failed with status ${response.status}`,
            };
        }

        // Handle 204 No Content responses
        if (response.status === 204) {
            return {
                success: true,
                data: undefined as any,
            };
        }

        const data = await response.json();
        return {
            success: true,
            data,
        };
    } catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Network error',
        };
    }
}

// Auth API
export const authApi = {
    signup: async (
        email: string,
        password: string,
        name?: string
    ): Promise<ApiResponse<AuthResponse>> => {
        // Step 1: Create user account
        const signupResponse = await apiCall<User>('/api/users/signup', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
                name: name || email.split('@')[0],
            }),
        });

        if (!signupResponse.success || !signupResponse.data) {
            return {
                success: false,
                error: signupResponse.error || 'Signup failed',
            };
        }

        // Step 2: Login to get access token
        const loginResponse = await apiCall<{ access_token: string; token_type: string }>(
            '/api/users/login',
            {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            }
        );

        if (!loginResponse.success || !loginResponse.data) {
            return {
                success: false,
                error: loginResponse.error || 'Failed to obtain access token',
            };
        }

        // Save tokens
        const tokens = {
            accessToken: loginResponse.data.access_token,
            refreshToken: '', // Backend doesn't provide refresh token yet
        };

        return {
            success: true,
            data: {
                user: signupResponse.data,
                tokens,
            },
        };
    },

    login: async (email: string, password: string): Promise<ApiResponse<AuthResponse>> => {
        // Step 1: Login to get access token
        const loginResponse = await apiCall<{ access_token: string; token_type: string }>(
            '/api/users/login',
            {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            }
        );

        if (!loginResponse.success || !loginResponse.data) {
            return {
                success: false,
                error: loginResponse.error || 'Login failed',
            };
        }

        // Temporarily save token to fetch user data
        const token = loginResponse.data.access_token;
        TokenStorage.setTokens({ accessToken: token });

        // Step 2: Get user profile
        const userResponse = await apiCall<User>('/api/users/me', {
            method: 'GET',
        });

        if (!userResponse.success || !userResponse.data) {
            TokenStorage.clearTokens();
            return {
                success: false,
                error: userResponse.error || 'Failed to fetch user data',
            };
        }

        const tokens = {
            accessToken: token,
            refreshToken: '', // Backend doesn't provide refresh token yet
        };

        return {
            success: true,
            data: {
                user: userResponse.data,
                tokens,
            },
        };
    },

    logout: () => {
        TokenStorage.clearTokens();
    },

    isAuthenticated: (): boolean => {
        return !!TokenStorage.getAccessToken();
    },
};

// Profile API
export const profileApi = {
    getProfile: async (): Promise<ApiResponse<User>> => {
        return apiCall<User>('/api/users/me', {
            method: 'GET',
        });
    },

    updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
        return apiCall<User>('/api/users/me', {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },
};

// Portfolio API
export const portfolioApi = {
    uploadPortfolio: async (file: File): Promise<ApiResponse<Portfolio>> => {
        try {
            const token = TokenStorage.getAccessToken();
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_URL}/api/portfolios/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                return {
                    success: false,
                    error: errorData.detail || 'Upload failed',
                };
            }

            const data = await response.json();
            return {
                success: true,
                data,
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Network error',
            };
        }
    },

    getPortfolios: async (): Promise<ApiResponse<Portfolio[]>> => {
        return apiCall<Portfolio[]>('/api/portfolios', {
            method: 'GET',
        });
    },

    deletePortfolio: async (portfolioId: string): Promise<ApiResponse<void>> => {
        return apiCall<void>(`/api/portfolios/${portfolioId}`, {
            method: 'DELETE',
        });
    },
};

// Interview API
export const interviewApi = {
    createSession: async (jobPostingId?: string): Promise<ApiResponse<InterviewSession>> => {
        return apiCall<InterviewSession>('/api/interviews/sessions', {
            method: 'POST',
            body: JSON.stringify({
                job_posting_id: jobPostingId || null
            }),
        });
    },

    getSessionQuestions: async (sessionId: string): Promise<ApiResponse<InterviewQuestion[]>> => {
        return apiCall<InterviewQuestion[]>(`/api/interviews/sessions/${sessionId}/questions`, {
            method: 'GET',
        });
    },
};

// Mock Capability API (simulates backend analysis results)
export const capabilityApi = {
    getCapabilities: async (): Promise<ApiResponse<import('@/types').Capability[]>> => {
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate delay

        // Mock backend capability analysis results
        const capabilities = [
            { skill: 'Professionalism', value: 75 },
            { skill: 'Attitude', value: 80 },
            { skill: 'Creativity', value: 65 },
            { skill: 'Communication', value: 85 },
            { skill: 'Leadership', value: 60 },
            { skill: 'Teamwork', value: 75 },
            { skill: 'Sociability', value: 80 },
        ];

        return {
            success: true,
            data: capabilities
        };
    },

    getImprovementSuggestions: async (): Promise<ApiResponse<import('@/types').ImprovementSuggestion[]>> => {
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate delay

        // Mock backend improvement suggestions for weak capabilities
        const suggestions = [
            {
                id: 'suggestion_1',
                capability: 'Leadership',
                currentScore: 60,
                title: '리더십 역량 강화 방안',
                description: '팀을 이끄는 경험이 부족합니다. 작은 프로젝트부터 리드 역할을 맡아보세요.',
                actionItems: [
                    '소규모 스터디 그룹이나 프로젝트에서 리더 역할 맡아보기',
                    '멘토링 프로그램에 참여하여 후배 개발자 지도하기',
                    '팀 회의에서 적극적으로 의견 제시하고 토론 주도하기',
                    '리더십 관련 도서 읽기 (예: "The Five Dysfunctions of a Team")',
                    '온라인 강의로 리더십 스킬 학습하기'
                ]
            },
            {
                id: 'suggestion_2',
                capability: 'Creativity',
                currentScore: 65,
                title: '창의성 향상 전략',
                description: '창의적인 문제 해결 능력을 더 발전시킬 필요가 있습니다.',
                actionItems: [
                    '다양한 분야의 기술 블로그와 케이스 스터디 읽기',
                    '해커톤이나 아이디어톤에 참여하여 새로운 솔루션 제안하기',
                    '기존 프로젝트를 다른 기술 스택으로 재구현해보기',
                    'UX/UI 디자인 원칙 학습하여 사용자 중심 사고 기르기',
                    '브레인스토밍 세션에 정기적으로 참여하기'
                ]
            }
        ];

        return {
            success: true,
            data: suggestions
        };
    },
};

