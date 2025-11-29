import React from 'react';
import { cn } from '@/lib/utils';

interface ChannelIndicatorProps {
    channel: number;
    name: string;
    value: number;
    unit?: string;
    level: number; // 0-100%
    status: 'ok' | 'warning' | 'saturated' | 'error' | 'off';
}

export const ChannelIndicator: React.FC<ChannelIndicatorProps> = ({
    channel,
    name,
    value,
    unit = 'V',
    level,
    status,
}) => {
    const getStatusColor = (s: string) => {
        switch (s) {
            case 'ok': return 'bg-success';
            case 'warning': return 'bg-warning';
            case 'saturated': return 'bg-error';
            case 'error': return 'bg-error';
            default: return 'bg-slate-300';
        }
    };

    return (
        <div className={cn(
            "border rounded p-2 flex flex-col gap-2 transition-colors",
            status === 'off' ? 'bg-bg-subtle border-border' : 'bg-white border-border hover:border-primary-light'
        )}>
            <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-text-secondary">CH {channel}</span>
                <div className={cn("w-2 h-2 rounded-full", getStatusColor(status))} />
            </div>

            <div className="font-mono text-sm font-bold text-center text-text-primary">
                {status === 'off' ? '--' : value.toFixed(3)}
                <span className="text-xs font-normal text-text-muted ml-1">{unit}</span>
            </div>

            <div className="h-1.5 w-full bg-bg-subtle rounded-full overflow-hidden">
                <div
                    className={cn("h-full transition-all duration-300", getStatusColor(status))}
                    style={{ width: `${Math.min(level, 100)}%` }}
                />
            </div>

            <div className="text-[10px] text-text-muted truncate text-center">
                {name}
            </div>
        </div>
    );
};
