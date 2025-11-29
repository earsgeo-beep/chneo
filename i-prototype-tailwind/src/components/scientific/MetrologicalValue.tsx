import React from 'react';
import { cn } from '@/lib/utils';

interface MetrologicalValueProps {
    value: number;
    uncertainty?: number;
    unit?: string;
    label?: string;
    className?: string;
    precision?: number;
}

export const MetrologicalValue: React.FC<MetrologicalValueProps> = ({
    value,
    uncertainty,
    unit,
    label,
    className,
    precision = 3,
}) => {
    return (
        <div className={cn('flex items-baseline gap-2', className)}>
            {label && <span className="text-sm text-text-secondary mr-1">{label} =</span>}
            <span className="font-mono">
                <span className="font-bold text-black text-lg">
                    {value.toFixed(precision)}
                </span>
                {uncertainty !== undefined && (
                    <span className="text-text-secondary ml-2 text-sm">
                        ± {uncertainty.toFixed(precision)}
                    </span>
                )}
                {unit && <span className="text-text-muted ml-1 text-sm">{unit}</span>}
            </span>
        </div>
    );
};
