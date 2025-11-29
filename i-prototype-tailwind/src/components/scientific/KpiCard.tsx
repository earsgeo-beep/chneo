import React from 'react';
import { MetrologicalValue } from './MetrologicalValue';
import { StatusBadge } from './StatusBadge';

interface KpiCardProps {
    title: string;
    subtitle?: string;
    value: number;
    uncertainty?: number;
    unit?: string;
    status?: 'ok' | 'warning' | 'error';
    metadata?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
    title,
    subtitle,
    value,
    uncertainty,
    unit,
    status = 'ok',
    metadata,
}) => {
    return (
        <div className="panel p-4 hover:border-primary-light transition-colors">
            <div className="flex justify-between items-start mb-2">
                <div>
                    <h3 className="text-lg font-bold text-text-primary">{title}</h3>
                    {subtitle && <p className="text-xs text-text-muted">{subtitle}</p>}
                </div>
                <StatusBadge status={status} className="px-2 py-0.5 text-[10px]" />
            </div>

            <div className="my-3">
                <MetrologicalValue
                    value={value}
                    uncertainty={uncertainty}
                    unit={unit}
                    className="text-xl"
                />
            </div>

            {metadata && (
                <div className="pt-2 mt-2 border-t border-border text-xs text-text-muted flex justify-between">
                    <span>Source:</span>
                    <span className="font-medium text-text-secondary">{metadata}</span>
                </div>
            )}
        </div>
    );
};
