import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface WaveHistogramProps {
    data?: { bin: number; count: number; rayleigh: number }[];
}

export function WaveHistogram({ data }: WaveHistogramProps) {
    // Demo data
    const chartData = data || Array.from({ length: 20 }, (_, i) => {
        const h = i * 0.02;
        // Rayleigh distribution shape
        const Hrms = 0.1;
        const rayleigh = (2 * h / (Hrms * Hrms)) * Math.exp(-1 * (h * h) / (Hrms * Hrms));
        // Random histogram counts roughly following Rayleigh
        const count = Math.max(0, Math.floor(rayleigh * 50 + (Math.random() - 0.5) * 10));
        return {
            bin: h,
            count,
            rayleigh: rayleigh * 50 // Scale theoretical to match count magnitude for demo
        };
    });

    return (
        <div className="w-full h-full min-h-[250px] font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                    <XAxis
                        dataKey="bin"
                        tickFormatter={(val) => val.toFixed(2)}
                        label={{ value: 'Hauteur (m)', position: 'insideBottomRight', offset: -5 }}
                    />
                    <YAxis
                        yAxisId="left"
                        label={{ value: 'Nombre', angle: -90, position: 'insideLeft' }}
                    />
                    <YAxis
                        yAxisId="right"
                        orientation="right"
                        hide
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', fontSize: '12px' }}
                        labelFormatter={(label) => `H = ${Number(label).toFixed(2)} m`}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Bar
                        yAxisId="left"
                        dataKey="count"
                        name="Mesuré"
                        fill="#0066CC"
                        opacity={0.8}
                        barSize={20}
                    />
                    <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="rayleigh"
                        name="Rayleigh (Théorique)"
                        stroke="#EF4444"
                        strokeWidth={2}
                        dot={false}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
}
