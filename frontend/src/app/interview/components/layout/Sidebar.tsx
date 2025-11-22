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
    activeItem?: string;
}

export default function Sidebar({
    isCollapsed,
    onToggle,
    isSignLanguageMode,
    onSignLanguageToggle,
    activeItem = 'Interview'
}: SidebarProps) {
    const router = useRouter();

    const handleLogout = () => {
        authApi.logout();
        router.push('/login');
    };

    const mainMenuItems = [
        { icon: LayoutDashboard, label: 'Dashboard' },
        { icon: VideoIcon, label: 'Interview' },
        { icon: Lightbulb, label: 'Insight' },
        { icon: Users, label: 'Talent' },
    ];

    const generalItems = [
        { icon: SettingsIcon, label: 'Setting' },
    ];

    return (
        <div className={`bg-sidebar text-white flex flex-col transition-all duration-300 relative ${isCollapsed ? 'w-20' : 'w-60'}`}>
            {/* Logo */}
            <div className={`p-6 flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
                <div className="w-10 h-10 flex items-center justify-center flex-shrink-0">
                    <svg width="40" height="40" viewBox="0 0 70 70" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M35 15C45.4934 15 54 23.7304 54 34.5C54 38.8009 52.6419 42.7757 50.3438 46H19.6562C17.3581 42.7757 16 38.8009 16 34.5C16 23.7304 24.5066 15 35 15Z" fill="#FF4D12"/>
                        <path fillRule="evenodd" clipRule="evenodd" d="M12.396 55.4165C12.396 54.8363 12.6265 54.2799 13.0367 53.8697C13.4469 53.4595 14.0033 53.229 14.5835 53.229H55.4168C55.997 53.229 56.5534 53.4595 56.9636 53.8697C57.3739 54.2799 57.6043 54.8363 57.6043 55.4165C57.6043 55.9967 57.3739 56.5531 56.9636 56.9633C56.5534 57.3735 55.997 57.604 55.4168 57.604H14.5835C14.0033 57.604 13.4469 57.3735 13.0367 56.9633C12.6265 56.5531 12.396 55.9967 12.396 55.4165ZM21.146 64.1665C21.146 63.5863 21.3765 63.0299 21.7867 62.6197C22.1969 62.2095 22.7533 61.979 23.3335 61.979H46.6668C47.247 61.979 47.8034 62.2095 48.2136 62.6197C48.6239 63.0299 48.8543 63.5863 48.8543 64.1665C48.8543 64.7467 48.6239 65.3031 48.2136 65.7133C47.8034 66.1235 47.247 66.354 46.6668 66.354H23.3335C22.7533 66.354 22.1969 66.1235 21.7867 65.7133C21.3765 65.3031 21.146 64.7467 21.146 64.1665Z" fill="#FFDA8F"/>
                        <path fillRule="evenodd" clipRule="evenodd" d="M35.0002 3.646C35.5803 3.646 36.1367 3.87646 36.547 4.2867C36.9572 4.69694 37.1877 5.25333 37.1877 5.8335V8.75016C37.1877 9.33032 36.9572 9.88672 36.547 10.297C36.1367 10.7072 35.5803 10.9377 35.0002 10.9377C34.42 10.9377 33.8636 10.7072 33.4534 10.297C33.0431 9.88672 32.8127 9.33032 32.8127 8.75016V5.8335C32.8127 5.25333 33.0431 4.69694 33.4534 4.2867C33.8636 3.87646 34.42 3.646 35.0002 3.646ZM12.8306 12.8306C13.2407 12.4209 13.7967 12.1908 14.3764 12.1908C14.9561 12.1908 15.5121 12.4209 15.9222 12.8306L17.0685 13.9739C17.4672 14.3863 17.6879 14.9388 17.6832 15.5123C17.6785 16.0859 17.4487 16.6346 17.0433 17.0404C16.6379 17.4462 16.0894 17.6765 15.5158 17.6818C14.9423 17.687 14.3896 17.4668 13.9768 17.0685L12.8306 15.9222C12.4209 15.5121 12.1908 14.9561 12.1908 14.3764C12.1908 13.7967 12.4209 13.2407 12.8306 12.8306ZM57.1697 12.8306C57.5794 13.2407 57.8095 13.7967 57.8095 14.3764C57.8095 14.9561 57.5794 15.5121 57.1697 15.9222L56.0235 17.0685C55.6088 17.4549 55.0604 17.6653 54.4936 17.6553C53.9269 17.6453 53.3862 17.4157 52.9854 17.0149C52.5846 16.6141 52.3551 16.0734 52.3451 15.5067C52.3351 14.94 52.5454 14.3915 52.9318 13.9768L54.0781 12.8306C54.4882 12.4209 55.0442 12.1908 55.6239 12.1908C56.2036 12.1908 56.7596 12.4209 57.1697 12.8306ZM3.646 35.0002C3.646 34.42 3.87646 33.8636 4.2867 33.4534C4.69694 33.0431 5.25334 32.8127 5.8335 32.8127H8.75016C9.33032 32.8127 9.88672 33.0431 10.297 33.4534C10.7072 33.8636 10.9377 34.42 10.9377 35.0002C10.9377 35.5803 10.7072 36.1367 10.297 36.547C9.88672 36.9572 9.33032 37.1877 8.75016 37.1877H5.8335C5.25334 37.1877 4.69694 36.9572 4.2867 36.547C3.87646 36.1367 3.646 35.5803 3.646 35.0002ZM59.0627 35.0002C59.0627 34.42 59.2931 33.8636 59.7034 33.4534C60.1136 33.0431 60.67 32.8127 61.2502 32.8127H64.1668C64.747 32.8127 65.3034 33.0431 65.7136 33.4534C66.1239 33.8636 66.3543 34.42 66.3543 35.0002C66.3543 35.5803 66.1239 36.1367 65.7136 36.547C65.3034 36.9572 64.747 37.1877 64.1668 37.1877H61.2502C60.67 37.1877 60.1136 36.9572 59.7034 36.547C59.2931 36.1367 59.0627 35.5803 59.0627 35.0002Z" fill="#FF4D12"/>
                        <line x1="6" y1="47" x2="64" y2="47" stroke="#FF8C00" strokeWidth="4" strokeLinecap="round"/>
                    </svg>
                </div>
                {!isCollapsed && <span className="text-xl font-extrabold text-white">내일면접</span>}
            </div>

            {/* Main Menu */}
            <div className={`${isCollapsed ? 'px-2' : 'px-4'} mt-4`}>
                {!isCollapsed && <div className="text-xs text-gray-500 mb-3 px-3">Main Menu</div>}
                {mainMenuItems.map((item) => (
                    <SidebarItem 
                        key={item.label} 
                        {...item} 
                        active={item.label === activeItem}
                        isCollapsed={isCollapsed} 
                    />
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
                    <SidebarItem 
                        key={item.label} 
                        {...item} 
                        active={item.label === activeItem}
                        isCollapsed={isCollapsed} 
                    />
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
