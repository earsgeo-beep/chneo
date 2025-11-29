import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { KrFrequencyPlot, SpectrumPlot } from '@/components/scientific';

export function ReflectionAnalysisPage() {
    const [config] = useState({
        x1: 0.0,
        x2: 0.5,
        x3: 1.2,
        depth: 0.8,
        fMin: 0.5,
        fMax: 2.0,
        ch1: '1',
        ch2: '2',
        ch3: '3',
    });

    const [hasResults] = useState(true); // Demo

    const result = {
        kr: 0.35,
        krUncertainty: 0.03,
        interpretation: 'RÉFLEXION MODÉRÉE',
        interpretationColor: 'var(--color-warning)',
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Analyse de Réflexion (Mansard-Funke)
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Séparation houle incidente/réfléchie - Méthode 3 sondes
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button variant="secondary">📂 Charger</Button>
                    <Button>▶ Analyser</Button>
                </div>
            </div>

            {/* Configuration 3 sondes */}
            <div className="panel">
                <div className="panel-header">Configuration des 3 Sondes</div>
                <div className="panel-content">
                    {/* Visual Schema */}
                    <div className="mb-6 p-4 bg-bg-subtle rounded-lg">
                        <div className="flex items-center justify-center gap-4 text-sm">
                            <div className="text-center">
                                <div className="font-medium">Sonde 1</div>
                                <div className="text-text-muted">x₁ = {config.x1.toFixed(2)} m</div>
                            </div>
                            <div className="flex-1 h-0.5 bg-primary relative">
                                <div className="absolute top-1/2 left-0 w-3 h-3 -mt-1.5 rounded-full bg-primary"></div>
                            </div>
                            <div className="text-center">
                                <div className="font-medium">Sonde 2</div>
                                <div className="text-text-muted">x₂ = {config.x2.toFixed(2)} m</div>
                            </div>
                            <div className="flex-1 h-0.5 bg-primary relative">
                                <div className="absolute top-1/2 left-0 w-3 h-3 -mt-1.5 rounded-full bg-primary"></div>
                            </div>
                            <div className="text-center">
                                <div className="font-medium">Sonde 3</div>
                                <div className="text-text-muted">x₃ = {config.x3.toFixed(2)} m</div>
                            </div>
                            <div className="flex-1 h-0.5 bg-primary">
                                <div className="absolute top-1/2 left-0 w-3 h-3 -mt-1.5 rounded-full bg-primary"></div>
                            </div>
                            <div className="text-center px-4 py-2 border-2 border-text-muted rounded">
                                <div className="text-text-muted">Structure</div>
                            </div>
                        </div>
                    </div>

                    {/* Inputs */}
                    <div className="grid grid-cols-6 gap-4">
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Canal Sonde 1
                            </label>
                            <select className="w-full h-9 px-2 rounded border border-border bg-white text-sm">
                                {Array.from({ length: 8 }, (_, i) => (
                                    <option key={i} value={i + 1}>CH{i + 1}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Canal Sonde 2
                            </label>
                            <select className="w-full h-9 px-2 rounded border border-border bg-white text-sm">
                                {Array.from({ length: 8 }, (_, i) => (
                                    <option key={i} value={i + 1} selected={i === 1}>CH{i + 1}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Canal Sonde 3
                            </label>
                            <select className="w-full h-9 px-2 rounded border border-border bg-white text-sm">
                                {Array.from({ length: 8 }, (_, i) => (
                                    <option key={i} value={i + 1} selected={i === 2}>CH{i + 1}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Profondeur
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    className="w-full h-9 px-2 pr-8 rounded border border-border bg-white text-sm font-mono"
                                    defaultValue={config.depth}
                                    step="0.01"
                                />
                                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted text-sm">m</span>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Fréq. Min
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    className="w-full h-9 px-2 pr-8 rounded border border-border bg-white text-sm font-mono"
                                    defaultValue={config.fMin}
                                    step="0.1"
                                />
                                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted text-sm">Hz</span>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-text-secondary mb-1">
                                Fréq. Max
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    className="w-full h-9 px-2 pr-8 rounded border border-border bg-white text-sm font-mono"
                                    defaultValue={config.fMax}
                                    step="0.1"
                                />
                                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted text-sm">Hz</span>
                            </div>
                        </div>
                    </div>

                    {/* Validation */}
                    <div className="mt-4 flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 rounded-full bg-success"></span>
                        <span className="text-success">
                            Configuration valide - Pas de singularité dans la plage de fréquences
                        </span>
                    </div>
                </div>
            </div>

            {/* Main Result */}
            {hasResults && (
                <div className="panel">
                    <div className="panel-content">
                        <div className="text-center py-6">
                            <div className="text-sm text-text-secondary mb-2">
                                COEFFICIENT DE RÉFLEXION
                            </div>
                            <div className="text-5xl font-mono font-bold text-text-primary">
                                Kr = {result.kr.toFixed(2)}
                                <span className="text-2xl text-text-muted font-normal ml-2">
                                    ± {result.krUncertainty.toFixed(2)}
                                </span>
                            </div>
                            <div
                                className="mt-4 inline-block px-4 py-2 rounded-full text-sm font-medium"
                                style={{
                                    backgroundColor: `color-mix(in srgb, ${result.interpretationColor} 20%, transparent)`,
                                    color: result.interpretationColor
                                }}
                            >
                                {result.interpretation}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-2 gap-4">
                {/* Kr(f) */}
                <div className="panel">
                    <div className="panel-header">Coefficient de Réflexion Kr(f)</div>
                    <div className="panel-content">
                        <div className="h-[200px] bg-white rounded border border-border p-2">
                            <KrFrequencyPlot />
                        </div>
                    </div>
                </div>

                {/* Spectra */}
                <div className="panel">
                    <div className="panel-header">Spectres Incident et Réfléchi</div>
                    <div className="panel-content">
                        <div className="h-[200px] bg-white rounded border border-border p-2">
                            <SpectrumPlot />
                        </div>
                    </div>
                </div>
            </div>

            {/* Export */}
            <div className="panel">
                <div className="panel-content flex items-center justify-between">
                    <span className="text-sm text-text-secondary">Export des résultats</span>
                    <div className="flex gap-2">
                        <Button variant="secondary" size="sm">📥 Export CSV Kr(f)</Button>
                        <Button variant="secondary" size="sm">📥 Export Spectres</Button>
                        <Button size="sm">📄 Rapport PDF</Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
