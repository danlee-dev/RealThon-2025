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


// Job Posting API
export const jobPostingApi = {
    submitJobPosting: async (url: string): Promise<ApiResponse<{ id: string }>> => {
        // First, get the current user to obtain user_id
        const userResponse = await apiCall<User>('/api/users/me', {
            method: 'GET',
        });

        if (!userResponse.success || !userResponse.data) {
            return {
                success: false,
                error: 'Failed to get user information',
            };
        }

        const userId = userResponse.data.id;

        // Submit job posting URL for crawling
        return apiCall<{ id: string }>(`/api/job-postings/crawl?user_id=${userId}`, {
            method: 'POST',
            body: JSON.stringify({
                url: url
            }),
        });
    },
};

// Interview API
export const interviewApi = {
    createSession: async (jobPostingId: string): Promise<ApiResponse<InterviewSession>> => {
        // Get the current user to obtain user_id
        const userResponse = await apiCall<User>('/api/users/me', {
            method: 'GET',
        });

        if (!userResponse.success || !userResponse.data) {
            return {
                success: false,
                error: 'Failed to get user information',
            };
        }

        const userId = userResponse.data.id;

        // Create interview session with job_posting_id (required)
        return apiCall<InterviewSession>(`/api/interviews/sessions?user_id=${userId}`, {
            method: 'POST',
            body: JSON.stringify({
                job_posting_id: jobPostingId
            }),
        });
    },

    getSessionQuestions: async (sessionId: string): Promise<ApiResponse<InterviewQuestion[]>> => {
        return apiCall<InterviewQuestion[]>(`/api/interviews/sessions/${sessionId}/questions`, {
            method: 'GET',
        });
    },
};

