"""Scientific, auditable rendering of CHNeoWave analysis results."""

# HTML tables and print CSS are kept readable in source as complete markup lines.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import html
from pathlib import Path
from typing import Any


def source_sha256(source_file: str | None) -> str:
    """Return the source fingerprint without loading a laboratory record in memory."""

    if not source_file:
        return "Non disponible"
    path = Path(source_file)
    if not path.is_file():
        return "Source inaccessible"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def diagnostic_label(indicators: dict[str, Any]) -> str:
    """Describe machine observations without taking an engineering decision."""

    return {
        "nominal": "AUCUNE ALERTE",
        "valid": "AUCUNE ALERTE",
        "warning": "ALERTE À EXAMINER",
        "critical": "ALERTE CRITIQUE",
        # Compatibility with analysis files produced by older CHNeoWave builds.
        "rejected": "ALERTE CRITIQUE",
    }.get(
        str(indicators.get("diagnostic_level") or indicators.get("status", "")),
        "AUCUNE ALERTE" if not indicators.get("warnings") else "ALERTE À EXAMINER",
    )


def engineer_decision_label(indicators: dict[str, Any]) -> str:
    """Return the explicit decision recorded by the responsible engineer."""

    return {
        "accepted": "ACCEPTÉ PAR L’INGÉNIEUR",
        "rejected": "REJETÉ PAR L’INGÉNIEUR",
        "pending": "EN ATTENTE",
        "": "EN ATTENTE",
    }.get(str(indicators.get("engineer_decision", "pending")), "EN ATTENTE")


def quality_label(indicators: dict[str, Any]) -> str:
    """Backward-compatible alias for the automatic diagnostic label."""

    return diagnostic_label(indicators)


def _number(value: Any, digits: int = 6) -> str:
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return "—"


def _channel_unit(results: dict[str, Any], channel: str) -> str:
    metadata = results.get("channel_metadata", {})
    if isinstance(metadata, list):
        channel_names = list(results.get("basic_stats", {}))
        metadata = {
            str(item.get("key") or channel_names[index] if index < len(channel_names) else index): item
            for index, item in enumerate(metadata)
            if isinstance(item, dict)
        }
    item = metadata.get(channel, {}) if isinstance(metadata, dict) else {}
    return str(item.get("physical_unit") or item.get("physical_units") or item.get("unit") or "unité")


