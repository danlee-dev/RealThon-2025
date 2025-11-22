'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Bell,
  ChevronLeft,
  Mic,
  Volume2,
  PhoneOff,
  Video,
  Settings,
  Paperclip,
  Smile,
  HelpCircle,
  LayoutDashboard,
  Video as VideoIcon,
  Lightbulb,
  Users,
  MessageCircle,
  SettingsIcon,
  LogOut,
  ChevronRight,
  Hand
} from 'lucide-react';
import { ResponsiveRadar } from '@nivo/radar';
import { ResponsivePie } from '@nivo/pie';

export default function InterviewPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSignLanguageMode, setIsSignLanguageMode] = useState(false);

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
        <Header />

        {/* Content Area */}
        <div className="flex-1 flex gap-6 p-6 overflow-auto bg-light-grey">
          {/* Left Column - Video & Charts */}
          <div className="flex-[2] flex flex-col gap-6">
            {/* Video Section */}
            <VideoSection />

            {/* Charts Section */}
            <div className="grid grid-cols-2 gap-6">
              <AIVideoScoreChart />
              <WorkmapScoreChart />
            </div>
          </div>

          {/* Right Column - Scores & Chat */}
          <div className="flex-[1] flex flex-col gap-6">
            <ScoreCards />
            <ChatSection />
          </div>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ isCollapsed, onToggle, isSignLanguageMode, onSignLanguageToggle }: {
  isCollapsed: boolean,
  onToggle: () => void,
  isSignLanguageMode: boolean,
  onSignLanguageToggle: () => void
}) {
  const mainMenuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: false },
    { icon: VideoIcon, label: 'Interview', active: true },
    { icon: Lightbulb, label: 'Insight', active: false },
    { icon: Users, label: 'Talent', active: false },
  ];

  const generalItems = [
    { icon: SettingsIcon, label: 'Setting', active: false },
  ];

  return (
    <div className={`bg-sidebar text-white flex flex-col transition-all duration-300 relative ${isCollapsed ? 'w-20' : 'w-60'}`}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={`absolute top-1/2 -translate-y-1/2 z-20 w-8 h-16 flex items-center justify-center transition-all duration-300 ${
          isCollapsed
            ? '-right-4 bg-sidebar text-primary rounded-r-full'
            : '-right-4 bg-white text-gray-700 rounded-l-full shadow-lg'
        }`}
      >
        <ChevronRight className={`w-5 h-5 transition-transform ${isCollapsed ? '' : 'rotate-180'}`} />
      </button>

      {/* Logo */}
      <div className={`p-6 flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center flex-shrink-0">
          <VideoIcon className="w-5 h-5" />
        </div>
        {!isCollapsed && <span className="text-lg font-semibold">InterviewAI</span>}
      </div>

      {/* Main Menu */}
      <div className={`${isCollapsed ? 'px-2' : 'px-4'} mt-4`}>
        {!isCollapsed && <div className="text-xs text-gray-500 mb-3 px-3">Main Menu</div>}
        {mainMenuItems.map((item) => (
          <SidebarItem key={item.label} {...item} isCollapsed={isCollapsed} />
        ))}
      </div>

      {/* General */}
      <div className={`${isCollapsed ? 'px-2' : 'px-4'} mt-6`}>
        {!isCollapsed && <div className="text-xs text-gray-500 mb-3 px-3">General</div>}

        {/* Sign Language Mode Toggle */}
        <button
          onClick={onSignLanguageToggle}
          className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 rounded-xl mb-1 transition-all ${
            isSignLanguageMode
              ? 'bg-primary text-white shadow-lg'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
          title={isCollapsed ? 'Sign Language Mode' : ''}
        >
          {/* Custom Toggle Switch */}
          <div className="relative flex-shrink-0">
            <div className={`w-11 h-6 rounded-full transition-colors ${
              isSignLanguageMode ? 'bg-gray-400' : 'bg-gray-400'
            }`}>
              <div
                className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full transition-all duration-300 ${
                  isSignLanguageMode
                    ? 'translate-x-5'
                    : 'translate-x-0 bg-white'
                }`}
                style={isSignLanguageMode ? { backgroundColor: '#9A00ED' } : {}}
              />
            </div>
          </div>
          {!isCollapsed && <span>수화 모드</span>}
        </button>

        {generalItems.map((item) => (
          <SidebarItem key={item.label} {...item} isCollapsed={isCollapsed} />
        ))}
      </div>

      {/* Log Out */}
      <div className={`mt-auto ${isCollapsed ? 'p-2' : 'p-4'}`}>
        <button className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 text-gray-400 hover:text-white transition-colors rounded-xl hover:bg-white/5`}>
          <LogOut className="w-5 h-5" />
          {!isCollapsed && <span>Log Out</span>}
        </button>
      </div>
    </div>
  );
}

function SidebarItem({ icon: Icon, label, active, isCollapsed }: { icon: any, label: string, active: boolean, isCollapsed: boolean }) {
  return (
    <button
      className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 rounded-xl mb-1 transition-all ${
        active
          ? 'bg-primary text-white shadow-lg'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
      title={isCollapsed ? label : ''}
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      {!isCollapsed && <span>{label}</span>}
    </button>
  );
}

function Header() {
  return (
    <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-gray-100 rounded-full">
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Interview for UI/UX Designer</h1>
          <p className="text-sm text-gray-500">Sans Brother</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-gray-100 rounded-full relative">
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-200">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-semibold">
            ZM
          </div>
          <span className="text-sm font-medium">Zaim Maulana</span>
        </button>
      </div>
    </div>
  );
}

function VideoSection() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRecorderRef = useRef<MediaRecorder | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [volume, setVolume] = useState(75);
  const [isRecording, setIsRecording] = useState(false);
  const [isAudioRecording, setIsAudioRecording] = useState(false);
  const [questions, setQuestions] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [audioRecordings, setAudioRecordings] = useState<Blob[][]>([]);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const isDev = process.env.NODE_ENV === 'development';

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720 },
          audio: true
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error('Camera access error:', error);
        setCameraError('카메라 접근 권한이 필요합니다');
      }
    };

    startCamera();

    return () => {
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = () => {
    if (!videoRef.current?.srcObject) return;

    const stream = videoRef.current.srcObject as MediaStream;
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'video/webm;codecs=vp9'
    });

    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      downloadRecording(chunks);
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
    console.log('[DEBUG] Recording started');
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      console.log('[DEBUG] Recording stopped');
    }
  };

  const downloadRecording = (chunks: Blob[]) => {
    const blob = new Blob(chunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-recording-${Date.now()}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    console.log('[DEBUG] Recording saved');
  };

  const startAudioRecording = () => {
    if (!videoRef.current?.srcObject) return;

    const stream = videoRef.current.srcObject as MediaStream;
    const audioStream = new MediaStream(stream.getAudioTracks());

    const audioRecorder = new MediaRecorder(audioStream, {
      mimeType: 'audio/webm'
    });

    const chunks: Blob[] = [];

    audioRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    audioRecorder.onstop = () => {
      setAudioRecordings(prev => {
        const newRecordings = [...prev];
        newRecordings[currentQuestionIndex] = chunks;
        return newRecordings;
      });

      // 즉시 오디오 파일 다운로드
      const blob = new Blob(chunks, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `question-${currentQuestionIndex + 1}-audio-${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log(`[DEBUG] Question ${currentQuestionIndex + 1} audio saved and downloaded`);
    };

    audioRecorderRef.current = audioRecorder;
    audioRecorder.start();
    setIsAudioRecording(true);
    console.log(`[DEBUG] Recording answer for question ${currentQuestionIndex + 1}`);
  };

  const stopAudioRecording = () => {
    if (audioRecorderRef.current && isAudioRecording) {
      audioRecorderRef.current.stop();
      setIsAudioRecording(false);

      // 마지막 질문이면 녹화도 종료
      if (currentQuestionIndex === questions.length - 1) {
        console.log('[DEBUG] Last question completed, stopping video recording');
        stopRecording();
        sendAllRecordings();
      } else {
        setCurrentQuestionIndex(prev => prev + 1);
      }
    }
  };

  const sendAllRecordings = async () => {
    console.log('[DEBUG] Preparing to send all recordings to backend...');
    console.log('[DEBUG] Total questions:', questions.length);
    console.log('[DEBUG] Total audio recordings:', audioRecordings.length);

    // TODO: 실제 백엔드 API 호출
    // const formData = new FormData();
    // audioRecordings.forEach((chunks, index) => {
    //   const blob = new Blob(chunks, { type: 'audio/webm' });
    //   formData.append(`question_${index}`, blob, `question_${index}.webm`);
    // });
    // await fetch('/api/analyze-interview', { method: 'POST', body: formData });

    console.log('[DEBUG] All recordings would be sent to backend here');
  };

  const handleDebugUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log('[DEBUG] Video uploaded:', file.name);

      // Mock questions from backend
      const mockQuestions = [
        '자기소개를 해주세요.',
        '이 회사에 지원한 동기는 무엇인가요?',
        '본인의 강점과 약점을 말씀해주세요.',
        '5년 후 자신의 모습은 어떨 것 같나요?'
      ];

      setQuestions(mockQuestions);
      setCurrentQuestionIndex(0);
      setAudioRecordings([]);
      setInterviewStarted(true);

      console.log('[DEBUG] Starting interview with', mockQuestions.length, 'questions');
      console.log('[DEBUG] Auto-starting video recording...');
      startRecording();
    }
  };

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600">Digital Interview has Live</span>
        </div>
        <div className="flex items-center gap-3">
          {isRecording && (
            <div className="flex items-center gap-2 px-3 py-1 bg-red-100 rounded-full">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-red-600 font-medium">녹화 중</span>
            </div>
          )}
          {isDev && (
            <div className="flex items-center gap-2">
              {!isRecording ? (
                <label className="px-4 py-2 bg-blue-500 text-white text-sm rounded-lg cursor-pointer hover:bg-blue-600 transition-colors">
                  디버그: 영상 업로드
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleDebugUpload}
                    className="hidden"
                  />
                </label>
              ) : (
                <button
                  onClick={stopRecording}
                  className="px-4 py-2 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors"
                >
                  녹화 중지
                </button>
              )}
            </div>
          )}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span className="text-sm text-primary">Also joined in this call</span>
          </div>
        </div>
      </div>

      {/* Question and Recording Controls */}
      {interviewStarted && questions.length > 0 && (
        <div className="mb-4 p-4 bg-gradient-to-r from-primary/10 to-brand-purple-light/10 rounded-xl border-l-4 border-primary">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                  질문 {currentQuestionIndex + 1} / {questions.length}
                </span>
              </div>
              <p className="text-gray-900 font-medium text-lg">
                {questions[currentQuestionIndex]}
              </p>
            </div>
            <div className="ml-4">
              {!isAudioRecording ? (
                <button
                  onClick={startAudioRecording}
                  className="px-6 py-3 bg-primary text-white rounded-xl hover:bg-brand-purple transition-colors flex items-center gap-2 shadow-lg"
                >
                  <Mic className="w-5 h-5" />
                  <span>답변 녹음 시작</span>
                </button>
              ) : (
                <button
                  onClick={stopAudioRecording}
                  className="px-6 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors flex items-center gap-2 shadow-lg animate-pulse"
                >
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                  <span>녹음 중지</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Video Area */}
      <div className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video">
        {/* Main Video - Avatar Background */}
        <img
          src="/avatar.png"
          alt="Interview Avatar"
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* User Camera - Horizontal Card */}
        <div className="absolute top-4 right-4 w-64 h-36 bg-gray-800 rounded-xl overflow-hidden shadow-lg border-2 border-gray-700">
          {cameraError ? (
            <div className="w-full h-full flex items-center justify-center text-white text-xs p-4 text-center">
              <span>{cameraError}</span>
            </div>
          ) : (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
          )}
        </div>

        {/* Volume Slider */}
        <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-3">
          <div className="bg-gray-800/80 backdrop-blur-sm rounded-full p-3 shadow-lg">
            <Volume2 className="w-5 h-5 text-white" />
          </div>
          <div
            className="relative h-32 w-6 bg-gray-700 rounded-full overflow-hidden cursor-pointer"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const y = e.clientY - rect.top;
              const newVolume = Math.max(0, Math.min(100, 100 - (y / rect.height) * 100));
              setVolume(Math.round(newVolume));
            }}
          >
            <div
              className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-primary to-brand-purple-light rounded-full transition-all duration-150"
              style={{ height: `${volume}%` }}
            ></div>
          </div>
        </div>

        {/* Controls */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4">
          <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
            <Mic className="w-5 h-5" />
          </button>
          <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
            <Volume2 className="w-5 h-5" />
          </button>
          <button className="w-14 h-14 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white">
            <PhoneOff className="w-6 h-6" />
          </button>
          <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
            <Video className="w-5 h-5" />
          </button>
          <button className="w-12 h-12 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Caption */}
      <div className="mt-4 flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
        <div className="flex gap-0.5 mt-1">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="w-1 h-4 bg-primary rounded-full animate-pulse" style={{ animationDelay: `${i * 0.1}s` }}></div>
          ))}
        </div>
        <p className="text-sm text-gray-700">
          <span className="font-medium">Conversation now:</span> Your resume is amazing richard, next tell me why you choose this company?
        </p>
      </div>
    </div>
  );
}