// Capability API (real backend integration)
export const capabilityApi = {
    /**
     * 역량 평가 생성 (Gemini 사용)
     *
     * @param portfolioId - 포트폴리오 ID (선택, 없으면 첫 번째 포트폴리오 사용)
     * @returns 생성된 역량 평가 결과
     */
    generateCapabilities: async (portfolioId?: string): Promise<ApiResponse<any>> => {
        try {
            // 1. portfolioId가 없으면 첫 번째 포트폴리오 조회
            if (!portfolioId) {
                const portfoliosResponse = await apiCall<import('@/types').Portfolio[]>('/api/portfolios', {
                    method: 'GET'
                });

                if (!portfoliosResponse.success || !portfoliosResponse.data || portfoliosResponse.data.length === 0) {
                    return {
                        success: false,
                        error: '포트폴리오를 찾을 수 없습니다.'
                    };
                }

                portfolioId = portfoliosResponse.data[0].id;
            }

            // 2. 역량 평가 생성 요청
            const response = await apiCall<any>(`/api/portfolios/${portfolioId}/capabilities/generate`, {
                method: 'POST'
            });

            if (!response.success || !response.data) {
                return {
                    success: false,
                    error: response.error || '역량 평가 생성 실패'
                };
            }

            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Network error'
            };
        }
    },

    /**
     * 포트폴리오의 역량 평가 데이터 조회
     *
     * @param portfolioId - 포트폴리오 ID (선택, 없으면 첫 번째 포트폴리오 사용)
     * @returns 6개 역량 카테고리 (스파이더 차트용)
     */
    getCapabilities: async (portfolioId?: string): Promise<ApiResponse<import('@/types').Capability[]>> => {
        try {
            // 1. portfolioId가 없으면 첫 번째 포트폴리오 조회
            if (!portfolioId) {
                const portfoliosResponse = await apiCall<import('@/types').Portfolio[]>('/api/portfolios', {
                    method: 'GET'
                });

                if (!portfoliosResponse.success || !portfoliosResponse.data || portfoliosResponse.data.length === 0) {
                    return {
                        success: false,
                        error: '포트폴리오를 찾을 수 없습니다.'
                    };
                }

                portfolioId = portfoliosResponse.data[0].id;
            }

            // 2. 역량 평가 데이터 조회
            const response = await apiCall<{
                capabilities: Array<{
                    skill: string;
                    value: number;
                    skill_ko?: string;
                }>;
                improvement_suggestions: any[];
            }>(`/api/portfolios/${portfolioId}/capabilities`, {
                method: 'GET'
            });

            if (!response.success || !response.data) {
                // 404 에러인 경우 역량 평가가 없는 것이므로, 자동 생성 시도
                if (response.error?.includes('404') || response.error?.includes('역량 평가 데이터가 없습니다')) {
                    console.log('[INFO] 역량 평가 없음. 자동 생성 시도...');

                    // 자동으로 역량 평가 생성
                    const generateResponse = await capabilityApi.generateCapabilities(portfolioId);

                    if (!generateResponse.success) {
                        return {
                            success: false,
                            error: '역량 평가 생성 실패: ' + (generateResponse.error || 'Unknown error')
                        };
                    }

                    // 생성 후 다시 조회
                    const retryResponse = await apiCall<{
                        capabilities: Array<{
                            skill: string;
                            value: number;
                            skill_ko?: string;
                        }>;
                        improvement_suggestions: any[];
                    }>(`/api/portfolios/${portfolioId}/capabilities`, {
                        method: 'GET'
                    });

                    if (!retryResponse.success || !retryResponse.data) {
                        return {
                            success: false,
                            error: '역량 데이터 재조회 실패'
                        };
                    }

                    return {
                        success: true,
                        data: retryResponse.data.capabilities
                    };
                }

                return {
                    success: false,
                    error: response.error || '역량 데이터 조회 실패'
                };
            }

            return {
                success: true,
                data: response.data.capabilities
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Network error'
            };
        }
    },

    /**
     * 개선 제안 데이터 조회
     *
     * @param portfolioId - 포트폴리오 ID (선택, 없으면 첫 번째 포트폴리오 사용)
     * @returns 낮은 점수 역량에 대한 개선 제안 리스트
     */
    getImprovementSuggestions: async (portfolioId?: string): Promise<ApiResponse<import('@/types').ImprovementSuggestion[]>> => {
        try {
            // 1. portfolioId가 없으면 첫 번째 포트폴리오 조회
            if (!portfolioId) {
                const portfoliosResponse = await apiCall<import('@/types').Portfolio[]>('/api/portfolios', {
                    method: 'GET'
                });

                if (!portfoliosResponse.success || !portfoliosResponse.data || portfoliosResponse.data.length === 0) {
                    return {
                        success: false,
                        error: '포트폴리오를 찾을 수 없습니다.'
                    };
                }

                portfolioId = portfoliosResponse.data[0].id;
            }

            // 2. 역량 평가 데이터 조회
            const response = await apiCall<{
                capabilities: any[];
                improvement_suggestions: Array<{
                    id: string;
                    capability: string;
                    capability_ko: string;
                    currentScore: number;
                    title: string;
                    description: string;
                    actionItems: string[];
                }>;
            }>(`/api/portfolios/${portfolioId}/capabilities`, {
                method: 'GET'
            });

            if (!response.success || !response.data) {
                // 404 에러인 경우 역량 평가가 없는 것이므로, 자동 생성 시도
                if (response.error?.includes('404') || response.error?.includes('역량 평가 데이터가 없습니다')) {
                    console.log('[INFO] 역량 평가 없음. 자동 생성 시도...');

                    // 자동으로 역량 평가 생성
                    const generateResponse = await capabilityApi.generateCapabilities(portfolioId);

                    if (!generateResponse.success) {
                        return {
                            success: false,
                            error: '역량 평가 생성 실패: ' + (generateResponse.error || 'Unknown error')
                        };
                    }

                    // 생성 후 다시 조회
                    const retryResponse = await apiCall<{
                        capabilities: any[];
                        improvement_suggestions: Array<{
                            id: string;
                            capability: string;
                            capability_ko: string;
                            currentScore: number;
                            title: string;
                            description: string;
                            actionItems: string[];
                        }>;
                    }>(`/api/portfolios/${portfolioId}/capabilities`, {
                        method: 'GET'
                    });

                    if (!retryResponse.success || !retryResponse.data) {
                        return {
                            success: false,
                            error: '개선 제안 재조회 실패'
                        };
                    }

                    return {
                        success: true,
                        data: retryResponse.data.improvement_suggestions
                    };
                }

                return {
                    success: false,
                    error: response.error || '개선 제안 조회 실패'
                };
            }

            return {
                success: true,
                data: response.data.improvement_suggestions
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Network error'
            };
        }
    },
};

