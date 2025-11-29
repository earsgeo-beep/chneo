import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface SpectrumPlotProps {
    data?: { f: number; S: number }[];
    logScale?: boolean;
}

export function SpectrumPlot({ data, logScale = false }: SpectrumPlotProps) {
    // Generate demo data if none provided
    const chartData = data || Array.from({ length: 100 }, (_, i) => {
        const f = i * 0.02;
        // JONSWAP-like shape demo
        const fp = 0.8;
        const gamma = 3.3;
        const sigma = f <= fp ? 0.07 : 0.09;
        const exp1 = -1.25 * Math.pow(f / fp, -4);
        const exp2 = -0.5 * Math.pow((f - fp) / (sigma * fp), 2);
        const S = f === 0 ? 0 : 0.01 * Math.pow(f, -5) * Math.exp(exp1) * Math.pow(gamma, Math.exp(exp2));
        return { f, S: S > 0.0001 ? S : 0 };
    });

    return (
        <div className="w-full h-full min-h-[300px] font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorS" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#0066CC" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#0066CC" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                    <XAxis
                        dataKey="f"
                        type="number"
                        tickFormatter={(val) => val.toFixed(2)}
                        label={{ value: 'Fréquence (Hz)', position: 'insideBottomRight', offset: -5 }}
                        domain={[0, 'auto']}
                    />
                    <YAxis
                        scale={logScale ? 'log' : 'auto'}
                        domain={['auto', 'auto']}
                        label={{ value: 'S(f) [m²/Hz]', angle: -90, position: 'insideLeft' }}
                        tickFormatter={(val) => val.toExponential(1)}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', fontSize: '12px' }}
                        itemStyle={{ color: '#0066CC' }}
                        formatter={(value: number) => [value.toExponential(3), 'S(f)']}
                        labelFormatter={(label) => `f = ${Number(label).toFixed(3)} Hz`}
                    />
                    <Area
                        type="monotone"
                        dataKey="S"
                        stroke="#0066CC"
                        fillOpacity={1}
                        fill="url(#colorS)"
                        strokeWidth={2}
                        isAnimationActive={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
