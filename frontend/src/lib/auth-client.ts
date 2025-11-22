import { ApiResponse, AuthResponse, User, Portfolio } from '@/types';

// Mock Data
const MOCK_USER: User = {
    id: 'user_1',
    email: 'demo@example.com',
    name: '김철수',
    jobTitle: 'Frontend Developer',
};

const MOCK_PORTFOLIOS: Portfolio[] = [
    {
        id: 'portfolio_1',
        user_id: 'user_1',
        filename: 'portfolio_v1.pdf',
        file_url: '#',
        parsed_text: '이 포트폴리오는 프론트엔드 개발 경험을 중심으로 구성되어 있습니다. React, Next.js, TypeScript를 주력으로 사용하며, 다양한 프로젝트 경험을 보유하고 있습니다.',
        summary: '프론트엔드 개발자로서의 역량이 잘 드러나는 포트폴리오입니다. 특히 React 생태계에 대한 이해도가 높습니다.',
    },
    {
        id: 'portfolio_2',
        user_id: 'user_1',
        filename: 'project_showcase.pdf',
        file_url: '#',
        parsed_text: '이 프로젝트는 AI를 활용한 면접 코칭 서비스입니다. 사용자의 이력서를 분석하고 맞춤형 면접 질문을 생성합니다.',
        summary: 'AI 기술을 활용한 프로젝트 경험이 돋보입니다. 풀스택 개발 능력을 증명하는 좋은 사례입니다.',
    }
];

// Token storage (simulated)
export const TokenStorage = {
    setTokens: (tokens: { accessToken: string; refreshToken: string }) => {
        if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', tokens.accessToken);
            localStorage.setItem('refreshToken', tokens.refreshToken);
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

// Mock Auth API
export const authApi = {
    signup: async (email: string, password: string): Promise<ApiResponse<AuthResponse>> => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay

        const mockTokens = {
            accessToken: 'mock_access_token_' + Date.now(),
            refreshToken: 'mock_refresh_token_' + Date.now(),
        };

        // Simulate creating a new user
        const newUser = {
            ...MOCK_USER,
            email,
            name: email.split('@')[0],
            jobTitle: '', // Reset for new user
        };

        // Update global mock user to simulate persistence
        Object.assign(MOCK_USER, newUser);

        return {
            success: true,
            data: {
                user: newUser,
                tokens: mockTokens
            }
        };
    },

    login: async (email: string, password: string): Promise<ApiResponse<AuthResponse>> => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay

        // For testing, accept any credentials
        const mockTokens = {
            accessToken: 'mock_access_token_' + Date.now(),
            refreshToken: 'mock_refresh_token_' + Date.now(),
        };

        // Update mock user to match login email if different
        if (email !== MOCK_USER.email) {
            Object.assign(MOCK_USER, {
                email,
                name: email.split('@')[0],
            });
        }

        return {
            success: true,
            data: {
                user: { ...MOCK_USER },
                tokens: mockTokens
            }
        };
    },

    logout: () => {
        TokenStorage.clearTokens();
    },

    isAuthenticated: (): boolean => {
        return !!TokenStorage.getAccessToken();
    },
};

// Mock Profile API
export const profileApi = {
    getProfile: async (): Promise<ApiResponse<User>> => {
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate delay
        return {
            success: true,
            data: MOCK_USER
        };
    },

    updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay

        // Update mock user in memory (persists only for session/reload if we don't save to LS, but good enough for mock)
        Object.assign(MOCK_USER, data);

        return {
            success: true,
            data: { ...MOCK_USER }
        };
    },
};

// Mock Portfolio API
export const portfolioApi = {
    uploadPortfolio: async (file: File): Promise<ApiResponse<Portfolio>> => {
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate upload delay

        const newPortfolio: Portfolio = {
            id: 'portfolio_' + Date.now(),
            user_id: MOCK_USER.id,
            filename: file.name,
            file_url: URL.createObjectURL(file), // Create a local URL for the file
            parsed_text: '새로 업로드된 포트폴리오의 분석 내용입니다. 이력서 내용이 충실하며, 프로젝트 경험이 잘 기술되어 있습니다.',
            summary: '업로드된 파일에 대한 AI 분석 요약입니다. 전반적으로 훌륭한 역량을 보유하고 있습니다.',
        };

        MOCK_PORTFOLIOS.push(newPortfolio);

        return {
            success: true,
            data: newPortfolio
        };
    },

    getPortfolios: async (): Promise<ApiResponse<Portfolio[]>> => {
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate delay
        return {
            success: true,
            data: [...MOCK_PORTFOLIOS]
        };
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

