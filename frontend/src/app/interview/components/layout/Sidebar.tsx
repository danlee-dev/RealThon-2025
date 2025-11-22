'use client';

import { useRouter } from 'next/navigation';
import {
    LayoutDashboard,
    Video as VideoIcon,
    Lightbulb,
    Users,
    SettingsIcon,
    LogOut,
    ChevronRight,
} from 'lucide-react';
import { authApi } from '@/lib/auth-client';

interface SidebarProps {
    isCollapsed: boolean;
    onToggle: () => void;
    isSignLanguageMode: boolean;
    onSignLanguageToggle: () => void;
}

export default function Sidebar({
    isCollapsed,
    onToggle,
    isSignLanguageMode,
    onSignLanguageToggle
}: SidebarProps) {
    const router = useRouter();

    const handleLogout = () => {
        authApi.logout();
        router.push('/login');
    };

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
                    className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 rounded-xl mb-1 transition-all ${isSignLanguageMode
                        ? 'bg-primary text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                        }`}
                    title={isCollapsed ? 'Sign Language Mode' : ''}
                >
                    {/* Custom Toggle Switch */}
                    <div className="relative flex-shrink-0">
                        <div className={`w-11 h-6 rounded-full transition-colors ${isSignLanguageMode ? 'bg-gray-400' : 'bg-gray-400'
                            }`}>
                            <div
                                className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full transition-all duration-300 ${isSignLanguageMode
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

            {/* Footer */}
            <div className={`mt-auto ${isCollapsed ? 'p-2' : 'p-4'} space-y-2`}>
                <button
                    onClick={handleLogout}
                    className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 text-gray-400 hover:text-white transition-colors rounded-xl hover:bg-white/5`}
                >
                    <LogOut className="w-5 h-5" />
                    {!isCollapsed && <span>Log Out</span>}
                </button>

                <button 
                    onClick={onToggle}
                    className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 text-gray-400 hover:text-white transition-colors rounded-xl hover:bg-white/5`}
                >
                    <ChevronRight className={`w-5 h-5 transition-transform duration-300 ${isCollapsed ? '' : 'rotate-180'}`} />
                    {!isCollapsed && <span>접기</span>}
                </button>
            </div>
        </div>
    );
}

function SidebarItem({ icon: Icon, label, active, isCollapsed }: { icon: any, label: string, active: boolean, isCollapsed: boolean }) {
    return (
        <button
            className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-3 py-2.5 rounded-xl mb-1 transition-all ${active
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
