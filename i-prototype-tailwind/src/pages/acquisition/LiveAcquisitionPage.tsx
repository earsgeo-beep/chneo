import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { ChannelIndicator, StatusBadge, RealtimeOscilloscope } from '@/components/scientific';

type AcquisitionState = 'idle' | 'running' | 'paused';

export function LiveAcquisitionPage() {
    const [status, setStatus] = useState<AcquisitionState>('idle');
    const [elapsed, setElapsed] = useState(0);
    const [samples, setSamples] = useState(0);
    const [oscData, setOscData] = useState<number[][]>(Array(8).fill([]));

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (status === 'running') {
            interval = setInterval(() => {
                setElapsed(e => e + 1);
                setSamples(s => s + 100);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [status]);

    useEffect(() => {
        if (status !== 'running') return;

        const interval = setInterval(() => {
            setOscData(prev => {
                const newData = prev.map((channelData, i) => {
                    // Generate sine waves with different frequencies/phases
                    const t = Date.now() / 1000;
                    const val = Math.sin(t * 2 * Math.PI * (0.5 + i * 0.1)) * 0.5 + (Math.random() - 0.5) * 0.05;
                    const newChannel = [...channelData, val];
                    if (newChannel.length > 500) newChannel.shift(); // Keep buffer size manageable
                    return newChannel;
                });
                return newData;
            });
        }, 50); // 20Hz update

        return () => clearInterval(interval);
    }, [status]);

    const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const handleStart = () => setStatus('running');
    const handleStop = () => setStatus('idle');

    return (
        <div className="h-full flex flex-col gap-4">
            {/* Header Controls */}
            <div className="flex items-center justify-between bg-bg-panel p-4 rounded-lg border border-border shadow-sm">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3">
                        <StatusBadge status={status} />
                        <div className="flex flex-col">
                            <span className="text-xs text-text-secondary uppercase tracking-wider">Temps Écoulé</span>
                            <span className="font-mono text-xl font-bold text-text-primary">{formatTime(elapsed)}</span>
                        </div>
                    </div>
                    <div className="h-8 w-px bg-border"></div>
                    <div className="flex flex-col">
                        <span className="text-xs text-text-secondary uppercase tracking-wider">Échantillons</span>
                        <span className="font-mono text-xl font-bold text-text-primary">{samples.toLocaleString()}</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {status === 'idle' || status === 'paused' ? (
                        <Button
                            variant="primary"
                            onClick={handleStart}
                            className="min-w-[120px]"
                        >
                            ▶ Démarrer
                        </Button>
                    ) : (
                        <Button
                            variant="secondary"
                            onClick={handleStop}
                            className="min-w-[120px] border-error text-error hover:bg-error/10"
                        >
                            ⏹ Arrêter
                        </Button>
                    )}
                    <Button variant="secondary">⚙ Config</Button>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
                {/* Left: Channels Status */}
                <div className="col-span-3 flex flex-col gap-4 overflow-y-auto pr-2">
                    {Array.from({ length: 8 }).map((_, i) => {
                        const val = status === 'running' ? (Math.random() * 2 - 1) : 0;
                        return (
                            <ChannelIndicator
                                key={i}
                                channel={i + 1}
                                name={`Sonde ${i + 1}`}
                                value={val}
                                level={Math.abs(val) * 50 + 50}
                                status={status === 'running' ? 'ok' : 'off'}
                            />
                        );
                    })}
                </div>

                {/* Right: Real-time Graph */}
                <div className="col-span-9 bg-bg-panel rounded-lg border border-border p-4 flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-medium text-text-primary">Visualisation Temps Réel</h3>
                        <div className="flex gap-2">
                            <select className="h-8 text-xs border border-border rounded px-2 bg-bg-app">
                                <option>8 Canaux</option>
                                <option>4 Canaux</option>
                                <option>1 Canal</option>
                            </select>
                            <select className="h-8 text-xs border border-border rounded px-2 bg-bg-app">
                                <option>5s</option>
                                <option>10s</option>
                                <option>30s</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex-1 relative min-h-0">
                        <RealtimeOscilloscope data={oscData} />
                    </div>
                </div>
            </div>
        </div>
    );
}
