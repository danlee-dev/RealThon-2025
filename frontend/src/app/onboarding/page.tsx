'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Combobox from '@/components/Combobox';
import { profileApi, portfolioApi } from '@/lib/auth-client';
import styles from './page.module.css';

// Predefined job positions
const JOB_POSITIONS = [
    // Frontend
    'Frontend Developer',
    'React Developer',
    'Vue.js Developer',
    'Angular Developer',

    // Backend
    'Backend Developer',
    'Node.js Developer',
    'Java Developer',
    'Python Developer',
    'Go Developer',
    'PHP Developer',

    // Full Stack
    'Full Stack Developer',

    // Mobile
    'Mobile Developer',
    'iOS Developer',
    'Android Developer',
    'React Native Developer',
    'Flutter Developer',

    // DevOps & Cloud
    'DevOps Engineer',
    'Cloud Engineer',
    'Site Reliability Engineer (SRE)',
    'Infrastructure Engineer',
    'Platform Engineer',

    // Data & AI
    'Data Scientist',
    'Data Engineer',
    'Machine Learning Engineer',
    'AI Research Engineer',
    'Data Analyst',

    // Product & Design
    'Product Manager',
    'Product Owner',
    'UX Designer',
    'UI Designer',
    'UX/UI Designer',
    'Product Designer',

    // QA & Testing
    'QA Engineer',
    'Test Engineer',
    'QA Automation Engineer',

    // Architecture & Leadership
    'Software Architect',
    'Solution Architect',
    'Technical Lead',
    'Engineering Manager',

    // Specialized
    'Security Engineer',
    'Database Administrator',
    'System Administrator',
    'Blockchain Developer',
    'Game Developer',
    'Embedded Systems Engineer',
];

interface PortfolioLink {
    url: string;
    label: string;
}

