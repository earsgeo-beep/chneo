Scientific analysis workstation
===============================

Purpose
-------

The processing workspace is an operator-controlled scientific instrument, not
an administrative dashboard. It keeps the acquired record immutable, makes
every numerical choice explicit, and separates a computed value from a value
that is physically reliable.

Implemented workflow
--------------------

The operator can select:

* the exact time interval used by every channel, cross-spectrum and optional
  incident/reflected separation;
* presets of 30 seconds, 1, 5 or 10 minutes, a custom interval, and previous/
  next-window navigation; records longer than 10 minutes open on a readable
  5-minute view while the complete record remains selectable;
* the Welch segment length, overlap, window, mean or median aggregation,
  zero-padding factor and frequency band;
* no detrending, mean removal or linear detrending;
* optional zero-phase Butterworth low-pass, high-pass, band-pass and band-stop
  filtering using second-order sections;
* one active channel or an all-channel overlay;
* physical units or original voltage when a RAW import contains both;
* physical, centred, analysis-conditioned or display-only normalised temporal
  traces;
* PSD, ASD, PSD in dB or cumulative energy with linear/logarithmic axes and an
  approximate 95 percent confidence band for mean Welch aggregation;
* a selected-channel spectrogram with dynamic range and perceptual colour-map
  controls.

The PyQtGraph instrument toolbar is present on every scientific figure. Cursor,
interval selection, rectangle zoom, pan, grid, legend, fit-to-data and PNG/SVG
export work without modifying the source record. Long records are clipped to
the visible X range and downsampled with a min/max preserving method for fast
display; calculations always use the selected source samples, not the display
decimation.

Resolution semantics
--------------------

The displayed ``Rayleigh`` resolution is ``Fs / nperseg`` and is governed by
segment duration. The distinct ``frequency_bin_spacing`` is ``Fs / nfft``.
Zero-padding refines the frequency grid and peak interpolation but is never
reported as an improvement of physical spectral resolution.

Scientific results
------------------

Results are organised with one row per channel. The workspace exposes:

* time statistics: sample count, mean, standard deviation, RMS, extrema,
  skewness and kurtosis;
* spectral values: Hm0, peak frequency, Tp, Tm01, Tm02, Te, m0, frequency
  resolution, Welch segment count and approximate degrees of freedom;
* quality evidence: time/spectral variance ratio, block stationarity ratio,
  cycles at the spectral peak, samples per peak period, flat-run percentage
  and linear trend;
* cross-channel coherence, phase and lag;
* optional multi-probe incident/reflected separation when calibration,
  positions and water depth are complete.

Validity rules
--------------

``Tp`` remains stored numerically for traceability, but the user interface and
report mark it ``NON FIABLE`` when the peak touches an analysis-band boundary,
when fewer than ten samples describe a peak period, or when fewer than ten peak
cycles occur in the selected record.

Automatic checks only produce evidence levels (nominal, warning or critical).
They never accept or reject a probe. The engineer's decision remains explicit
because probe response can legitimately differ with model geometry and probe
position. Wave-height interpretation also requires an identified elevation
sensor, a length unit and a valid calibration.

Scientific report and exports
-----------------------------

The PDF, HTML and TXT reports contain source identity and SHA-256, acquisition
timing, selected interval, numerical method and version, Welch settings,
spectral confidence assumptions, detailed results and moments per channel,
quality warnings, cross-spectral results, multi-probe status, interpretation
limits and a spectral figure. JSON and HDF5 remain the complete machine-readable
records. CSV includes global configuration, metadata, quality indicators,
spectral moments and the principal scalar results.

Next scientific increments
--------------------------

The following increments are intentionally not presented as implemented:

* filter-response magnitude/phase plots and before/after overlay;
* spike, clipping and dropout event annotation on the time axis;
* wavelet time-frequency analysis;
* interactive coherence and phase dashboards for arbitrary channel pairs;
* propagation of calibration uncertainty into amplitudes and wave parameters;
* repeatability comparisons between several runs and ensemble confidence
  intervals;
* directional spectra for a qualified probe array;
* signed review workflow with analyst conclusion and immutable report manifest.

These functions should only be added with reference datasets, method-level
tests and an explicit algorithm version in the exported record.

Method references
-----------------

* `SciPy Welch PSD documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_
* `SciPy Butterworth filter documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>`_
* `SciPy zero-phase SOS filtering documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html>`_
* `SciPy ShortTimeFFT documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html>`_
* `PyQtGraph PlotDataItem documentation <https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html>`_
* `SciPy cross-spectral density documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.csd.html>`_
* `ITTC 7.5-02-07-01.2, Laboratory Modelling of Waves <https://www.ittc.info/media/9697/75-02-07-012.pdf>`_

Validated interface captures
----------------------------

The following captures were rendered from the real 9-channel, 32 Hz legacy RAW
record supplied for validation, using a 300-second interval:

* ``screenshots/v7/analysis-time-window.png``;
* ``screenshots/v7/analysis-spectrum-controls.png``;
* ``screenshots/v7/analysis-spectrogram.png``.
