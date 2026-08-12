CHNeoWave instrument interface
==============================

Identity
--------

CHNeoWave is presented as a maritime measurement workstation, not as an
administrative dashboard. Its identity is built from an owned vector mark (a
probe crossing two wave layers), a consistent line-icon family and a compact
instrument density. Emoji, platform font symbols, decorative gradients,
glass effects and oversized dashboard cards are excluded from the production
interface.

The shell uses a collapsible 224/58 pixel navigation rail, a 60 pixel context
bar, one primary action per workspace and the largest possible scientific
plot area. Values use tabular numerals when the host font supports them.

Themes
------

Two production themes share exactly the same geometry:

``light``
   Mineral white work surfaces, Atlantic ink text and a dark navigation rail.

``dark``
   Deep ocean surfaces, high-contrast cyan traces and restrained amber warning
   states for low-light laboratory operation.

The selected theme is stored with Qt ``QSettings`` and can be changed from the
context bar. Plot backgrounds, axes, selection regions, cursors and icons are
updated at the same time as the Qt stylesheet.

Scientific graphics stack
-------------------------

The responsibilities are deliberately separated:

* PyQtGraph 0.14 renders interactive and potentially long live or imported
  signals using clipping and automatic peak downsampling;
* NumPy and SciPy perform numerical processing and never depend on the GUI;
* Matplotlib renders static figures intended for PDF/HTML reports;
* HDF5 remains the master laboratory record.

The August 2026 runtime baseline is Python 3.12+, PySide6 6.11, NumPy 2.5,
SciPy 1.18, Matplotlib 3.11, pandas 3 and h5py 3.16. This avoids coupling
acquisition performance to publication rendering while
preserving reproducibility. Dependency ranges are bounded in
``pyproject.toml``; a release must update them only after the full scientific
and Qt test suites pass on the supported Windows Python version.

Interaction contract
--------------------

Every interactive plot provides the same compact controls: measurement
cursor, interval selection where meaningful, automatic range and PNG export.
The mouse wheel zooms and drag navigation pans. On the time view, the selected
region writes the exact start/end values used by the analysis request. On the
PSD view, the spectral peak is a target marker and the approximate confidence
band and cumulative energy remain optional overlays.

Accessibility and safety
------------------------

Colour is never the only carrier of acquisition or quality state: every state
also has a textual verdict. Physical acquisition stays locked unless a real
qualified device is connected. Theme changes have no effect on data,
calibration, processing configuration or exported values.
