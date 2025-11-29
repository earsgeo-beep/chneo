import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { MetrologicalValue, SpectrumPlot } from '@/components/scientific';

export function SpectralAnalysisPage() {
    const [selectedFile] = useState<string | null>(null);
    const [selectedChannel, setSelectedChannel] = useState('1');
    const [windowType, setWindowType] = useState('hanning');
    const [segments, setSegments] = useState('8');
    const [overlap, setOverlap] = useState('50');
    const [hasResults, setHasResults] = useState(false);

    // Demo data
    const spectralParams = [
        { parameter: 'Hs (= 4√m0)', value: 0.125, uncertainty: 0.004, unit: 'm' },
        { parameter: 'Tp (période pic)', value: 1.23, uncertainty: 0.02, unit: 's' },
        { parameter: 'fp (fréq. pic)', value: 0.813, uncertainty: 0.01, unit: 'Hz' },
        { parameter: 'm0 (moment 0)', value: 9.77e-4, uncertainty: 1.0e-5, unit: 'm²' },
        { parameter: 'm2 (moment 2)', value: 8.12e-4, uncertainty: 8.0e-6, unit: 'm²/s²' },
        { parameter: 'Tm02 (= √(m0/m2))', value: 1.10, uncertainty: 0.02, unit: 's' },
    ];

    const handleCalculate = () => {
        setHasResults(true);
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Analyse Spectrale (FFT)
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Densité spectrale de puissance et paramètres spectraux
                    </p>
                </div>
                <Button variant="secondary">
                    📂 Charger Fichier
                </Button>
            </div>

            {/* Selected File */}
            {selectedFile && (
                <div className="panel">
                    <div className="panel-content flex items-center gap-6 text-sm">
                        <span className="font-medium">{selectedFile}</span>
                        <span className="text-text-muted">|</span>
                        <span>Durée: <span className="font-mono">10:32</span></span>
                        <span className="text-text-muted">|</span>
                        <span>fs: <span className="font-mono">100 Hz</span></span>
                        <span className="text-text-muted">|</span>
                        <span>8 canaux</span>
                    </div>
                </div>
            )}

            {/* Config + Results */}
            <div className="grid grid-cols-2 gap-4">
                {/* FFT Params */}
                <div className="panel">
                    <div className="panel-header">Paramètres FFT</div>
                    <div className="panel-content space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Canal
                                </label>
                                <select
                                    className="w-full h-9 px-3 rounded border border-border bg-white text-sm"
                                    value={selectedChannel}
                                    onChange={(e) => setSelectedChannel(e.target.value)}
                                >
                                    {Array.from({ length: 8 }, (_, i) => (
                                        <option key={i} value={i + 1}>CH{i + 1} - Sonde {i + 1}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Fenêtrage
                                </label>
                                <select
                                    className="w-full h-9 px-3 rounded border border-border bg-white text-sm"
                                    value={windowType}
                                    onChange={(e) => setWindowType(e.target.value)}
                                >
                                    <option value="hanning">Hanning</option>
                                    <option value="hamming">Hamming</option>
                                    <option value="blackman">Blackman</option>
                                    <option value="rectangular">Rectangulaire</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Segments (Welch)
                                </label>
                                <select
                                    className="w-full h-9 px-3 rounded border border-border bg-white text-sm"
                                    value={segments}
                                    onChange={(e) => setSegments(e.target.value)}
                                >
                                    <option value="4">4 segments</option>
                                    <option value="8">8 segments</option>
                                    <option value="16">16 segments</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Recouvrement
                                </label>
                                <select
                                    className="w-full h-9 px-3 rounded border border-border bg-white text-sm"
                                    value={overlap}
                                    onChange={(e) => setOverlap(e.target.value)}
                                >
                                    <option value="0">0%</option>
                                    <option value="50">50%</option>
                                    <option value="75">75%</option>
                                </select>
                            </div>
                        </div>
                        <Button onClick={handleCalculate} className="w-full">
                            Calculer Spectre
                        </Button>
                    </div>
                </div>

                {/* Main Results */}
                <div className="panel">
                    <div className="panel-header">Résultats Principaux</div>
                    <div className="panel-content">
                        {hasResults ? (
                            <div className="grid grid-cols-3 gap-4">
                                <MetrologicalValue
                                    label="Hs"
                                    value={0.125}
                                    uncertainty={0.004}
                                    unit="m"
                                />
                                <MetrologicalValue
                                    label="Tp"
                                    value={1.23}
                                    uncertainty={0.02}
                                    unit="s"
                                />
                                <MetrologicalValue
                                    label="m0"
                                    value={9.77e-4}
                                    uncertainty={1.0e-5}
                                    unit="m²"
                                    precision={2}
                                />
                            </div>
                        ) : (
                            <div className="h-24 flex items-center justify-center text-text-muted">
                                Charger un fichier et calculer pour voir les résultats
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Spectrum Chart */}
            <div className="panel">
                <div className="panel-header flex items-center justify-between">
                    <span>Spectre de Densité de Puissance</span>
                    <div className="flex items-center gap-2">
                        <button className="px-2 py-1 text-xs rounded border border-border hover:bg-bg-hover">
                            Lin/Log
                        </button>
                        <button className="px-2 py-1 text-xs rounded border border-border hover:bg-bg-hover">
                            Zoom
                        </button>
                        <button className="px-2 py-1 text-xs rounded border border-border hover:bg-bg-hover">
                            Export PNG
                        </button>
                    </div>
                </div>
                <div className="panel-content">
                    <div className="h-[300px] bg-white rounded border border-border p-2">
                        <SpectrumPlot logScale={false} />
                    </div>
                </div>
            </div>

            {/* Detailed Params Table */}
            <div className="panel">
                <div className="panel-header">Paramètres Spectraux Détaillés</div>
                <div className="panel-content">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left py-2 font-medium text-text-secondary">Paramètre</th>
                                <th className="text-right py-2 font-medium text-text-secondary">Valeur</th>
                                <th className="text-right py-2 font-medium text-text-secondary">Incertitude</th>
                                <th className="text-left py-2 pl-4 font-medium text-text-secondary">Unité</th>
                            </tr>
                        </thead>
                        <tbody>
                            {spectralParams.map((param, i) => (
                                <tr key={i} className="border-b border-border last:border-0">
                                    <td className="py-2 text-text-primary">{param.parameter}</td>
                                    <td className="py-2 text-right font-mono font-medium text-text-primary">
                                        {typeof param.value === 'number' && param.value < 0.01
                                            ? param.value.toExponential(2)
                                            : param.value.toFixed(3)}
                                    </td>
                                    <td className="py-2 text-right font-mono text-text-muted">
                                        ± {typeof param.uncertainty === 'number' && param.uncertainty < 0.01
                                            ? param.uncertainty.toExponential(1)
                                            : param.uncertainty.toFixed(3)}
                                    </td>
                                    <td className="py-2 pl-4 text-text-muted">{param.unit}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-border">
                        <Button variant="secondary" size="sm">📋 Copier</Button>
                        <Button variant="secondary" size="sm">📥 Export CSV</Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
