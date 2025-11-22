'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Button from '@/components/Button';
import { authApi, profileApi } from '@/lib/auth-client';
import { User } from '@/types';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    const authenticated = authApi.isAuthenticated();
    setIsAuthenticated(authenticated);

    if (authenticated && !user) {
      try {
        const response = await profileApi.getProfile();
        if (response.success && response.data) {
          setUser(response.data);
        }
      } catch (error) {
        console.error('Failed to load user data:', error);
      }
    }

    setLoading(false);
  };

  useEffect(() => {
    checkAuth();
  }, [user]);

  const handleLogout = () => {
    authApi.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="glass-card sticky top-0 z-50 border-b border-border/50">
        <div className="container-custom h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">AI 면접 코칭</span>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="text-muted-foreground text-sm hidden md:block">
                  {user?.email || user?.name}
                </span>
                <Link href="/profile">
                  <Button variant="outline" size="sm">내 정보</Button>
                </Link>
                <Button variant="secondary" size="sm" onClick={handleLogout}>
                  로그아웃
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                  로그인
                </Link>
                <Link href="/signup">
                  <Button variant="primary" size="sm">
                    시작하기
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className={`page-section ${styles.heroSection} flex-1 flex items-center`}>
        <div className="container-custom grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 animate-slide-up">
            <h1 className="text-4xl md:text-6xl font-bold text-foreground leading-tight">
              AI와 함께하는 <br />
              <span className="text-primary">완벽한 면접 준비</span>
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed max-w-lg">
              실시간 AI 피드백으로 면접 스킬을 향상시키세요.
              당신의 이력서를 분석하여 맞춤형 예상 질문을 제공합니다.
            </p>
            <div className="flex gap-4 pt-4">
              {isAuthenticated ? (
                <>
                  <Link href="/profile">
                    <Button variant="secondary" size="lg" className="shadow-lg shadow-primary/10">
                      내 정보 관리
                    </Button>
                  </Link>
                  <Button variant="primary" size="lg" className="shadow-lg shadow-primary/20">
                    면접 시작하기
                  </Button>
                </>
              ) : (
                <>
                  <Link href="/signup">
                    <Button variant="primary" size="lg" className="shadow-lg shadow-primary/20">
                      무료로 시작하기
                    </Button>
                  </Link>
                  <Link href="#features">
                    <Button variant="outline" size="lg">
                      더 알아보기
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="relative animate-scale-in hidden md:block">
            <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full transform translate-y-10"></div>
            <div className="glass-card rounded-2xl p-6 relative z-10 transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-border pb-4">
                  <div className="w-3 h-3 rounded-full bg-error"></div>
                  <div className="w-3 h-3 rounded-full bg-warning"></div>
                  <div className="w-3 h-3 rounded-full bg-success"></div>
                </div>
                <div className="space-y-3">
                  <div className="h-2 bg-muted rounded w-3/4"></div>
                  <div className="h-2 bg-muted rounded w-1/2"></div>
                  <div className="h-20 bg-primary/5 rounded-lg border border-primary/10 p-3">
                    <p className="text-sm text-primary font-medium">
                      "답변의 구조가 매우 논리적입니다. 다만, 구체적인 예시를 들어 설명하면 더욱 설득력이 있을 것 같습니다."
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="page-section bg-surface">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto mb-16 animate-fade-in">
            <h2 className="text-3xl font-bold text-foreground mb-4">주요 기능</h2>
            <p className="text-muted-foreground">
              면접 합격을 위한 모든 기능을 제공합니다
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className={`elevated-card p-8 ${styles.featureCard} animate-slide-up`} style={{ animationDelay: '0.1s' }}>
              <div className={styles.featureIcon}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">이력서 분석</h3>
              <p className="text-muted-foreground leading-relaxed">
                업로드한 이력서를 AI가 심층 분석하여 강점과 약점을 파악하고 개선점을 제안합니다.
              </p>
            </div>

            {/* Feature 2 */}
            <div className={`elevated-card p-8 ${styles.featureCard} animate-slide-up`} style={{ animationDelay: '0.2s' }}>
              <div className={styles.featureIcon}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">맞춤형 질문</h3>
              <p className="text-muted-foreground leading-relaxed">
                지원하는 직무와 이력서를 바탕으로 실제 면접에서 나올 법한 예상 질문을 생성합니다.
              </p>
            </div>

            {/* Feature 3 */}
            <div className={`elevated-card p-8 ${styles.featureCard} animate-slide-up`} style={{ animationDelay: '0.3s' }}>
              <div className={styles.featureIcon}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">실시간 피드백</h3>
              <p className="text-muted-foreground leading-relaxed">
                모의 면접 답변에 대해 내용, 태도, 목소리 톤까지 종합적인 피드백을 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface border-t border-border py-8">
        <div className="container-custom text-center text-muted-foreground text-sm">
          <p>© 2025 AI 면접 코칭. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
