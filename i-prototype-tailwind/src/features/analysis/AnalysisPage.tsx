import React from 'react';
import { ScientificChart } from '../../components/common/ScientificChart';

const spectrumData = Array.from({ length: 50 }, (_, i) => ({
    freq: (i * 0.1).toFixed(1),
    energy: Math.exp(-(i - 20) * (i - 20) / 50) * 10 + Math.random() * 0.5,
}));

export const AnalysisPage: React.FC = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Data Analysis</h1>
                <div className="flex gap-2">
                    <select className="px-3 py-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-sm">
                        <option>Last Session</option>
                        <option>Session #ACQ-001</option>
                    </select>
                    <button className="px-4 py-2 bg-maritime-blue text-white rounded-lg text-sm font-medium">
                        Run Analysis
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ScientificChart
                    title="Power Spectral Density (JONSWAP)"
                    data={spectrumData}
                    xKey="freq"
                    lines={[
                        { key: 'energy', color: '#ef4444', name: 'Energy (m²/Hz)' },
                    ]}
                    height={350}
                />

                <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-slate-700">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Statistical Summary</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-gray-50 dark:bg-slate-900/50 rounded-lg">
                            <p className="text-xs text-gray-500">Significant Wave Height (Hs)</p>
                            <p className="text-xl font-bold text-maritime-blue">2.45 m</p>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-slate-900/50 rounded-lg">
                            <p className="text-xs text-gray-500">Peak Period (Tp)</p>
                            <p className="text-xl font-bold text-wave-teal">12.4 s</p>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-slate-900/50 rounded-lg">
                            <p className="text-xs text-gray-500">Zero-Crossing Period (Tz)</p>
                            <p className="text-xl font-bold text-gray-700 dark:text-gray-300">8.2 s</p>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-slate-900/50 rounded-lg">
                            <p className="text-xs text-gray-500">Spectral Width</p>
                            <p className="text-xl font-bold text-gray-700 dark:text-gray-300">0.42</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