function AIVideoScoreChart() {
  const data = [
    { skill: 'Professionalism', value: 75 },
    { skill: 'Attitude', value: 80 },
    { skill: 'Creativity', value: 70 },
    { skill: 'Communication', value: 85 },
    { skill: 'Leadership', value: 65 },
    { skill: 'Teamwork', value: 75 },
    { skill: 'Sociability', value: 80 },
  ];

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">AI Video Score</h3>
        <HelpCircle className="w-5 h-5 text-gray-400" />
      </div>
      <p className="text-xs text-gray-500 mb-6">Based on Accurate Value from Video</p>
      <div className="h-64">
        <ResponsiveRadar
          data={data}
          keys={['value']}
          indexBy="skill"
          maxValue={100}
          margin={{ top: 40, right: 60, bottom: 40, left: 60 }}
          borderColor={{ from: 'color' }}
          gridLabelOffset={16}
          dotSize={8}
          dotColor={{ theme: 'background' }}
          dotBorderWidth={2}
          colors={['#7C5CFC']}
          fillOpacity={0.25}
          blendMode="multiply"
          animate={true}
          motionConfig="gentle"
        />
      </div>
    </div>
  );
}

function WorkmapScoreChart() {
  const scores = [
    { label: 'Presentation', value: 90, color: '#7C5CFC' },
    { label: 'Opportunistic', value: 60, color: '#FF8D68' },
    { label: 'Business Acumen', value: 85, color: '#7C5CFC' },
    { label: 'Closing Technique', value: 40, color: '#FF8D68' },
  ];

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Workmap Score</h3>
        <HelpCircle className="w-5 h-5 text-gray-400" />
      </div>
      <p className="text-xs text-gray-500 mb-6">Based on Accurate Value from Video</p>
      <div className="space-y-4">
        {scores.map((score) => (
          <div key={score.label}>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-700">{score.label}</span>
              <span className="font-semibold">{score.value}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${score.value}%`,
                  backgroundColor: score.color
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScoreCards() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <ScoreCard
        title="AI Video Score"
        score={80}
        color="#7C5CFC"
      />
      <ScoreCard
        title="Workmap Score"
        score={75}
        color="#FF8D68"
      />
    </div>
  );
}

function ScoreCard({ title, score, color }: { title: string, score: number, color: string }) {
  const data = [
    { id: 'score', value: score },
    { id: 'remaining', value: 100 - score },
  ];

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">
      <div className="h-32 relative">
        <ResponsivePie
          data={data}
          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
          innerRadius={0.7}
          padAngle={0}
          cornerRadius={0}
          colors={[color, '#F0F0F0']}
          enableArcLinkLabels={false}
          enableArcLabels={false}
          isInteractive={false}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold" style={{ color }}>{score}%</div>
          </div>
        </div>
      </div>
      <p className="text-sm text-gray-700 text-center mt-2">{title}</p>
    </div>
  );
}

function ChatSection() {
  const messages = [
    {
      id: 1,
      sender: 'Richard Gomez',
      avatar: 'RG',
      message: 'Hello everyone, Good Morning :)',
      time: '08:42 AM',
      isMe: false,
    },
    {
      id: 2,
      sender: 'You',
      message: 'Hi Richard, Goodmorning too. Let\'s start this interview yourself!',
      time: '08:43 AM',
      isMe: true,
    },
    {
      id: 3,
      type: 'system',
      message: 'We announce that you accepted this call',
    },
    {
      id: 4,
      sender: 'Richard Gomez',
      avatar: 'RG',
      message: 'Why you choose this company?',
      time: '08:45 AM',
      isMe: false,
    },
  ];

  return (
    <div className="bg-white rounded-3xl shadow-sm flex-1 flex flex-col overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-100">
        <button className="flex-1 py-4 text-sm font-medium text-white bg-primary rounded-tl-3xl">
          Chat
        </button>
        <button className="flex-1 py-4 text-sm font-medium text-gray-500 hover:text-gray-700">
          Participant
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => {
          if (msg.type === 'system') {
            return (
              <div key={msg.id} className="flex justify-center">
                <p className="text-xs text-gray-500 bg-gray-100 px-4 py-2 rounded-full">
                  {msg.message}
                </p>
              </div>
            );
          }

          return (
            <div key={msg.id} className={`flex gap-3 ${msg.isMe ? 'flex-row-reverse' : ''}`}>
              {!msg.isMe && (
                <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold flex-shrink-0">
                  {msg.avatar}
                </div>
              )}
              <div className={`flex-1 ${msg.isMe ? 'flex flex-col items-end' : ''}`}>
                {!msg.isMe && (
                  <p className="text-sm font-medium text-gray-900 mb-1">{msg.sender}</p>
                )}
                <div className={`inline-block px-4 py-2 rounded-2xl ${
                  msg.isMe
                    ? 'bg-primary text-white rounded-tr-none'
                    : 'bg-gray-100 text-gray-900 rounded-tl-none'
                }`}>
                  <p className="text-sm">{msg.message}</p>
                </div>
                <p className="text-xs text-gray-400 mt-1">{msg.time}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3 bg-gray-50 rounded-full px-4 py-3">
          <button className="text-gray-400 hover:text-gray-600">
            <Paperclip className="w-5 h-5" />
          </button>
          <input
            type="text"
            placeholder="Type a message..."
            className="flex-1 bg-transparent outline-none text-sm"
          />
          <button className="text-gray-400 hover:text-gray-600">
            <Smile className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
