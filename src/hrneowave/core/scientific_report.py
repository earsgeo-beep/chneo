"""Scientific, auditable rendering of CHNeoWave analysis results."""

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


def quality_label(indicators: dict[str, Any]) -> str:
    """Map the machine status to an unambiguous laboratory verdict."""

    return {
        "valid": "VALIDE",
        "warning": "À VÉRIFIER",
        "rejected": "REJETÉ",
    }.get(
        str(indicators.get("status", "")),
        "VALIDE" if not indicators.get("warnings") else "À VÉRIFIER",
    )


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
    return str(
        item.get("physical_unit")
        or item.get("physical_units")
        or item.get("unit")
        or "unité"
    )


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
    overall = "VALIDE"
    if any(quality_label(quality.get(channel, {})) == "REJETÉ" for channel in channels):
        overall = "PARTIELLEMENT REJETÉ"
    elif any(quality_label(quality.get(channel, {})) == "À VÉRIFIER" for channel in channels):
        overall = "À VÉRIFIER"

    lines = [
        config.get("title") or "Rapport scientifique CHNeoWave",
        f"Verdict global: {overall}",
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
        f"Bande demandée: {_number(method.get('min_frequency', 0))} à "
        f"{_number(maximum_frequency)} Hz",
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
            else f"NON FIABLE (valeur calculée: {_number(channel_waves.get('Tp'))} s)"
        )
        lines.extend(
            [
                f"[{channel}] · {quality_label(indicators)} · unité: {_channel_unit(results, channel)}",
                f"  N={channel_stats.get('sample_count', metadata.get('n_samples', 0))}; "
                f"moyenne={_number(channel_stats.get('mean'))}; "
                f"écart-type={_number(channel_stats.get('std'))}; "
                f"RMS={_number(channel_stats.get('rms'))}; min/max={_number(channel_stats.get('min'))} / "
                f"{_number(channel_stats.get('max'))}",
                f"  Hm0={_number(spectrum.get('Hm0'))}; H1/3={_number(channel_waves.get('H1_3'))}; "
                f"Hmax={_number(channel_waves.get('H_max'))}; vagues={channel_waves.get('n_waves', 0)}",
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
            "Un Tp signalé NON FIABLE ne doit pas être utilisé: le pic touche une limite de bande, la "
            "résolution temporelle est insuffisante ou la durée contient moins de dix cycles.",
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
) -> str:
    """Render the scientific text as print-safe HTML with an optional PSD figure."""

    text = build_scientific_report_text(results, source_file, project_metadata, report_config)
    report_title = (report_config or {}).get("title") or "Rapport scientifique CHNeoWave"
    text_lines = text.splitlines()
    if text_lines and text_lines[0] == report_title:
        text_lines = text_lines[1:]
    escaped_lines = [html.escape(line) for line in text_lines]
    body: list[str] = []
    channel_block_open = False
    channel_index = 0
    for line in escaped_lines:
        if line and line[0].isdigit() and ". " in line[:4]:
            if channel_block_open:
                body.append("</div>")
                channel_block_open = False
            body.append(f'<h2>{line}</h2>')
        elif line.startswith("["):
            if channel_block_open:
                body.append("</div>")
            if channel_index == 1 or (channel_index > 1 and (channel_index - 1) % 4 == 0):
                body.append('<div style="page-break-before:always"></div>')
            body.append('<div class="channel">')
            channel_block_open = True
            channel_index += 1
            body.append(f'<h3>{line}</h3>')
        elif line.startswith("Verdict global:"):
            body.append(f'<p class="verdict">{line}</p>')
        elif line.startswith("  ALERTE:"):
            body.append(f'<p class="warning">{line.strip()}</p>')
        elif line.startswith("  "):
            body.append(f'<p class="metric">{line.strip()}</p>')
        elif line:
            body.append(f"<p>{line}</p>")
        else:
            body.append('<div class="spacer"></div>')
    if channel_block_open:
        body.append("</div>")
    plot = (
        '<div style="page-break-before:always">'
        f'<h2>Figure spectrale</h2><img class="plot" src="{spectral_plot_data_uri}" />'
        "</div>"
        if spectral_plot_data_uri
        else ""
    )
    report_title = html.escape(report_title)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; color:#172b35; margin:32px; font-size:10pt; }}
h1 {{ color:#123f4d; border-bottom:3px solid #1a7188; padding-bottom:10px; }}
h2 {{ color:#1a7188; font-size:15pt; border-bottom:1px solid #cbd8de; margin-top:24px; }}
h3 {{ color:#203843; font-size:11pt; background:#eef4f6; padding:7px; margin-bottom:5px; }}
p {{ margin:4px 0; }} .metric {{ margin-left:14px; font-family:Consolas, monospace; }}
.verdict {{ font-weight:700; font-size:12pt; color:#123f4d; }}
.warning {{ color:#9a4f00; margin-left:14px; font-weight:600; }}
.spacer {{ height:6px; }} .channel {{ page-break-inside:avoid; }}
.plot {{ width:100%; max-width:920px; }}
</style></head><body><h1>{report_title}</h1>
{''.join(body)}{plot}</body></html>"""
