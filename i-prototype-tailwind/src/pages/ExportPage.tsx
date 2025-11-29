import { useState } from 'react';
import { Button } from '@/components/ui/Button';

export function ExportPage() {
    const [selectedSession, setSelectedSession] = useState<string | null>(null);
    const [exportFormat, setExportFormat] = useState('hdf5');
    const [includeMetadata, setIncludeMetadata] = useState(true);
    const [includeUncertainties, setIncludeUncertainties] = useState(true);

    const sessions = [
        { id: '001', name: 'session_2025-11-29_001', date: '29/11/2025 14:35', duration: '10:32', size: '45.2 MB' },
        { id: '002', name: 'session_2025-11-29_002', date: '29/11/2025 16:10', duration: '15:45', size: '68.1 MB' },
        { id: '003', name: 'session_2025-11-28_001', date: '28/11/2025 09:20', duration: '30:12', size: '142.5 MB' },
    ];

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold text-text-primary">
                        Export des Données
                    </h1>
                    <p className="text-sm text-text-secondary">
                        Exporter les sessions d'acquisition et résultats d'analyse
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {/* Sessions List */}
                <div className="col-span-2 panel">
                    <div className="panel-header">Sessions Disponibles</div>
                    <div className="panel-content">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left py-2 w-8"></th>
                                    <th className="text-left py-2 font-medium text-text-secondary">Nom</th>
                                    <th className="text-left py-2 font-medium text-text-secondary">Date</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Durée</th>
                                    <th className="text-right py-2 font-medium text-text-secondary">Taille</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.map((session) => (
                                    <tr
                                        key={session.id}
                                        className={`border-b border-border last:border-0 cursor-pointer hover:bg-bg-hover ${selectedSession === session.id ? 'bg-primary-light' : ''
                                            }`}
                                        onClick={() => setSelectedSession(session.id)}
                                    >
                                        <td className="py-3">
                                            <input
                                                type="radio"
                                                checked={selectedSession === session.id}
                                                onChange={() => setSelectedSession(session.id)}
                                                className="accent-primary"
                                            />
                                        </td>
                                        <td className="py-3 font-mono">{session.name}</td>
                                        <td className="py-3">{session.date}</td>
                                        <td className="py-3 text-right font-mono">{session.duration}</td>
                                        <td className="py-3 text-right font-mono text-text-muted">{session.size}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Export Options */}
                <div className="panel">
                    <div className="panel-header">Options d'Export</div>
                    <div className="panel-content space-y-4">
                        {/* Format */}
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-2">
                                Format
                            </label>
                            <div className="space-y-2">
                                {[
                                    { value: 'hdf5', label: 'HDF5 (.h5)', desc: 'Recommandé - Données complètes' },
                                    { value: 'csv', label: 'CSV (.csv)', desc: 'Tableau simple' },
                                    { value: 'mat', label: 'MATLAB (.mat)', desc: 'Compatible MATLAB' },
                                    { value: 'json', label: 'JSON (.json)', desc: 'Métadonnées et config' },
                                ].map((format) => (
                                    <label
                                        key={format.value}
                                        className={`flex items-start gap-3 p-2 rounded border cursor-pointer ${exportFormat === format.value
                                                ? 'border-primary bg-primary-light'
                                                : 'border-border hover:bg-bg-hover'
                                            }`}
                                    >
                                        <input
                                            type="radio"
                                            name="format"
                                            value={format.value}
                                            checked={exportFormat === format.value}
                                            onChange={(e) => setExportFormat(e.target.value)}
                                            className="mt-0.5 accent-primary"
                                        />
                                        <div>
                                            <div className="font-medium text-sm">{format.label}</div>
                                            <div className="text-xs text-text-muted">{format.desc}</div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Options */}
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-2">
                                Contenu
                            </label>
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={includeMetadata}
                                        onChange={(e) => setIncludeMetadata(e.target.checked)}
                                        className="accent-primary"
                                    />
                                    <span className="text-sm">Inclure métadonnées</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={includeUncertainties}
                                        onChange={(e) => setIncludeUncertainties(e.target.checked)}
                                        className="accent-primary"
                                    />
                                    <span className="text-sm">Inclure incertitudes (GUM)</span>
                                </label>
                            </div>
                        </div>

                        {/* Export Button */}
                        <Button
                            className="w-full"
                            disabled={!selectedSession}
                        >
                            📥 Exporter
                        </Button>
                    </div>
                </div>
            </div>

            {/* Reports */}
            <div className="panel">
                <div className="panel-header">Génération de Rapports</div>
                <div className="panel-content">
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 border border-border rounded-lg hover:border-primary cursor-pointer transition-colors">
                            <div className="text-2xl mb-2">📊</div>
                            <div className="font-medium">Rapport d'Essai</div>
                            <div className="text-xs text-text-muted mt-1">
                                Résultats complets avec graphiques
                            </div>
                        </div>
                        <div className="p-4 border border-border rounded-lg hover:border-primary cursor-pointer transition-colors">
                            <div className="text-2xl mb-2">📋</div>
                            <div className="font-medium">Certificat de Calibration</div>
                            <div className="text-xs text-text-muted mt-1">
                                Document métrologique
                            </div>
                        </div>
                        <div className="p-4 border border-border rounded-lg hover:border-primary cursor-pointer transition-colors">
                            <div className="text-2xl mb-2">📈</div>
                            <div className="font-medium">Rapport de Réflexion</div>
                            <div className="text-xs text-text-muted mt-1">
                                Analyse Mansard-Funke
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