def build_scientific_report_text(
    results: dict[str, Any],
    source_file: str | None,
    project_metadata: dict[str, Any] | None = None,
    report_config: dict[str, Any] | None = None,
) -> str:
    """Build the human-readable scientific record used by TXT and the analysis tab."""

    project = project_metadata or {}
    config = report_config or {}
    metadata = results.get("metadata", {})
    method = results.get("analysis_configuration", {})
    spectra = results.get("spectral_analysis", {})
    waves = results.get("wave_parameters", {})
    quality = results.get("quality", {})
    stats = results.get("basic_stats", {})
    channels = list(stats)
    maximum_frequency = method.get("max_frequency")
    if maximum_frequency is None:
        maximum_frequency = float(metadata.get("sample_rate_hz", results.get("sample_rate", 0))) / 2
    decisions = [engineer_decision_label(quality.get(channel, {})) for channel in channels]
    if any(decision == "REJETÉ PAR L’INGÉNIEUR" for decision in decisions):
        overall = "PARTIELLEMENT REJETÉ PAR L’INGÉNIEUR"
    elif decisions and all(decision == "ACCEPTÉ PAR L’INGÉNIEUR" for decision in decisions):
        overall = "VALIDÉ PAR L’INGÉNIEUR"
    else:
        overall = "EN ATTENTE DE VALIDATION INGÉNIEUR"

    lines = [
        config.get("title") or "Rapport scientifique CHNeoWave",
        f"Décision ingénieur globale: {overall}",
        f"Projet: {project.get('name', 'CHNeoWave')}",
        f"Essai / référence: {config.get('test_id', '') or 'Non renseigné'}",
        f"Opérateur / analyste: {config.get('author', '') or project.get('manager', '') or 'Non renseigné'}",
        f"Date du rapport: {config.get('date', '') or 'Non renseignée'}",
        "",
        "1. TRAÇABILITÉ DE LA SOURCE",
        f"Source: {source_file or 'Non définie'}",
        f"SHA-256: {source_sha256(source_file)}",
        f"Format source: {results.get('source_metadata', {}).get('source_format', 'détecté par CHNeoWave')}",
        "Fréquence d'échantillonnage: "
        f"{_number(metadata.get('sample_rate_hz', results.get('sample_rate')))} Hz",
        f"Pas temporel: {_number(metadata.get('dt_seconds'))} s",
        "Enregistrement source: "
        f"{metadata.get('source_n_samples', metadata.get('n_samples', 0))} échantillons, "
        f"{_number(metadata.get('source_duration_s', metadata.get('duration_s')))} s",
        f"Intervalle analysé: {_number(metadata.get('analysis_start_s', 0))} à "
        f"{_number(metadata.get('analysis_end_s', metadata.get('duration_s')))} s "
        f"({metadata.get('n_samples', 0)} échantillons)",
        "",
        "2. MÉTHODE NUMÉRIQUE",
        f"Méthode: {method.get('method', 'Welch PSD + zero-upcrossing')}",
        f"Version: {method.get('method_version', '—')}",
        f"Fenêtre: {method.get('window', 'hann')}",
        f"Segment: {method.get('segment_length', '—')} échantillons",
        f"Recouvrement: {_number(100 * float(method.get('overlap_ratio', 0)))} %",
        f"Détrend linéaire: {'oui' if method.get('detrend', True) else 'non'}",
        f"Bande demandée: {_number(method.get('min_frequency', 0))} à {_number(maximum_frequency)} Hz",
        "PSD unilatérale en densité; moments intégrés sur la bande sélectionnée.",
        "IC 95 % approximatif par loi du χ² et DDL ≈ 2K; la corrélation du recouvrement n'est pas corrigée.",
        "",
        "3. RÉSULTATS PAR CANAL",
    ]

    for channel in channels:
        channel_stats = stats.get(channel, {})
        spectrum = spectra.get(channel, {})
        channel_waves = waves.get(channel, {})
        indicators = quality.get(channel, {})
        moments = spectrum.get("spectral_moments", {})
        tp = (
            f"{_number(channel_waves.get('Tp'))} s"
            if indicators.get("peak_period_reliable", False)
            else f"À CONFIRMER (valeur calculée: {_number(channel_waves.get('Tp'))} s)"
        )
        lines.extend(
            [
                f"[{channel}] · diagnostic automatique: {diagnostic_label(indicators)} · "
                f"décision: {engineer_decision_label(indicators)} · unité: {_channel_unit(results, channel)}",
                f"  N (nombre d’échantillons)={channel_stats.get('sample_count', metadata.get('n_samples', 0))}; "
                f"moyenne={_number(channel_stats.get('mean'))}; "
                f"σ (écart-type population)={_number(channel_stats.get('std'))}; "
                f"RMS (valeur efficace)={_number(channel_stats.get('rms'))}; min/max={_number(channel_stats.get('min'))} / "
                f"{_number(channel_stats.get('max'))}",
                f"  Hmin={_number(channel_waves.get('H_min'))}; "
                f"Hmoy={_number(channel_waves.get('H_mean'))}; "
                f"H1/3={_number(channel_waves.get('H1_3'))}; "
                f"Hmax={_number(channel_waves.get('H_max'))}; "
                f"Hm0={_number(spectrum.get('Hm0'))}; vagues={channel_waves.get('n_waves', 0)}",
                f"  fpic={_number(spectrum.get('peak_frequency'))} Hz; Tp={tp}; "
                f"Tm01={_number(spectrum.get('Tm01'))} s; Tm02={_number(spectrum.get('Tm02'))} s; "
                f"Te={_number(spectrum.get('Te'))} s",
                f"  m-1={_number(moments.get('m_1'))}; m0={_number(moments.get('m0'))}; "
                f"m1={_number(moments.get('m1'))}; m2={_number(moments.get('m2'))}; "
                f"m4={_number(moments.get('m4'))}",
                f"  Δf={_number(spectrum.get('frequency_resolution'))} Hz; "
                f"K={spectrum.get('segment_count', 0)}; "
                f"DDL≈{spectrum.get('equivalent_degrees_of_freedom_approx', 0)}; "
                f"variance PSD/temps={_number(indicators.get('spectral_to_time_variance_ratio'))}; "
                f"stationnarité={_number(indicators.get('block_variance_ratio'))}",
            ]
        )
        warnings = indicators.get("warnings", [])
        lines.extend(f"  ALERTE: {warning}" for warning in warnings)
        if not warnings:
            lines.append("  Aucune alerte automatique.")

    lines.extend(["", "4. ANALYSES CROISÉES ET MULTI-SONDES"])
    cross = results.get("cross_spectral_analysis", {})
    if cross:
        for pair, metrics in cross.items():
            lines.append(
                f"{pair}: cohérence au pic={_number(metrics.get('coherence_at_reference_peak'))}; "
                f"phase={_number(metrics.get('phase_at_reference_peak_degrees'))}°; "
                f"retard={_number(metrics.get('time_lag_at_reference_peak_seconds'))} s"
            )
    else:
        lines.append("Analyse croisée non disponible.")
    separation = results.get("incident_reflected_analysis", {})
    if separation.get("status") == "complete":
        lines.append(
            f"Séparation incidente/réfléchie: Hm0,i={_number(separation.get('incident_Hm0'))}; "
            f"Hm0,r={_number(separation.get('reflected_Hm0'))}; "
            f"Kr={_number(separation.get('energy_reflection_coefficient'))}."
        )
    else:
        lines.append(f"Séparation incidente/réfléchie: {separation.get('reason', 'non configurée')}.")

    lines.extend(
        [
            "",
            "5. LIMITES ET INTERPRÉTATION",
            "Les paramètres de hauteur de houle ne sont physiquement interprétables que pour un capteur "
            "d'élévation correctement identifié, étalonné et exprimé dans une unité de longueur.",
            "Un Tp signalé À CONFIRMER demande l’examen de l’ingénieur: le pic peut toucher une limite "
            "de bande, la résolution temporelle peut être insuffisante ou la durée trop courte.",
            "Toute alerte de non-stationnarité, portion plate, saturation ou calibration doit être résolue "
            "ou documentée avant validation du résultat.",
        ]
    )
    notes = config.get("description", "")
    if notes:
        lines.extend(["", "6. NOTES DE L'ANALYSTE", str(notes)])

    if not config.get("include_traceability", True):
        filtered: list[str] = []
        skipping = False
        for line in lines:
            if line.startswith(("1. TRAÇABILITÉ", "2. MÉTHODE")):
                skipping = True
                continue
            if line.startswith("3. RÉSULTATS"):
                skipping = False
            if not skipping:
                filtered.append(line)
        lines = filtered
    if not config.get("include_quality", True):
        filtered = []
        skipping = False
        for line in lines:
            if line.startswith("5. LIMITES"):
                skipping = True
                continue
            if line.startswith("6. NOTES"):
                skipping = False
            if not skipping and "ALERTE:" not in line:
                filtered.append(line)
        lines = filtered
    return "\n".join(lines).strip()


