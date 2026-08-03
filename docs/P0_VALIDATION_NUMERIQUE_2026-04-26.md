# Preuves numeriques P0 - CHNeoWave

Date: 2026-04-26

Ce fichier accompagne `P0_SCIENTIFIC_DIFF_2026-04-26.patch`.

## Verdict de revue

P0 est accepte provisoirement comme corrige cote code et contrat de donnees.

Reserve maintenue: la calibration reelle reste a developper en P1. En P0, elle
est seulement securisee: le logiciel ne retourne plus de faux statut `ok` et
annonce explicitement `CALIBRATION_NOT_PERFORMED`.

## Commandes executees

```powershell
$env:PYTHONPATH='src'; python -m unittest discover -s tests
python -m compileall src\hrneowave
```

Resultat apres corrections de contrat de donnees:

```text
Ran 14 tests in 2.274s
OK
```

## Resultats numeriques observes

Signal analytique:

```text
eta(t) = sin(2*pi*f*t)
A = 1 m
f = 1 Hz
Fs = 100 Hz
```

Zero-crossing:

```text
Hs   = 2.000000000000
Hmax = 2.000000000000
Tm   = 1.000000000000
Tp   = 1.000000000000
```

PSD normalisee:

```text
m0   = 0.500000012688
Hm0  = 2.828427160634
4*sqrt(m0) = 2.828427160634
```

Goda SVD complexe:

```text
|Ai| = 1.044030650891
|Ar| = 0.320156211872
Kr   = 0.306654035107
```

Simulation pression:

```text
raw_min = -0.098042989497 V
raw_max = -0.068502461646 V
within_pm5 = True
```

## Statut scientifique

P0-1 zero-crossing: corrige et teste.

P0-2 PSD physique: corrigee sur periodogramme one-sided normalise, testee contre variance temporelle.

P0-3 faux nom Goda: `zero_crossing_metrics` est le nom canonique; `goda_metrics` reste un alias de compatibilite avec warning.

P0-4 pseudo-inverse complexe: corrigee avec transposee conjuguee.

P0-5 calibration: securisee mais non terminee. Le logiciel retourne `not_performed` et `CALIBRATION_NOT_PERFORMED`, pas une fausse calibration.

P0-6 simulation pression: corrigee en pression relative compatible avec la plage DAQ.

## Corrections residuelles ajoutees

Les points suivants etaient encore bloquants pour une validation scientifique
finale du contrat de donnees. Ils sont maintenant couverts par tests:

1. Le chargeur CSV selectionne uniquement la colonne exacte `time` ou les alias
   stricts `t`, `time_s`, `timestamp_s`. Il ne peut plus prendre `time_start`
   ou `time_end` comme axe temps.
2. Tout axe temps charge est valide contre `sample_rate_hz`: valeurs finies,
   monotonie stricte, `dt` median coherent avec `1/Fs`, et irregularite max
   inferieure a 1%.
3. Les signaux contenant `NaN` ou `Inf` sont refuses explicitement. Le code ne
   compresse plus silencieusement la serie temporelle avec `values[np.isfinite]`.
4. L'export CSV ecrit un sidecar `*.metadata.json` contenant le contrat
   scientifique complet: `sensor_id`, unites, calibration, formule de
   conversion et warnings.
5. Le round-trip HDF5 preserve `channel_metadata` et les metadonnees de
   calibration.
