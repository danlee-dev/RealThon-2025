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

export default function InterviewPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSignLanguageMode, setIsSignLanguageMode] = useState(false);
  const [currentStage, setCurrentStage] = useState<InterviewStage>(InterviewStage.WAITING);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);

  const handleStartInterview = () => {
    console.log('[DEBUG] Starting interview, changing stage to INTERVIEWING');
    setCurrentStage(InterviewStage.INTERVIEWING);
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
            <WaitingScreen key="waiting" onStart={handleStartInterview} />
          )}
          {currentStage === InterviewStage.INTERVIEWING && (
            <InterviewingScreen key="interviewing" onEnd={handleEndInterview} />
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
