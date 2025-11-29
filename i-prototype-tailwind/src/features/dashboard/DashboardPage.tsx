import React from 'react';
import {
    ServerIcon,
    SignalIcon,
    ClockIcon,
    CpuChipIcon
} from '@heroicons/react/24/outline';

const MetricCard = ({ title, value, subtext, icon: Icon, colorClass }: any) => (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-slate-700 transition-all hover:shadow-md">
        <div className="flex items-start justify-between">
            <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{value}</h3>
                <p className="text-xs text-gray-400 mt-1">{subtext}</p>
            </div>
            <div className={`p-3 rounded-lg ${colorClass} bg-opacity-10`}>
                <Icon className={`w-6 h-6 ${colorClass.replace('bg-', 'text-')}`} />
            </div>
        </div>
    </div>
);

export const DashboardPage: React.FC = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">System Overview</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Real-time monitoring and control center</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors">
                        Export Report
                    </button>
                    <button className="px-4 py-2 bg-maritime-blue text-white rounded-lg text-sm font-medium hover:bg-blue-800 transition-colors shadow-sm shadow-blue-900/20">
                        New Project
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    title="System Status"
                    value="Operational"
                    subtext="All systems nominal"
                    icon={ServerIcon}
                    colorClass="bg-emerald-500 text-emerald-600"
                />
                <MetricCard
                    title="Active Sensors"
                    value="16 / 16"
                    subtext="100% Signal Quality"
                    icon={SignalIcon}
                    colorClass="bg-blue-500 text-blue-600"
                />
                <MetricCard
                    title="Uptime"
                    value="24h 12m"
                    subtext="Since last calibration"
                    icon={ClockIcon}
                    colorClass="bg-amber-500 text-amber-600"
                />
                <MetricCard
                    title="CPU Load"
                    value="12%"
                    subtext="Optimal performance"
                    icon={CpuChipIcon}
                    colorClass="bg-purple-500 text-purple-600"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700 p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
                        <button className="text-sm text-maritime-blue hover:underline">View All</button>
                    </div>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-900/50 rounded-lg border border-gray-100 dark:border-slate-800">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">
                                        P{i}
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">Wave Spectrum Analysis #{100 + i}</h4>
                                        <p className="text-xs text-gray-500">Completed 2 hours ago • Duration: 45m</p>
                                    </div>
                                </div>
                                <span className="px-3 py-1 text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                                    Completed
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Quick Actions</h3>
                    <div className="space-y-3">
                        <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors text-left">
                            <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                                <SignalIcon className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">Start Acquisition</p>
                                <p className="text-xs text-gray-500">Begin new data recording</p>
                            </div>
                        </button>
                        <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors text-left">
                            <div className="p-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-amber-600 dark:text-amber-400">
                                <ClockIcon className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">Calibrate Sensors</p>
                                <p className="text-xs text-gray-500">Check probe accuracy</p>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
