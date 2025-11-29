import { Button } from '@/components/ui/Button';
import { KpiCard, WaveHistogram } from '@/components/scientific';

export function GodaAnalysisPage() {
    const waveStats = {
        h13: { value: 0.125, uncertainty: 0.004 },
        h110: { value: 0.159, uncertainty: 0.005 },
        hmax: { value: 0.201, uncertainty: 0.008 },
        hmean: { value: 0.078, uncertainty: 0.002 },
        hrms: { value: 0.088, uncertainty: 0.003 },
        tz: { value: 1.05, uncertainty: 0.02 },
        tc: { value: 0.98, uncertainty: 0.02 },
        nWaves: 523,
    };

    const rayleighCheck = [
        { ratio: 'H1/3 / Hmoy', measured: 1.60, theoretical: 1.60, status: 'ok' },
        { ratio: 'H1/10 / H1/3', measured: 1.27, theoretical: 1.27, status: 'ok' },
        { ratio: 'Hrms / Hmoy', measured: 1.13, theoretical: 1.13, status: 'ok' },
    ];

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Analyse Statistique (Goda)
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Statistiques des vagues par méthode zero-crossing
                    </p>
                </div>
                <Button variant="secondary">📂 Charger Fichier</Button>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-4 gap-4">
                <KpiCard
                    title="H1/3"
                    subtitle="Hauteur Significative"
                    value={waveStats.h13.value}
                    uncertainty={waveStats.h13.uncertainty}
                    unit="m"
                    status="ok"
                />
                <KpiCard
                    title="H1/10"
                    subtitle="Hauteur 1/10"
                    value={waveStats.h110.value}
                    uncertainty={waveStats.h110.uncertainty}
                    unit="m"
                    status="ok"
                />
                <KpiCard
                    title="Hmax"
                    subtitle="Hauteur Maximale"
                    value={waveStats.hmax.value}
                    uncertainty={waveStats.hmax.uncertainty}
                    unit="m"
                    status="ok"
                />
                <KpiCard
                    title="Tz"
                    subtitle="Période Moyenne"
                    value={waveStats.tz.value}
                    uncertainty={waveStats.tz.uncertainty}
                    unit="s"
                    status="ok"
                />
            </div>

            {/* Info */}
            <div className="panel">
                <div className="panel-content flex items-center justify-center gap-8 text-sm">
                    <span>
                        <span className="text-text-muted">Vagues analysées: </span>
                        <span className="font-mono font-medium">{waveStats.nWaves}</span>
                    </span>
                    <span className="text-text-muted">|</span>
                    <span>
                        <span className="text-text-muted">Durée: </span>
                        <span className="font-mono">10:32</span>
                    </span>
                    <span className="text-text-muted">|</span>
                    <span>
                        <span className="text-text-muted">Méthode: </span>
                        <span>Zero-crossing (up-crossing)</span>
                    </span>
                    <span className="text-text-muted">|</span>
                    <span className="text-success">● Statistiques valides (N &gt; 200)</span>
                </div>
            </div>

            {/* Distribution + Stats */}
            <div className="grid grid-cols-2 gap-4">
                {/* Histogram */}
                <div className="panel">
                    <div className="panel-header">Distribution des Hauteurs</div>
                    <div className="panel-content">
                        <div className="h-[250px] bg-white rounded border border-border p-2">
                            <WaveHistogram />
                        </div>
                    </div>
                </div>

                {/* Detailed Stats */}
                <div className="panel">
                    <div className="panel-header">Statistiques Détaillées</div>
                    <div className="panel-content">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left py-2 font-medium text-text-secondary">Paramètre</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Valeur</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Incert.</th>
                                    <th className="text-left py-2 pl-2 font-medium text-text-secondary">Unité</th>
                                </tr>
                            </thead>
                            <tbody className="font-mono">
                                <tr className="border-b border-border">
                                    <td className="py-2">H1/3</td>
                                    <td className="py-2 text-right font-medium">{waveStats.h13.value.toFixed(3)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.h13.uncertainty.toFixed(3)}</td>
                                    <td className="py-2 pl-2 text-text-muted">m</td>
                                </tr>
                                <tr className="border-b border-border">
                                    <td className="py-2">H1/10</td>
                                    <td className="py-2 text-right font-medium">{waveStats.h110.value.toFixed(3)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.h110.uncertainty.toFixed(3)}</td>
                                    <td className="py-2 pl-2 text-text-muted">m</td>
                                </tr>
                                <tr className="border-b border-border">
                                    <td className="py-2">Hmax</td>
                                    <td className="py-2 text-right font-medium">{waveStats.hmax.value.toFixed(3)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.hmax.uncertainty.toFixed(3)}</td>
                                    <td className="py-2 pl-2 text-text-muted">m</td>
                                </tr>
                                <tr className="border-b border-border">
                                    <td className="py-2">Hmoy</td>
                                    <td className="py-2 text-right font-medium">{waveStats.hmean.value.toFixed(3)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.hmean.uncertainty.toFixed(3)}</td>
                                    <td className="py-2 pl-2 text-text-muted">m</td>
                                </tr>
                                <tr className="border-b border-border">
                                    <td className="py-2">Hrms</td>
                                    <td className="py-2 text-right font-medium">{waveStats.hrms.value.toFixed(3)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.hrms.uncertainty.toFixed(3)}</td>
                                    <td className="py-2 pl-2 text-text-muted">m</td>
                                </tr>
                                <tr className="border-b border-border">
                                    <td className="py-2">Tz</td>
                                    <td className="py-2 text-right font-medium">{waveStats.tz.value.toFixed(2)}</td>
                                    <td className="py-2 text-right text-text-muted">± {waveStats.tz.uncertainty.toFixed(2)}</td>
                                    <td className="py-2 pl-2 text-text-muted">s</td>
                                </tr>
                                <tr>
                                    <td className="py-2">N vagues</td>
                                    <td className="py-2 text-right font-medium">{waveStats.nWaves}</td>
                                    <td className="py-2 text-right text-text-muted">-</td>
                                    <td className="py-2 pl-2 text-text-muted">-</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Rayleigh Check */}
            <div className="panel">
                <div className="panel-header">Vérification Distribution Rayleigh</div>
                <div className="panel-content">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left py-2 font-medium text-text-secondary">Ratio</th>
                                <th className="text-right py-2 font-medium text-text-secondary">Mesuré</th>
                                <th className="text-right py-2 font-medium text-text-secondary">Théorique</th>
                                <th className="text-right py-2 font-medium text-text-secondary">Écart</th>
                                <th className="text-center py-2 font-medium text-text-secondary">Statut</th>
                            </tr>
                        </thead>
                        <tbody className="font-mono">
                            {rayleighCheck.map((check, i) => {
                                const deviation = ((check.measured - check.theoretical) / check.theoretical * 100).toFixed(1);
                                return (
                                    <tr key={i} className="border-b border-border last:border-0">
                                        <td className="py-2 font-sans">{check.ratio}</td>
                                        <td className="py-2 text-right font-medium">{check.measured.toFixed(2)}</td>
                                        <td className="py-2 text-right text-text-muted">{check.theoretical.toFixed(2)}</td>
                                        <td className="py-2 text-right">{deviation}%</td>
                                        <td className="py-2 text-center">
                                            <span className="text-success">✓ OK</span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                    <div className="mt-4 pt-4 border-t border-border flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-success"></span>
                        <span className="text-sm text-success">
                            Distribution conforme à Rayleigh (écarts &lt; 5%)
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
