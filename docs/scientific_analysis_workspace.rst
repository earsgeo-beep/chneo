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
* the Welch segment length, overlap, window and frequency band;
* linear detrending before spectral and zero-upcrossing analysis;
* one active channel or an all-channel overlay;
* physical units or original voltage when a RAW import contains both;
* centred display, mean and standard-deviation guides;
* logarithmic or linear PSD scale, approximate 95 percent confidence band and
  cumulative spectral energy.

Interactive time, PSD and incident/reflected plots use PyQtGraph 0.14. They
provide native wheel zoom, drag navigation, high-volume peak downsampling,
crosshair readout, automatic range, selectable analysis interval and PNG
export without modifying the source record. Matplotlib remains the static
publication backend used by the reproducible scientific report.

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

A channel is rejected when the signal is constant, contains a prolonged flat
portion, or has a block-variance ratio above the stationarity threshold. Other
warnings produce an ``A VERIFIER`` verdict. Wave-height interpretation also
requires an identified elevation sensor, a length unit and a valid calibration.

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

* non-destructive filter previews with original/filtered comparison and filter
  response plots;
* spike, clipping and dropout event annotation on the time axis;
* spectrogram/STFT and wavelet time-frequency analysis;
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
* `SciPy cross-spectral density documentation <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.csd.html>`_
* `ITTC 7.5-02-07-01.2, Laboratory Modelling of Waves <https://www.ittc.info/media/9697/75-02-07-012.pdf>`_