def build_scientific_report_html(
    results: dict[str, Any],
    source_file: str | None,
    project_metadata: dict[str, Any] | None = None,
    report_config: dict[str, Any] | None = None,
    spectral_plot_data_uri: str = "",
    time_plot_data_uri: str = "",
) -> str:
    """Render a landscape laboratory dossier led by tables and measured evidence."""

    project = project_metadata or {}
    config = report_config or {}
    metadata = results.get("metadata", {}) or {}
    method = results.get("analysis_configuration", {}) or {}
    stats = results.get("basic_stats", {}) or {}
    waves = results.get("wave_parameters", {}) or {}
    spectra = results.get("spectral_analysis", {}) or {}
    quality = results.get("quality", {}) or {}
    channels = list(stats)

    def cell(value: Any, *, numeric: bool = False) -> str:
        text = _number(value) if numeric else str(value if value not in (None, "") else "—")
        return f'<td class="{"num" if numeric else ""}">{html.escape(text)}</td>'

    def row(values: list[tuple[Any, bool]], row_class: str = "") -> str:
        cells = "".join(cell(value, numeric=numeric) for value, numeric in values)
        return f'<tr class="{row_class}">{cells}</tr>'

    decisions = [engineer_decision_label(quality.get(channel, {})) for channel in channels]
    if any(decision == "REJETÉ PAR L’INGÉNIEUR" for decision in decisions):
        overall = "PARTIELLEMENT REJETÉ PAR L’INGÉNIEUR"
    elif decisions and all(decision == "ACCEPTÉ PAR L’INGÉNIEUR" for decision in decisions):
        overall = "VALIDÉ PAR L’INGÉNIEUR"
    else:
        overall = "EN ATTENTE DE VALIDATION INGÉNIEUR"
    rate = metadata.get("sample_rate_hz", results.get("sample_rate"))
    source_name = Path(source_file).name if source_file else "Non définie"
    report_title = html.escape(config.get("title") or "Rapport scientifique CHNeoWave")

    temporal_rows = []
    spectral_rows = []
    quality_rows = []
    for channel in channels:
        channel_stats = stats.get(channel, {})
        channel_waves = waves.get(channel, {})
        spectrum = spectra.get(channel, {})
        indicators = quality.get(channel, {})
        diagnostic = diagnostic_label(indicators)
        decision = engineer_decision_label(indicators)
        row_class = (
            "rejected"
            if decision == "REJETÉ PAR L’INGÉNIEUR"
            else "accepted"
            if decision == "ACCEPTÉ PAR L’INGÉNIEUR"
            else "pending"
        )
        temporal_rows.append(
            row(
                [
                    (channel, False),
                    (_channel_unit(results, channel), False),
                    (channel_stats.get("sample_count", metadata.get("n_samples", 0)), False),
                    (channel_stats.get("mean"), True),
                    (channel_stats.get("std"), True),
                    (channel_stats.get("rms"), True),
                    (channel_stats.get("min"), True),
                    (channel_stats.get("max"), True),
                    (channel_waves.get("H_min"), True),
                    (channel_waves.get("H_mean"), True),
                    (channel_waves.get("H1_3"), True),
                    (channel_waves.get("H_max"), True),
                    (channel_waves.get("n_waves", 0), False),
                    (decision, False),
                ],
                row_class,
            )
        )
        tp = spectrum.get("peak_period", channel_waves.get("Tp"))
        if not indicators.get("peak_period_reliable", False):
            tp = "À CONFIRMER"
        spectral_rows.append(
            row(
                [
                    (channel, False),
                    (spectrum.get("Hm0"), True),
                    (spectrum.get("peak_frequency"), True),
                    (tp, isinstance(tp, (int, float))),
                    (spectrum.get("Tm01"), True),
                    (spectrum.get("Tm02"), True),
                    (spectrum.get("Te"), True),
                    (spectrum.get("spectral_moments", {}).get("m0"), True),
                    (spectrum.get("frequency_resolution"), True),
                    (spectrum.get("segment_count", 0), False),
                    (spectrum.get("equivalent_degrees_of_freedom_approx", 0), False),
                    (diagnostic, False),
                    (decision, False),
                ],
                row_class,
            )
        )
        warnings = indicators.get("warnings", [])
        quality_rows.append(
            row(
                [
                    (channel, False),
                    (diagnostic, False),
                    (decision, False),
                    (indicators.get("spectral_to_time_variance_ratio"), True),
                    (indicators.get("block_variance_ratio"), True),
                    (indicators.get("record_cycles_at_peak"), True),
                    (indicators.get("samples_per_peak_period"), True),
                    ("; ".join(map(str, warnings)) or "Aucune", False),
                ],
                row_class,
            )
        )

    figure_blocks = []
    if time_plot_data_uri:
        figure_blocks.append(
            f'<div style="page-break-before:always"></div><section class="figure-page"><h2>3.1 Signaux temporels</h2><figure><img src="{time_plot_data_uri}"/><figcaption>Figure 1 — Signaux temporels par voie sur l’intervalle analysé.</figcaption></figure></section>'
        )
    if spectral_plot_data_uri:
        figure_number = 2 if time_plot_data_uri else 1
        figure_blocks.append(
            f'<div style="page-break-before:always"></div><section class="figure-page"><h2>3.2 Densités spectrales de puissance</h2><figure><img src="{spectral_plot_data_uri}"/><figcaption>Figure spectrale {figure_number} — Densités spectrales de puissance, estimation Welch.</figcaption></figure></section>'
        )

    traceability = ""
    if config.get("include_traceability", True):
        traceability = f"""
        <div style="page-break-before:always"></div><section class="traceability-section"><h2>6. TRAÇABILITÉ DE LA SOURCE ET MÉTHODE NUMÉRIQUE</h2>
        <table class="facts"><tbody>
        {row([("Source", False), (source_file or "Non définie", False), ("SHA-256", False), (source_sha256(source_file), False)])}
        {row([("Format", False), (results.get("source_metadata", {}).get("source_format", "détecté"), False), ("Échantillonnage", False), (f"{_number(rate)} Hz", False)])}
        {row([("Pas temporel", False), (f"{_number(metadata.get('dt_seconds'))} s", False), ("Intervalle analysé", False), (f"{_number(metadata.get('analysis_start_s', 0))}–{_number(metadata.get('analysis_end_s', metadata.get('duration_s')))} s", False)])}
        {row([("Méthode", False), (method.get("method", "Welch PSD + zero-upcrossing"), False), ("Version", False), (method.get("method_version", "—"), False)])}
        {row([("Fenêtre / segment", False), (f"{method.get('window', 'hann')} / {method.get('segment_length', '—')}", False), ("Recouvrement", False), (f"{_number(100 * float(method.get('overlap_ratio', 0)))} %", False)])}
        </tbody></table></section>"""

    notes = ""
    if config.get("description"):
        notes = f"<section><h2>7. Notes de l’analyste</h2><p>{html.escape(str(config['description']))}</p></section>"

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
@page {{ size:A4 landscape; margin:10mm; }}
body {{ font-family:'Segoe UI',Arial,sans-serif; color:#132d36; margin:0; font-size:8pt; }}
header {{ border-bottom:3px solid #087f99; padding:0 0 8px; margin-bottom:10px; }}
h1 {{ color:#092f3c; font-size:18pt; margin:0 0 5px; }}
h2 {{ color:#0a6278; font-size:11.5pt; margin:14px 0 5px; border-bottom:1px solid #9fb5bd; padding-bottom:3px; }}
.identity {{ display:table; width:100%; border-collapse:collapse; }} .identity span {{ display:table-cell; padding-right:14px; }}
.verdict {{ color:#8c3340; font-weight:700; font-size:10pt; text-align:right; }}
table {{ width:100%; border-collapse:collapse; page-break-inside:auto; }}
thead {{ display:table-header-group; }} tr {{ page-break-inside:avoid; }}
th {{ background:#123f4d; color:white; border:1px solid #315c69; padding:4px 3px; font-size:7pt; white-space:nowrap; }}
td {{ border:1px solid #c3d0d5; padding:3px; vertical-align:top; }} td.num {{ text-align:right; font-family:Consolas,monospace; }}
tr:nth-child(even) td {{ background:#f1f5f6; }} tr.rejected td:last-child {{ color:#a13240; font-weight:700; }}
tr.pending td:last-child {{ color:#95610e; font-weight:700; }} tr.accepted td:last-child {{ color:#116e54; font-weight:700; }}
.facts td:nth-child(odd) {{ background:#e5edef; font-weight:700; width:12%; }}
.facts td:nth-child(even) {{ font-family:Consolas,monospace; }}
.technical-note {{ color:#526b75; font-size:7.5pt; margin:4px 0; }}
.spectral-section {{ page-break-before:always; }}
.figure-page {{ page-break-inside:avoid; }} figure {{ page-break-inside:avoid; margin:8px 0 14px; }}
figure img {{ width:100%; max-height:165mm; object-fit:contain; }} figcaption {{ color:#425d67; font-size:7.5pt; text-align:center; }}
.quality-section {{ page-break-inside:avoid; }} .quality td:last-child {{ width:48%; }}
.quality td:nth-child(1), .quality td:nth-child(2), .quality td:nth-child(3) {{ white-space:nowrap; }}
.traceability-section, .traceability-section table {{ page-break-inside:avoid; }}
</style></head><body>
<header><h1>{report_title}</h1><div class="identity">
<span><b>Projet</b><br>{html.escape(str(project.get("name", "CHNeoWave")))}</span>
<span><b>Essai / référence</b><br>{html.escape(str(config.get("test_id") or "Non renseigné"))}</span>
<span><b>Source</b><br>{html.escape(source_name)}</span>
<span><b>Opérateur</b><br>{html.escape(str(config.get("author") or project.get("manager") or "Non renseigné"))}</span>
<span><b>Date</b><br>{html.escape(str(config.get("date") or "Non renseignée"))}</span>
<span class="verdict">DÉCISION INGÉNIEUR<br>{overall}</span></div></header>
<section><h2>1. Statistiques temporelles et hauteurs par voie</h2>
<p class="technical-note"><b>Définitions :</b> N = nombre d’échantillons analysés par voie (N = fréquence × durée). σ = dispersion des valeurs autour de la moyenne. RMS = valeur efficace √moyenne(x²). Min/Max signal sont les extrêmes de la série. Hmin, Hmoy, H1/3 et Hmax sont calculées sur les vagues individuelles détectées par zero-upcrossing.</p>
<table><thead><tr><th>Voie</th><th>Unité</th><th>N échant.</th><th>Moy. signal</th><th>σ</th><th>RMS</th><th>Min signal</th><th>Max signal</th><th>Hmin</th><th>Hmoy</th><th>H1/3</th><th>Hmax</th><th>N vagues</th><th>Décision ingénieur</th></tr></thead><tbody>{"".join(temporal_rows)}</tbody></table></section>
<div style="page-break-before:always"></div>
<section class="spectral-section"><h2>2. Étude spectrale par voie</h2>
<table><thead><tr><th>Voie</th><th>Hm0</th><th>fpic (Hz)</th><th>Tp (s)</th><th>Tm01 (s)</th><th>Tm02 (s)</th><th>Te (s)</th><th>m0</th><th>Δf (Hz)</th><th>Segments K</th><th>DDL ≈</th><th>Diagnostic auto</th><th>Décision ingénieur</th></tr></thead><tbody>{"".join(spectral_rows)}</tbody></table></section>
{"".join(figure_blocks) or '<section class="figure-page"><h2>3. Figures scientifiques</h2><p>Aucune figure disponible.</p></section>'}
<div style="page-break-before:always"></div><section class="quality-section"><h2>4. Diagnostic qualité et limites d’interprétation</h2>
<table class="quality"><thead><tr><th>Voie</th><th>Diagnostic auto</th><th>Décision ingénieur</th><th>Variance PSD/temps</th><th>Stationnarité</th><th>Cycles au pic</th><th>Éch./période</th><th>Alertes automatiques</th></tr></thead><tbody>{"".join(quality_rows)}</tbody></table></section>
<section><h2>5. Règles d’interprétation</h2><p>Un Tp marqué À CONFIRMER demande l’examen de l’ingénieur et du plan d’essai. Les hauteurs de houle ne sont interprétables que pour une voie d’élévation identifiée, étalonnée et exprimée dans une unité de longueur. Une différence d’amplitude entre sondes n’est jamais, à elle seule, un motif de rejet : la position et la réponse locale attendue doivent être prises en compte. Toute saturation, portion plate, non-stationnarité ou alerte de calibration doit être documentée avant la décision finale.</p></section>
{traceability}{notes}</body></html>"""
