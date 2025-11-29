import React, { useState, useEffect } from 'react';
import { PlayIcon, StopIcon, Cog6ToothIcon } from '@heroicons/react/24/solid';
import { ScientificChart } from '../../components/common/ScientificChart';

// Mock data generator
const generateData = (points: number) => {
    return Array.from({ length: points }, (_, i) => ({
        time: (i * 0.1).toFixed(1),
        sensor1: Math.sin(i * 0.2) + Math.random() * 0.1,
        sensor2: Math.cos(i * 0.2) * 0.8 + Math.random() * 0.1,
        sensor3: Math.sin(i * 0.1) * 0.5 + Math.random() * 0.05,
    }));
};

export const AcquisitionPage: React.FC = () => {
    const [isAcquiring, setIsAcquiring] = useState(false);
    const [data, setData] = useState(generateData(50));

    useEffect(() => {
        let interval: any;
        if (isAcquiring) {
            interval = setInterval(() => {
                setData(prev => {
                    const lastTime = parseFloat(prev[prev.length - 1].time);
                    const newPoint = {
                        time: (lastTime + 0.1).toFixed(1),
                        sensor1: Math.sin(lastTime * 0.5) + Math.random() * 0.2,
                        sensor2: Math.cos(lastTime * 0.5) * 0.8 + Math.random() * 0.2,
                        sensor3: Math.sin(lastTime * 0.25) * 0.5 + Math.random() * 0.1,
                    };
                    return [...prev.slice(1), newPoint];
                });
            }, 100);
        }
        return () => clearInterval(interval);
    }, [isAcquiring]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700">
                <div>
                    <h1 className="text-xl font-bold text-gray-900 dark:text-white">Real-Time Acquisition</h1>
                    <p className="text-sm text-gray-500">Session ID: #ACQ-2023-001</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-slate-700 rounded-lg">
                        <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Rate:</span>
                        <span className="text-sm font-bold text-gray-900 dark:text-white">100 Hz</span>
                    </div>
                    <button
                        onClick={() => setIsAcquiring(!isAcquiring)}
                        className={`flex items-center gap-2 px-6 py-2 rounded-lg font-bold text-white transition-all ${isAcquiring
                            ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30'
                            : 'bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-500/30'
                            }`}
                    >
                        {isAcquiring ? (
                            <>
                                <StopIcon className="w-5 h-5" /> Stop
                            </>
                        ) : (
                            <>
                                <PlayIcon className="w-5 h-5" /> Start
                            </>
                        )}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <ScientificChart
                        title="Wave Height Sensors (Real-time)"
                        data={data}
                        xKey="time"
                        lines={[
                            { key: 'sensor1', color: '#0ea5e9', name: 'Probe 1 (m)' },
                            { key: 'sensor2', color: '#8b5cf6', name: 'Probe 2 (m)' },
                        ]}
                        height={400}
                    />
                    <ScientificChart
                        title="Reference Sensor"
                        data={data}
                        xKey="time"
                        lines={[
                            { key: 'sensor3', color: '#f59e0b', name: 'Reference (m)' },
                        ]}
                        height={250}
                    />
                </div>

                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-gray-900 dark:text-white">Channel Status</h3>
                            <Cog6ToothIcon className="w-5 h-5 text-gray-400 cursor-pointer hover:text-gray-600" />
                        </div>
                        <div className="space-y-3">
                            {[1, 2, 3, 4, 5, 6, 7, 8].map((ch) => (
                                <div key={ch} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${ch <= 3 ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-slate-600'}`}></div>
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Channel {ch}</span>
                                    </div>
                                    <span className="text-xs font-mono text-gray-500">
                                        {ch <= 3 ? (Math.random() * 2 - 1).toFixed(3) + ' V' : '--'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Acquisition Log</h3>
                        <div className="space-y-2 max-h-48 overflow-y-auto text-xs font-mono">
                            <div className="text-gray-500">[10:42:01] System initialized</div>
                            <div className="text-gray-500">[10:42:05] Connected to DAQ board</div>
                            <div className="text-emerald-600 dark:text-emerald-400">[10:42:10] Calibration verified</div>
                            {isAcquiring && <div className="text-blue-600 dark:text-blue-400 animate-pulse">[10:42:15] Recording started...</div>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
