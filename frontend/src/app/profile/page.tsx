'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Combobox from '@/components/Combobox';
import { authApi, profileApi, portfolioApi } from '@/lib/auth-client';
import { User, Portfolio, CVAnalysisResult } from '@/types';
import { JOB_POSITIONS, JOB_LABEL_TO_ROLE, JOB_ROLE_TO_LABEL } from '@/constants/jobs';
import styles from './page.module.css';

export default function ProfilePage() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [analysisResult, setAnalysisResult] = useState<CVAnalysisResult | null>(null);
    const [showAnalysisModal, setShowAnalysisModal] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Form data
    const [formData, setFormData] = useState({
        name: '',
        jobTitle: '',
    });

    useEffect(() => {
        loadUserData();
    }, []);

    const loadUserData = async () => {
        // Check authentication
        if (!authApi.isAuthenticated()) {
            router.push('/login');
            return;
        }

        try {
            // Load user profile
            const profileResponse = await profileApi.getProfile();
            if (profileResponse.success && profileResponse.data) {
                setUser(profileResponse.data);
                // Convert role to display label
                const role = profileResponse.data.role || profileResponse.data.jobTitle;
                const displayJobTitle = role ? JOB_ROLE_TO_LABEL[role] : '';
                setFormData({
                    name: profileResponse.data.name || '',
                    jobTitle: displayJobTitle || '',
                });
            }

            // Load portfolios
            const portfoliosResponse = await portfolioApi.getPortfolios();
            if (portfoliosResponse.success && portfoliosResponse.data) {
                setPortfolios(portfoliosResponse.data);
            }
        } catch (err) {
            console.error('Load user data error:', err);
            setError('데이터를 불러오는데 실패했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const handleSaveProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setSaving(true);

        try {
            // Map display label to role
            const role = JOB_LABEL_TO_ROLE[formData.jobTitle];
            
            const response = await profileApi.updateProfile({
                name: formData.name,
                role: role,
            });

            if (response.success && response.data) {
                setUser(response.data);
                setSuccess('정보가 성공적으로 저장되었습니다.');
            } else {
                setError(response.error || '저장에 실패했습니다.');
            }
        } catch (err) {
            setError('서버와의 통신에 실패했습니다.');
            console.error('Save profile error:', err);
        } finally {
            setSaving(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        setError('');
        setSuccess('');
        setUploading(true);

        const file = e.target.files?.[0];
        if (!file) {
            setUploading(false);
            return;
        }

        try {
            const response = await portfolioApi.uploadPortfolio(file);

            if (response.success && response.data) {
                // Replace with new portfolio (only keep one)
                setPortfolios([response.data]);
                setSuccess('포트폴리오가 업로드되었습니다.');
            } else {
                setError(response.error || '업로드에 실패했습니다.');
            }
        } catch (err) {
            setError('서버와의 통신에 실패했습니다.');
            console.error('Upload error:', err);
        } finally {
            setUploading(false);
            // Clear the input field value to allow re-uploading the same file
            e.target.value = '';
        }
    };

    const handleDeletePortfolio = async (portfolioId: string) => {
        setError('');
        setSuccess('');
        try {
            // TODO: Implement delete endpoint in backend if needed
            // For now, just remove from state
            setPortfolios(prev => prev.filter(p => p.id !== portfolioId));
            setSuccess('포트폴리오가 삭제되었습니다.');
        } catch (err) {
            setError('삭제에 실패했습니다.');
            console.error('Delete error:', err);
        }
    };

    const handleAnalyzePortfolio = async (portfolioId: string) => {
        setError('');
        setSuccess('');
        setAnalyzing(true);
        
        try {
            const response = await portfolioApi.analyzePortfolio(portfolioId);
            if (response.success && response.data) {
                setAnalysisResult(response.data);
                setShowAnalysisModal(true);
                setSuccess('분석이 완료되었습니다.');
            } else {
                setError(response.error || '분석에 실패했습니다.');
            }
        } catch (err) {
            setError('서버와의 통신에 실패했습니다.');
            console.error('Analyze error:', err);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleLogout = () => {
        authApi.logout();
        router.push('/login');
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-6 animate-scale-in">
                {/* Header */}
                <div className="glass-card rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center text-3xl">
                            👤
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-foreground">
                                {user?.name || '사용자'}
                            </h1>
                            <p className="text-muted-foreground">
                                {(user?.role || user?.jobTitle)
                                    ? JOB_ROLE_TO_LABEL[user.role || user.jobTitle || ''] 
                                    : '직무 미설정'}
                            </p>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={() => router.push('/')}>
                            홈으로
                        </Button>
                        <Button variant="secondary" onClick={handleLogout}>
                            로그아웃
                        </Button>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    {/* Sidebar / Profile Edit */}
                    <div className="md:col-span-1 space-y-6">
                        <div className="glass-card rounded-3xl p-6">
                            <h2 className="text-lg font-bold text-foreground mb-4">프로필 수정</h2>
                            <form onSubmit={handleSaveProfile} className="space-y-4">
                                <Input
                                    label="이름"
                                    value={formData.name}
                                    disabled
                                />
                                <Combobox
                                    label="직무"
                                    options={JOB_POSITIONS}
                                    value={formData.jobTitle}
                                    onChange={(value) => setFormData({ ...formData, jobTitle: value })}
                                    placeholder="직무를 선택하거나 입력하세요"
                                />
                                {error && (
                                    <div className="bg-error/10 border border-error rounded-xl p-3">
                                        <p className="text-error text-sm">{error}</p>
                                    </div>
                                )}

                                {success && (
                                    <div className="bg-success/10 border border-success rounded-xl p-3">
                                        <p className="text-success text-sm">{success}</p>
                                    </div>
                                )}
                                <Button
                                    type="submit"
                                    variant="primary"
                                    className="w-full"
                                    isLoading={saving}
                                >
                                    저장하기
                                </Button>
                            </form>
                        </div>
                    </div>

                    {/* Main Content / Portfolio */}
                    <div className="md:col-span-2 space-y-6">
                        {/* Portfolio Upload */}
                        <div className="glass-card rounded-3xl p-6">
                            <h2 className="text-lg font-bold text-foreground mb-4">포트폴리오 업로드</h2>
                            {portfolios.length === 0 ? (
                                <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-primary/50 transition-colors">
                                    <input
                                        type="file"
                                        id="portfolio-upload"
                                        className="hidden"
                                        accept=".pdf"
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                    />
                                    <label htmlFor="portfolio-upload" className="cursor-pointer flex flex-col items-center gap-3">
                                        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                            📄
                                        </div>
                                        <div>
                                            <p className="font-medium text-foreground">PDF 파일 업로드</p>
                                            <p className="text-sm text-muted-foreground">최대 10MB</p>
                                        </div>
                                        {uploading && <p className="text-sm text-primary">업로드 중...</p>}
                                    </label>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {portfolios.map((portfolio) => (
                                        <div key={portfolio.id} className="flex items-center justify-between p-4 bg-surface/50 rounded-xl border border-border">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center text-red-500">
                                                    PDF
                                                </div>
                                                <div>
                                                    <p className="font-medium text-foreground">{portfolio.filename}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        PDF 문서
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex gap-2">
                                                <Button 
                                                    variant="outline" 
                                                    size="sm"
                                                    onClick={() => handleAnalyzePortfolio(portfolio.id)}
                                                    isLoading={analyzing}
                                                >
                                                    분석 보기
                                                </Button>
                                                <Button 
                                                    variant="outline" 
                                                    size="sm"
                                                    onClick={() => handleDeletePortfolio(portfolio.id)}
                                                >
                                                    삭제
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                    <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-primary/50 transition-colors">
                                        <input
                                            type="file"
                                            id="portfolio-upload-replace"
                                            className="hidden"
                                            accept=".pdf"
                                            onChange={handleFileUpload}
                                            disabled={uploading}
                                        />
                                        <label htmlFor="portfolio-upload-replace" className="cursor-pointer flex flex-col items-center gap-3">
                                            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                                🔄
                                            </div>
                                            <div>
                                                <p className="font-medium text-foreground">파일 변경</p>
                                                <p className="text-sm text-muted-foreground">새 PDF를 업로드하면 기존 파일이 대체됩니다</p>
                                            </div>
                                            {uploading && <p className="text-sm text-primary">업로드 중...</p>}
                                        </label>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Analysis Modal */}
                {showAnalysisModal && analysisResult && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-background rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-scale-in">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-foreground">포트폴리오 분석 결과</h2>
                                <button 
                                    onClick={() => setShowAnalysisModal(false)}
                                    className="text-muted-foreground hover:text-foreground"
                                >
                                    ✕
                                </button>
                            </div>
                            
                            <div className="space-y-6">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-surface p-4 rounded-xl">
                                        <p className="text-sm text-muted-foreground mb-1">직무 적합도</p>
                                        <p className="text-2xl font-bold text-primary">{analysisResult.overall_score}점</p>
                                    </div>
                                    <div className="bg-surface p-4 rounded-xl">
                                        <p className="text-sm text-muted-foreground mb-1">분석된 직무</p>
                                        <p className="text-xl font-bold text-foreground">{analysisResult.role}</p>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="font-bold text-foreground mb-3">보유 기술</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {analysisResult.possessed_skills.map((skill, i) => (
                                            <span key={i} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <h3 className="font-bold text-foreground mb-3 flex items-center gap-2">
                                            <span className="text-green-500">💪</span> 강점
                                        </h3>
                                        <ul className="space-y-3">
                                            {analysisResult.strengths.map((item, i) => (
                                                <li key={i} className="bg-surface/50 p-3 rounded-xl text-sm">
                                                    <p className="font-bold text-foreground mb-1">{item.skill}</p>
                                                    <p className="text-muted-foreground">{item.reason}</p>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-foreground mb-3 flex items-center gap-2">
                                            <span className="text-red-500">🎯</span> 보완점
                                        </h3>
                                        <ul className="space-y-3">
                                            {analysisResult.weaknesses.map((item, i) => (
                                                <li key={i} className="bg-surface/50 p-3 rounded-xl text-sm">
                                                    <p className="font-bold text-foreground mb-1">{item.skill}</p>
                                                    <p className="text-muted-foreground">{item.reason}</p>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="font-bold text-foreground mb-3">총평</h3>
                                    <div className="bg-surface/50 p-4 rounded-xl text-sm text-muted-foreground leading-relaxed">
                                        {analysisResult.summary}
                                    </div>
                                </div>

                                <div className="flex justify-end pt-4">
                                    <Button onClick={() => setShowAnalysisModal(false)}>
                                        닫기
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
