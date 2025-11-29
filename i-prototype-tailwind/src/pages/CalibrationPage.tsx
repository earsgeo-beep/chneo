import { useState } from 'react';
import { Button } from '@/components/ui/Button';

interface CalibrationPoint {
    position: number;
    voltage: number;
    residual: number;
}

export function CalibrationPage() {
    const [selectedChannel, setSelectedChannel] = useState(1);
    const [calibrationPoints] = useState<CalibrationPoint[]>([
        { position: -100, voltage: -2.45, residual: 0.02 },
        { position: -50, voltage: -1.22, residual: 0.01 },
        { position: 0, voltage: 0.01, residual: 0.00 },
        { position: 50, voltage: 1.24, residual: 0.02 },
        { position: 100, voltage: 2.48, residual: 0.01 },
    ]);

    const calibrationResult = {
        slope: 24.52,
        offset: 0.01,
        r2: 0.99998,
        maxResidual: 0.02,
        isValid: true,
    };

    const channels = Array.from({ length: 8 }, (_, i) => ({
        id: i + 1,
        name: `Sonde ${i + 1}`,
        calibrated: i < 3,
        lastCalibration: i < 3 ? '29/11/2025 09:15' : null,
    }));

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Calibration des Sondes
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Calibration linéaire et polynomiale des capteurs
                    </p>
                </div>
                <Button>+ Nouvelle Calibration</Button>
            </div>

            {/* Channel Selection */}
            <div className="panel">
                <div className="panel-header">Sélection du Canal</div>
                <div className="panel-content">
                    <div className="flex gap-2">
                        {channels.map((ch) => (
                            <button
                                key={ch.id}
                                onClick={() => setSelectedChannel(ch.id)}
                                className={`
                  flex flex-col items-center p-3 rounded-lg border transition-colors
                  ${selectedChannel === ch.id
                                        ? 'border-primary bg-primary-light'
                                        : 'border-border hover:bg-bg-hover'}
                `}
                            >
                                <span className="font-medium">CH{ch.id}</span>
                                <span className={`text-xs mt-1 ${ch.calibrated ? 'text-success' : 'text-text-muted'}`}>
                                    {ch.calibrated ? '● Calibré' : '○ Non calibré'}
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                {/* Calibration Points */}
                <div className="panel">
                    <div className="panel-header flex items-center justify-between">
                        <span>Points de Calibration - CH{selectedChannel}</span>
                        <Button size="sm" variant="secondary">+ Ajouter Point</Button>
                    </div>
                    <div className="panel-content">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left py-2 font-medium text-text-secondary">Point</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Position (mm)</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Tension (V)</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Résidu (mm)</th>
                                    <th className="w-10"></th>
                                </tr>
                            </thead>
                            <tbody className="font-mono">
                                {calibrationPoints.map((point, i) => (
                                    <tr key={i} className="border-b border-border last:border-0">
                                        <td className="py-2">{i + 1}</td>
                                        <td className="py-2 text-right">{point.position.toFixed(0)}</td>
                                        <td className="py-2 text-right">{point.voltage.toFixed(2)}</td>
                                        <td className="py-2 text-right">{point.residual.toFixed(2)}</td>
                                        <td className="py-2 text-center">
                                            <button className="text-text-muted hover:text-error">×</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Results */}
                <div className="space-y-4">
                    {/* Chart */}
                    <div className="panel">
                        <div className="panel-header">Courbe de Calibration</div>
                        <div className="panel-content">
                            <div className="h-[180px] bg-bg-subtle rounded border border-border flex items-center justify-center">
                                <div className="text-center text-text-muted">
                                    <div className="text-2xl mb-2">📈</div>
                                    <div>Tension vs Position</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Coefficients */}
                    <div className="panel">
                        <div className="panel-header">Résultats de la Régression</div>
                        <div className="panel-content">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-text-secondary">Pente (a)</span>
                                    <div className="font-mono font-medium">{calibrationResult.slope.toFixed(2)} mV/mm</div>
                                </div>
                                <div>
                                    <span className="text-text-secondary">Offset (b)</span>
                                    <div className="font-mono font-medium">{calibrationResult.offset.toFixed(2)} V</div>
                                </div>
                                <div>
                                    <span className="text-text-secondary">R²</span>
                                    <div className="font-mono font-medium">{calibrationResult.r2.toFixed(5)}</div>
                                </div>
                                <div>
                                    <span className="text-text-secondary">Résidu max</span>
                                    <div className="font-mono font-medium">{calibrationResult.maxResidual.toFixed(2)} mm</div>
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    {calibrationResult.isValid ? (
                                        <>
                                            <span className="w-2 h-2 rounded-full bg-success"></span>
                                            <span className="text-success font-medium">CALIBRATION VALIDE</span>
                                        </>
                                    ) : (
                                        <>
                                            <span className="w-2 h-2 rounded-full bg-error"></span>
                                            <span className="text-error font-medium">CALIBRATION INVALIDE</span>
                                        </>
                                    )}
                                </div>
                                <div className="flex gap-2">
                                    <Button variant="secondary" size="sm">Recalculer</Button>
                                    <Button size="sm">Valider</Button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="panel">
                <div className="panel-content flex items-center justify-between">
                    <span className="text-sm text-text-secondary">
                        Dernière calibration: 29/11/2025 09:15 par Opérateur1
                    </span>
                    <div className="flex gap-2">
                        <Button variant="secondary">📄 Certificat PDF</Button>
                        <Button variant="secondary">📋 Historique</Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
