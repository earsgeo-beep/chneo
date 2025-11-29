import React from 'react';
import { cn } from '@/lib/utils';

type StatusType = 'idle' | 'running' | 'paused' | 'error' | 'completed' | 'ok' | 'warning' | 'off';

interface StatusBadgeProps {
    status: StatusType;
    label?: string;
    className?: string;
}

const statusConfig: Record<StatusType, { color: string; icon: string; label: string }> = {
    idle: { color: 'bg-slate-400', icon: '○', label: 'IDLE' },
    running: { color: 'bg-success', icon: '●', label: 'EN COURS' },
    paused: { color: 'bg-warning', icon: '◐', label: 'PAUSE' },
    error: { color: 'bg-error', icon: '✕', label: 'ERREUR' },
    completed: { color: 'bg-primary', icon: '✓', label: 'TERMINÉ' },
    ok: { color: 'bg-success', icon: '●', label: 'OK' },
    warning: { color: 'bg-warning', icon: '⚠', label: 'ATTENTION' },
    off: { color: 'bg-slate-300', icon: '○', label: 'OFF' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className }) => {
    const config = statusConfig[status];

    return (
        <div className={cn('inline-flex items-center gap-2 px-3 py-1 rounded bg-bg-subtle border border-border', className)}>
            <span className={cn('w-2 h-2 rounded-full', config.color)}></span>
            <span className="text-xs font-bold text-text-secondary uppercase tracking-wide">
                {label || config.label}
            </span>
        </div>
    );
};