export default function OnboardingPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        jobTitle: '',
        portfolioFile: null as File | null,
        portfolioLinks: [] as PortfolioLink[],
    });

    const addPortfolioLink = () => {
        if (formData.portfolioLinks.length < 5) {
            setFormData({
                ...formData,
                portfolioLinks: [...formData.portfolioLinks, { url: '', label: '' }],
            });
        }
    };

    const removePortfolioLink = (index: number) => {
        setFormData({
            ...formData,
            portfolioLinks: formData.portfolioLinks.filter((_, i) => i !== index),
        });
    };

    const updatePortfolioLink = (index: number, field: 'url' | 'label', value: string) => {
        const updated = [...formData.portfolioLinks];
        updated[index][field] = value;
        setFormData({ ...formData, portfolioLinks: updated });
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setFormData({ ...formData, portfolioFile: file });
        }
    };

    const removeFile = () => {
        setFormData({ ...formData, portfolioFile: null });
    };

    const handleNext = () => {
        if (step === 1 && !formData.name.trim()) {
            alert('이름을 입력해주세요.');
            return;
        }
        if (step === 2 && !formData.jobTitle.trim()) {
            alert('직무를 선택해주세요.');
            return;
        }
        if (step < 4) {
            setStep(step + 1);
        } else {
            handleSubmit();
        }
    };

    const handlePrevious = () => {
        if (step > 1) {
            setStep(step - 1);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            // 1. Upload portfolio file if provided
            if (formData.portfolioFile) {
                setUploading(true);
                const uploadResponse = await portfolioApi.uploadPortfolio(formData.portfolioFile);
                if (!uploadResponse.success) {
                    alert('포트폴리오 파일 업로드에 실패했습니다.');
                    setLoading(false);
                    setUploading(false);
                    return;
                }
                setUploading(false);
            }

            // 2. Update profile with name, jobTitle, and portfolio URLs
            const urls = formData.portfolioLinks
                .filter(link => link.url.trim())
                .map(link => link.url.trim());

            // TODO: Portfolio URLs will need to be saved separately or User type needs to be updated
            const response = await profileApi.updateProfile({
                name: formData.name,
                jobTitle: formData.jobTitle,
            });

            if (response.success) {
                router.push('/');
            } else {
                alert('프로필 업데이트에 실패했습니다.');
            }
        } catch (error) {
            console.error('Onboarding error:', error);
            alert('오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const canProceed = () => {
        if (step === 1) return formData.name.trim().length > 0;
        if (step === 2) return formData.jobTitle.trim().length > 0;
        return true; // Steps 3 and 4 are optional
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="w-full max-w-md animate-scale-in">
                <div className="glass-card rounded-3xl p-8 md:p-10">
                    {/* Progress Bar */}
                    <div className="w-full h-2 bg-muted rounded-full mb-8 overflow-hidden">
                        <div
                            className="h-full bg-primary transition-all duration-500 ease-in-out"
                            style={{ width: `${(step / 4) * 100}%` }}
                        ></div>
                    </div>

                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
                            {step === 1 && '기본 정보'}
                            {step === 2 && '직무 정보'}
                            {step === 3 && '포트폴리오 파일'}
                            {step === 4 && '포트폴리오 링크'}
                        </h1>
                        <p className="text-muted-foreground">
                            {step === 1 && '사용자 정보를 입력해주세요'}
                            {step === 2 && '희망하는 직무를 선택해주세요'}
                            {step === 3 && 'PDF 포트폴리오를 업로드하세요 (선택)'}
                            {step === 4 && '포트폴리오 링크를 추가하세요 (선택)'}
                        </p>
                    </div>

                    {/* Form */}
                    <div className="space-y-6">
                        {/* Step 1: Name */}
                        {step === 1 && (
                            <div className="space-y-4 animate-fade-in">
                                <Input
                                    label="이름"
                                    placeholder="홍길동"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    autoFocus
                                />
                            </div>
                        )}

                        {/* Step 2: Job Title */}
                        {step === 2 && (
                            <div className="space-y-4 animate-fade-in">
                                <Combobox
                                    label="희망 직무"
                                    options={JOB_POSITIONS}
                                    value={formData.jobTitle}
                                    onChange={(value) => setFormData({ ...formData, jobTitle: value })}
                                    placeholder="직무를 선택하거나 입력하세요"
                                    required
                                />
                            </div>
                        )}

                        {/* Step 3: Portfolio File Upload */}
                        {step === 3 && (
                            <div className="space-y-4 animate-fade-in">
                                {!formData.portfolioFile ? (
                                    <div className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-primary/50 transition-colors">
                                        <input
                                            type="file"
                                            id="portfolio-upload"
                                            className="hidden"
                                            accept=".pdf"
                                            onChange={handleFileChange}
                                        />
                                        <label htmlFor="portfolio-upload" className="cursor-pointer flex flex-col items-center gap-3">
                                            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary text-2xl">
                                                📄
                                            </div>
                                            <div>
                                                <p className="font-medium text-foreground">PDF 파일 업로드</p>
                                                <p className="text-sm text-muted-foreground">최대 10MB</p>
                                            </div>
                                        </label>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-between p-4 bg-surface/50 rounded-xl border border-border">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center text-red-500 text-xs font-bold">
                                                PDF
                                            </div>
                                            <div>
                                                <p className="font-medium text-foreground">{formData.portfolioFile.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {(formData.portfolioFile.size / 1024).toFixed(1)} KB
                                                </p>
                                            </div>
                                        </div>
                                        <Button variant="outline" size="sm" onClick={removeFile}>
                                            ✕
                                        </Button>
                                    </div>
                                )}
                                <p className="text-xs text-muted-foreground text-center">
                                    포트폴리오 파일은 선택사항입니다. 건너뛰려면 다음을 클릭하세요.
                                </p>
                            </div>
                        )}

                        {/* Step 4: Portfolio Links */}
                        {step === 4 && (
                            <div className="space-y-4 animate-fade-in">
                                {formData.portfolioLinks.length === 0 ? (
                                    <div className="text-center py-8">
                                        <p className="text-muted-foreground mb-4">
                                            포트폴리오 링크를 추가하세요
                                        </p>
                                        <Button variant="outline" onClick={addPortfolioLink}>
                                            + 링크 추가
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {formData.portfolioLinks.map((link, index) => (
                                            <div key={index} className="space-y-2 p-4 bg-surface/50 rounded-xl border border-border">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-sm font-medium text-foreground">링크 {index + 1}</span>
                                                    <Button variant="outline" size="sm" onClick={() => removePortfolioLink(index)}>
                                                        ✕
                                                    </Button>
                                                </div>
                                                <Input
                                                    placeholder="https://github.com/username"
                                                    value={link.url}
                                                    onChange={(e) => updatePortfolioLink(index, 'url', e.target.value)}
                                                />
                                                <Input
                                                    placeholder="라벨 (선택사항, 예: GitHub)"
                                                    value={link.label}
                                                    onChange={(e) => updatePortfolioLink(index, 'label', e.target.value)}
                                                />
                                            </div>
                                        ))}
                                        {formData.portfolioLinks.length < 5 && (
                                            <Button variant="outline" className="w-full" onClick={addPortfolioLink}>
                                                + 링크 추가
                                            </Button>
                                        )}
                                    </div>
                                )}
                                <p className="text-xs text-muted-foreground text-center">
                                    최대 5개의 링크를 추가할 수 있습니다. 선택사항입니다.
                                </p>
                            </div>
                        )}

                        {/* Navigation Buttons */}
                        <div className="flex gap-3 pt-4">
                            {step > 1 && (
                                <Button
                                    variant="outline"
                                    onClick={handlePrevious}
                                    className="flex-1"
                                >
                                    이전
                                </Button>
                            )}
                            <Button
                                variant="primary"
                                onClick={handleNext}
                                className="flex-1"
                                isLoading={loading || uploading}
                                disabled={!canProceed()}
                            >
                                {step === 4 ? '완료' : '다음'}
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
