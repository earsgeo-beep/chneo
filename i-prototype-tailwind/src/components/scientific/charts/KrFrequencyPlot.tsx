import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';

interface KrFrequencyPlotProps {
    data?: { f: number; Kr: number }[];
}

export function KrFrequencyPlot({ data }: KrFrequencyPlotProps) {
    // Demo data
    const chartData = data || Array.from({ length: 50 }, (_, i) => {
        const f = 0.5 + i * 0.05;
        // Random Kr around 0.35
        const Kr = 0.35 + (Math.random() - 0.5) * 0.1 + Math.sin(f * 5) * 0.05;
        return { f, Kr: Math.max(0, Math.min(1, Kr)) };
    });

    const meanKr = chartData.reduce((acc, curr) => acc + curr.Kr, 0) / chartData.length;

    return (
        <div className="w-full h-full min-h-[200px] font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                    <XAxis
                        dataKey="f"
                        type="number"
                        domain={['auto', 'auto']}
                        tickFormatter={(val) => val.toFixed(1)}
                        label={{ value: 'Fréquence (Hz)', position: 'insideBottomRight', offset: -5 }}
                    />
                    <YAxis
                        domain={[0, 1]}
                        label={{ value: 'Kr [-]', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', fontSize: '12px' }}
                        formatter={(value: number) => [value.toFixed(3), 'Kr']}
                        labelFormatter={(label) => `f = ${Number(label).toFixed(2)} Hz`}
                    />
                    <ReferenceLine y={meanKr} stroke="#94A3B8" strokeDasharray="3 3" label={{ value: 'Moyenne', position: 'right', fontSize: 10, fill: '#64748B' }} />
                    <Line
                        type="monotone"
                        dataKey="Kr"
                        stroke="#0066CC"
                        strokeWidth={2}
                        dot={{ r: 2, fill: '#0066CC' }}
                        activeDot={{ r: 4 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
