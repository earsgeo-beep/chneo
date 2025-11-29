import { KpiCard, ChannelIndicator, StatusBadge } from '@/components/scientific';

export function Dashboard() {
    // Demo data
    const channels = Array.from({ length: 8 }, (_, i) => ({
        id: i + 1,
        name: `Sonde ${i + 1}`,
        value: (Math.random() - 0.5) * 0.1,
        level: Math.floor(Math.random() * 60) + 20,
        status: i < 6 ? 'ok' as const : 'off' as const,
    }));

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Tableau de Bord
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Vue d'ensemble du système d'acquisition
                    </p>
                </div>
                <StatusBadge status="idle" />
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-4 gap-4">
                <KpiCard
                    title="Hs"
                    subtitle="Hauteur Significative"
                    value={0.125}
                    uncertainty={0.004}
                    unit="m"
                    status="ok"
                    metadata="Dernière analyse"
                />
                <KpiCard
                    title="Tp"
                    subtitle="Période de Pic"
                    value={1.23}
                    uncertainty={0.02}
                    unit="s"
                    status="ok"
                    metadata="FFT"
                />
                <KpiCard
                    title="Kr"
                    subtitle="Coef. Réflexion"
                    value={0.35}
                    uncertainty={0.03}
                    unit=""
                    status="ok"
                    metadata="Mansard-Funke"
                />
                <KpiCard
                    title="N"
                    subtitle="Nombre Vagues"
                    value={523}
                    unit="vagues"
                    status="ok"
                    metadata="Goda"
                />
            </div>

            {/* Channels Panel */}
            <div className="panel">
                <div className="panel-header flex items-center justify-between">
                    <span>Canaux d'Acquisition</span>
                    <span className="text-sm font-normal text-text-muted">
                        6 actifs / 8 total
                    </span>
                </div>
                <div className="panel-content">
                    <div className="grid grid-cols-8 gap-3">
                        {channels.map((ch) => (
                            <ChannelIndicator
                                key={ch.id}
                                channel={ch.id}
                                name={ch.name}
                                value={ch.value}
                                unit="m"
                                level={ch.level}
                                status={ch.status}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-3 gap-4">
                <ActionCard
                    title="Nouvelle Acquisition"
                    description="Démarrer une session"
                    icon="▶"
                    href="/acquisition/live"
                />
                <ActionCard
                    title="Analyser Données"
                    description="FFT, Goda, Réflexion"
                    icon="📊"
                    href="/analysis/spectral"
                />
                <ActionCard
                    title="Calibration"
                    description="Vérifier les sondes"
                    icon="🔧"
                    href="/calibration"
                />
            </div>
        </div>
    );
}

function ActionCard({ title, description, icon, href }: {
    title: string;
    description: string;
    icon: string;
    href: string;
}) {
    return (
        <a
            href={href}
            className="panel hover:border-primary-light transition-colors cursor-pointer block"
        >
            <div className="panel-content flex items-center gap-4">
                <div className="text-2xl">{icon}</div>
                <div>
                    <div className="font-medium text-text-primary">{title}</div>
                    <div className="text-sm text-text-secondary">{description}</div>
                </div>
            </div>
        </a>
    );
}
