import { useEffect, useRef } from 'react';

interface RealtimeOscilloscopeProps {
    data: number[][]; // [channel][sample]
    sampleRate?: number;
    windowSize?: number; // seconds to display
    channels?: boolean[]; // active channels
}

export function RealtimeOscilloscope({
    data,
    sampleRate = 100,
    windowSize = 5,
    channels = Array(8).fill(true)
}: RealtimeOscilloscopeProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const container = containerRef.current;
        if (!canvas || !container) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Resize handling
        const resizeObserver = new ResizeObserver(() => {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        });
        resizeObserver.observe(container);

        // Animation loop
        let animationId: number;

        const render = () => {
            const width = canvas.width;
            const height = canvas.height;

            // Clear
            ctx.fillStyle = '#F8FAFC'; // bg-app
            ctx.fillRect(0, 0, width, height);

            // Grid
            ctx.strokeStyle = '#E2E8F0';
            ctx.lineWidth = 1;
            ctx.beginPath();
            // Vertical lines (time)
            const timeDivs = 10;
            for (let i = 0; i <= timeDivs; i++) {
                const x = (i / timeDivs) * width;
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
            }
            // Horizontal lines (amplitude)
            const ampDivs = 8;
            for (let i = 0; i <= ampDivs; i++) {
                const y = (i / ampDivs) * height;
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
            }
            ctx.stroke();

            // Plot Data
            const activeChannels = channels.map((active, i) => active ? i : -1).filter(i => i !== -1);
            if (activeChannels.length === 0) return;

            const channelHeight = height / activeChannels.length;
            const samplesToDraw = sampleRate * windowSize;

            activeChannels.forEach((channelIndex, i) => {
                const channelData = data[channelIndex];
                if (!channelData || channelData.length === 0) return;

                // Channel area
                const yOffset = i * channelHeight;
                const yCenter = yOffset + channelHeight / 2;
                const yScale = channelHeight * 0.4; // 40% of channel height is +/- 1 unit (approx)

                // Draw zero line
                ctx.strokeStyle = '#CBD5E1';
                ctx.setLineDash([2, 2]);
                ctx.beginPath();
                ctx.moveTo(0, yCenter);
                ctx.lineTo(width, yCenter);
                ctx.stroke();
                ctx.setLineDash([]);

                // Draw waveform
                ctx.strokeStyle = '#0066CC'; // Primary Blue
                ctx.lineWidth = 1.5;
                ctx.beginPath();

                const startIndex = Math.max(0, channelData.length - samplesToDraw);
                const visibleData = channelData.slice(startIndex);

                visibleData.forEach((val, idx) => {
                    const x = (idx / samplesToDraw) * width;
                    // Invert Y because canvas Y is down
                    const y = yCenter - (val * yScale);
                    if (idx === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();

                // Label
                ctx.fillStyle = '#64748B';
                ctx.font = '10px JetBrains Mono';
                ctx.fillText(`CH${channelIndex + 1}`, 5, yOffset + 12);
            });

            animationId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationId);
            resizeObserver.disconnect();
        };
    }, [data, sampleRate, windowSize, channels]);

    return (
        <div ref={containerRef} className="w-full h-full min-h-[400px] relative border border-border rounded bg-bg-app overflow-hidden">
            <canvas ref={canvasRef} className="block" />
        </div>
    );
}
