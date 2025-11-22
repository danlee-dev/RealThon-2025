'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { authApi, profileApi, portfolioApi } from '@/lib/auth-client';
import { User, Portfolio } from '@/types';
import styles from './page.module.css';

export default function ProfilePage() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
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
                setFormData({
                    name: profileResponse.data.name || '',
                    jobTitle: profileResponse.data.jobTitle || '',
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
            const response = await profileApi.updateProfile(formData);

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
                setPortfolios(prev => [...prev, response.data!]);
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
                                {user?.jobTitle || '직무 미설정'}
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
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                                <Input
                                    label="직무"
                                    value={formData.jobTitle}
                                    onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
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
                        </div>

                        {/* Portfolio List */}
                        <div className="glass-card rounded-3xl p-6">
                            <h2 className="text-lg font-bold text-foreground mb-4">내 포트폴리오</h2>
                            {portfolios.length === 0 ? (
                                <p className="text-muted-foreground text-center py-8">
                                    등록된 포트폴리오가 없습니다.
                                </p>
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
                                            <Button variant="outline" size="sm">
                                                분석 보기
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
