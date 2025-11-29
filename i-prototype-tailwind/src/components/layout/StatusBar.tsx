

export function StatusBar() {
    return (
        <footer
            className="fixed bottom-0 left-0 right-0 flex items-center justify-between px-4 bg-bg-panel border-t border-border text-xs"
            style={{ height: 'var(--spacing-statusbar)' }}
        >
            {/* Left */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-success"></span>
                    <span className="text-text-secondary">MCC USB-1608FS</span>
                </div>
                <span className="text-text-muted">|</span>
                <span className="font-mono text-text-secondary">fs = 100 Hz</span>
                <span className="text-text-muted">|</span>
                <span className="text-text-secondary">8/8 canaux actifs</span>
            </div>

            {/* Right */}
            <div className="flex items-center gap-4">
                <span className="text-text-muted">CHNeoWave v1.1.0</span>
            </div>
        </footer>
    );
}
