'use client';

import { useState } from 'react';
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
  ChevronRight
} from 'lucide-react';
import { ResponsiveRadar } from '@nivo/radar';
import { ResponsivePie } from '@nivo/pie';

export default function InterviewPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-sidebar">
      {/* Sidebar */}
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden rounded-l-3xl bg-white relative z-10" style={{ boxShadow: '-16px 0 40px rgba(255, 255, 255, 0.15), -8px 0 20px rgba(255, 255, 255, 0.1), -4px 0 8px rgba(255, 255, 255, 0.05)' }}>
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

function Sidebar({ isCollapsed, onToggle }: { isCollapsed: boolean, onToggle: () => void }) {
  const mainMenuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: false },
    { icon: VideoIcon, label: 'Interview', active: true },
    { icon: Lightbulb, label: 'Insight', active: false },
    { icon: Users, label: 'Talent', active: false },
  ];

  const generalItems = [
    { icon: MessageCircle, label: 'FAQ', active: false },
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
  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600">Digital Interview has Live</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
          <span className="text-sm text-primary">Also joined in this call</span>
        </div>
      </div>

      {/* Video Area */}
      <div className="relative bg-gray-900 rounded-2xl overflow-hidden aspect-video">
        {/* Main Video - Richard Gomez */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white text-center">
            <div className="w-32 h-32 bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-4xl">RG</span>
            </div>
            <p className="text-lg font-medium">Richard Gomez</p>
          </div>
        </div>

        {/* PIP Videos */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <div className="w-24 h-32 bg-gray-800 rounded-xl overflow-hidden">
            <div className="w-full h-full flex items-center justify-center text-white text-xs">
              <span>Interviewer 1</span>
            </div>
          </div>
          <div className="w-24 h-32 bg-gray-800 rounded-xl overflow-hidden">
            <div className="w-full h-full flex items-center justify-center text-white text-xs">
              <span>Interviewer 2</span>
            </div>
          </div>
        </div>

        {/* Volume Slider */}
        <div className="absolute left-4 bottom-20 flex flex-col items-center gap-2">
          <input
            type="range"
            className="w-24 -rotate-90 origin-center"
            style={{ transform: 'rotate(-90deg) translateY(-40px)' }}
          />
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
