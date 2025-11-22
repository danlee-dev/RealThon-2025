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
          <div className="flex items-center gap-3">
            <svg width="40" height="40" viewBox="0 0 70 70" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M35 15C45.4934 15 54 23.7304 54 34.5C54 38.8009 52.6419 42.7757 50.3438 46H19.6562C17.3581 42.7757 16 38.8009 16 34.5C16 23.7304 24.5066 15 35 15Z" fill="#FF4D12"/>
              <path fillRule="evenodd" clipRule="evenodd" d="M12.396 55.4165C12.396 54.8363 12.6265 54.2799 13.0367 53.8697C13.4469 53.4595 14.0033 53.229 14.5835 53.229H55.4168C55.997 53.229 56.5534 53.4595 56.9636 53.8697C57.3739 54.2799 57.6043 54.8363 57.6043 55.4165C57.6043 55.9967 57.3739 56.5531 56.9636 56.9633C56.5534 57.3735 55.997 57.604 55.4168 57.604H14.5835C14.0033 57.604 13.4469 57.3735 13.0367 56.9633C12.6265 56.5531 12.396 55.9967 12.396 55.4165ZM21.146 64.1665C21.146 63.5863 21.3765 63.0299 21.7867 62.6197C22.1969 62.2095 22.7533 61.979 23.3335 61.979H46.6668C47.247 61.979 47.8034 62.2095 48.2136 62.6197C48.6239 63.0299 48.8543 63.5863 48.8543 64.1665C48.8543 64.7467 48.6239 65.3031 48.2136 65.7133C47.8034 66.1235 47.247 66.354 46.6668 66.354H23.3335C22.7533 66.354 22.1969 66.1235 21.7867 65.7133C21.3765 65.3031 21.146 64.7467 21.146 64.1665Z" fill="#FFDA8F"/>
              <path fillRule="evenodd" clipRule="evenodd" d="M35.0002 3.646C35.5803 3.646 36.1367 3.87646 36.547 4.2867C36.9572 4.69694 37.1877 5.25333 37.1877 5.8335V8.75016C37.1877 9.33032 36.9572 9.88672 36.547 10.297C36.1367 10.7072 35.5803 10.9377 35.0002 10.9377C34.42 10.9377 33.8636 10.7072 33.4534 10.297C33.0431 9.88672 32.8127 9.33032 32.8127 8.75016V5.8335C32.8127 5.25333 33.0431 4.69694 33.4534 4.2867C33.8636 3.87646 34.42 3.646 35.0002 3.646ZM12.8306 12.8306C13.2407 12.4209 13.7967 12.1908 14.3764 12.1908C14.9561 12.1908 15.5121 12.4209 15.9222 12.8306L17.0685 13.9739C17.4672 14.3863 17.6879 14.9388 17.6832 15.5123C17.6785 16.0859 17.4487 16.6346 17.0433 17.0404C16.6379 17.4462 16.0894 17.6765 15.5158 17.6818C14.9423 17.687 14.3896 17.4668 13.9768 17.0685L12.8306 15.9222C12.4209 15.5121 12.1908 14.9561 12.1908 14.3764C12.1908 13.7967 12.4209 13.2407 12.8306 12.8306ZM57.1697 12.8306C57.5794 13.2407 57.8095 13.7967 57.8095 14.3764C57.8095 14.9561 57.5794 15.5121 57.1697 15.9222L56.0235 17.0685C55.6088 17.4549 55.0604 17.6653 54.4936 17.6553C53.9269 17.6453 53.3862 17.4157 52.9854 17.0149C52.5846 16.6141 52.3551 16.0734 52.3451 15.5067C52.3351 14.94 52.5454 14.3915 52.9318 13.9768L54.0781 12.8306C54.4882 12.4209 55.0442 12.1908 55.6239 12.1908C56.2036 12.1908 56.7596 12.4209 57.1697 12.8306ZM3.646 35.0002C3.646 34.42 3.87646 33.8636 4.2867 33.4534C4.69694 33.0431 5.25334 32.8127 5.8335 32.8127H8.75016C9.33032 32.8127 9.88672 33.0431 10.297 33.4534C10.7072 33.8636 10.9377 34.42 10.9377 35.0002C10.9377 35.5803 10.7072 36.1367 10.297 36.547C9.88672 36.9572 9.33032 37.1877 8.75016 37.1877H5.8335C5.25334 37.1877 4.69694 36.9572 4.2867 36.547C3.87646 36.1367 3.646 35.5803 3.646 35.0002ZM59.0627 35.0002C59.0627 34.42 59.2931 33.8636 59.7034 33.4534C60.1136 33.0431 60.67 32.8127 61.2502 32.8127H64.1668C64.747 32.8127 65.3034 33.0431 65.7136 33.4534C66.1239 33.8636 66.3543 34.42 66.3543 35.0002C66.3543 35.5803 66.1239 36.1367 65.7136 36.547C65.3034 36.9572 64.747 37.1877 64.1668 37.1877H61.2502C60.67 37.1877 60.1136 36.9572 59.7034 36.547C59.2931 36.1367 59.0627 35.5803 59.0627 35.0002Z" fill="#FF4D12"/>
              <line x1="6" y1="47" x2="64" y2="47" stroke="#FF8C00" strokeWidth="4" strokeLinecap="round"/>
            </svg>
            <span className="text-2xl font-extrabold text-primary">내일면접</span>
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
                  <Link href="/interview">
                    <Button variant="primary" size="lg" className="shadow-lg shadow-primary/20">
                      면접 시작하기
                    </Button>
                  </Link>
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
