import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';

export function AppLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    return (
        <div className="h-screen flex flex-col overflow-hidden bg-bg-app font-sans">
            {/* Header */}
            <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

            {/* Main Area */}
            <div className="flex-1 flex overflow-hidden relative" style={{ marginBottom: 'var(--spacing-statusbar)' }}>
                {/* Sidebar */}
                <Sidebar open={sidebarOpen} />

                {/* Content */}
                <main
                    className="flex-1 overflow-auto transition-all duration-200"
                    style={{ marginLeft: sidebarOpen ? 'var(--spacing-sidebar)' : '0' }}
                >
                    <div className="p-6 max-w-[1600px] mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>

            {/* Status Bar */}
            <StatusBar />
        </div>
    );
}
