'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import WaitingScreen from './components/screens/WaitingScreen';
import InterviewingScreen from './components/screens/InterviewingScreen';
import AnalyzingScreen from './components/screens/AnalyzingScreen';
import CompleteScreen from './components/screens/CompleteScreen';
import { InterviewStage, AnalysisResults } from './types';
import { interviewApi, jobPostingApi } from '@/lib/auth-client';

export default function InterviewPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSignLanguageMode, setIsSignLanguageMode] = useState(false);
  const [currentStage, setCurrentStage] = useState<InterviewStage>(InterviewStage.WAITING);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);

  const handleStartInterview = async (jobPostingUrl?: string) => {
    console.log('[DEBUG] Starting interview, creating session and loading questions');
    setIsLoadingQuestions(true);

    try {
      // Job posting URL is required
      if (!jobPostingUrl) {
        alert('취업 공고 URL을 입력해주세요.');
        setIsLoadingQuestions(false);
        return;
      }

      // Submit job posting URL to get the ID
      console.log('[DEBUG] Submitting job posting URL:', jobPostingUrl);
      const jobPostingResponse = await jobPostingApi.submitJobPosting(jobPostingUrl);

      if (!jobPostingResponse.success || !jobPostingResponse.data) {
        console.error('[ERROR] Failed to submit job posting URL:', jobPostingResponse.error);
        alert('공고 URL 제출에 실패했습니다. 다시 시도해주세요.');
        setIsLoadingQuestions(false);
        return;
      }

      const jobPostingId = jobPostingResponse.data.id;
      console.log('[DEBUG] Job posting ID received:', jobPostingId);

      const sessionResponse = await interviewApi.createSession(jobPostingId);

      if (!sessionResponse.success || !sessionResponse.data) {
        console.error('[ERROR] Failed to create interview session:', sessionResponse.error);
        alert('면접 세션 생성에 실패했습니다.');
        setIsLoadingQuestions(false);
        return;
      }

      const session = sessionResponse.data;
      setSessionId(session.id);
      console.log('[DEBUG] Session created:', session.id);

      const questionsResponse = await interviewApi.getSessionQuestions(session.id);

      if (!questionsResponse.success || !questionsResponse.data) {
        console.error('[ERROR] Failed to load questions:', questionsResponse.error);
        alert('질문 로드에 실패했습니다.');
        setIsLoadingQuestions(false);
        return;
      }

      const loadedQuestions = questionsResponse.data
        .sort((a, b) => a.order - b.order)
        .map(q => q.text);

      setQuestions(loadedQuestions);
      console.log('[DEBUG] Questions loaded:', loadedQuestions.length);
      setCurrentStage(InterviewStage.INTERVIEWING);
    } catch (error) {
      console.error('[ERROR] Failed to start interview:', error);
      alert('면접 시작에 실패했습니다.');
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  const handleEndInterview = () => {
    console.log('[DEBUG] Ending interview, changing stage to ANALYZING');
    setCurrentStage(InterviewStage.ANALYZING);
  };

  const handleAnalysisComplete = (results: AnalysisResults) => {
    console.log('[DEBUG] Analysis complete, changing stage to COMPLETE', results);
    setAnalysisResults(results);
    setCurrentStage(InterviewStage.COMPLETE);
  };

  return (
    <div className="flex h-screen bg-sidebar">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isSignLanguageMode={isSignLanguageMode}
        onSignLanguageToggle={() => setIsSignLanguageMode(!isSignLanguageMode)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-white relative z-10">
        {/* Header */}
        <Header stage={currentStage} />

        {/* Content Area - Different screens based on stage */}
        <AnimatePresence mode="wait">
          {currentStage === InterviewStage.WAITING && (
            <WaitingScreen
              key="waiting"
              onStart={handleStartInterview}
              isLoading={isLoadingQuestions}
            />
          )}
          {currentStage === InterviewStage.INTERVIEWING && (
            <InterviewingScreen
              key="interviewing"
              onEnd={handleEndInterview}
              questions={questions}
              sessionId={sessionId || ''}
            />
          )}
          {currentStage === InterviewStage.ANALYZING && (
            <AnalyzingScreen key="analyzing" onComplete={handleAnalysisComplete} />
          )}
          {currentStage === InterviewStage.COMPLETE && analysisResults && (
            <CompleteScreen key="complete" analysisResults={analysisResults} />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
