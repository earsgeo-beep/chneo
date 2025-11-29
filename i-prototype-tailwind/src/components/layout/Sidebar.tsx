import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

interface SidebarProps {
    open: boolean;
}

const navigation = [
    { name: 'Tableau de bord', href: '/', icon: 'dashboard' },
    { type: 'separator', label: 'ACQUISITION' },
    { name: 'Configuration', href: '/acquisition/config', icon: 'settings' },
    { name: 'Temps Réel', href: '/acquisition/live', icon: 'activity' },
    { name: 'Sessions', href: '/acquisition/sessions', icon: 'folder' },
    { type: 'separator', label: 'ANALYSE' },
    { name: 'Spectrale (FFT)', href: '/analysis/spectral', icon: 'chart' },
    { name: 'Statistique (Goda)', href: '/analysis/goda', icon: 'stats' },
    { name: 'Réflexion (3 sondes)', href: '/analysis/reflection', icon: 'waves' },
    { type: 'separator', label: 'MÉTROLOGIE' },
    { name: 'Calibration', href: '/calibration', icon: 'calibrate' },
    { type: 'separator', label: 'DONNÉES' },
    { name: 'Export', href: '/export', icon: 'download' },
];

export function Sidebar({ open }: SidebarProps) {
    const location = useLocation();

    if (!open) return null;

    return (
        <aside
            className="fixed left-0 top-[var(--spacing-header)] bottom-[var(--spacing-statusbar)] bg-bg-panel border-r border-border overflow-y-auto"
            style={{ width: 'var(--spacing-sidebar)' }}
        >
            <nav className="p-2">
                {navigation.map((item, index) => {
                    if (item.type === 'separator') {
                        return (
                            <div key={index} className="mt-4 mb-2 px-3">
                                <span className="text-[10px] font-semibold tracking-wider text-text-muted">
                                    {item.label}
                                </span>
                            </div>
                        );
                    }

                    const isActive = location.pathname === item.href;

                    return (
                        <NavLink
                            key={item.href}
                            to={item.href!}
                            className={cn(
                                'flex items-center gap-2 px-3 py-2 rounded text-sm',
                                isActive
                                    ? 'bg-primary-light text-primary font-medium'
                                    : 'text-text-secondary hover:bg-bg-hover'
                            )}
                        >
                            <span className="w-4 h-4 text-xs flex items-center justify-center">●</span>
                            <span>{item.name}</span>
                        </NavLink>
                    );
                })}
            </nav>
        </aside>
    );
}
