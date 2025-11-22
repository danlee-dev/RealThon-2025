import { ApiResponse, AuthResponse, User, Portfolio } from '@/types';

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
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token && !options.headers?.['Authorization']) {
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
};
