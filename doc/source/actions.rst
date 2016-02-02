
Available actions
=================

Most menu entries and toolbar buttons trigger an `action` when clicked. This
is a rather loose definition, but actions are different from `tools`_ and
`widgets`_.

The list below is sorted on category, which roughly corresponds to the
toolbar/menu in which they appear.



File
-----------------

Open
"""""""""""""""
Open a dialog to let the user interactively browse for files. It then loads
these files using :py:meth:`hyperspy.io.load` before plotting the loaded
signals.

Open Stack
""""""""""""""""""""""""""""""""""""
Open files and combine the loaded signals into one signal (stacked).

Close
""""""""""""""""""""""""""""""""""""
Close the selected signal(s).

Save
""""""""""""""""""""""""""""""""""""
Save the selected signal(s).

Save figure
"""""""""""""""
Save the currently active figure using matplotlib's ``savefig()``. Note that
this does not care about how the figure was produced, or the underlying 
resolution of the data.

New editor
""""""""""""""""""""""""""""""""""""
Opens a new `code editor`_.

Close All (signals)
""""""""""""""""""""""""""""""""""""
Close all signals. This can sometimes help clear out signals that get stuck
in an invalid state.

Exit
"""""""""""""""
Close the application



Signal
-----------------

Signal type
"""""""""""""""
Changes the signal type using a combination of methods on
:py:class:`hyperspy.Signal`:

    * :py:meth:`~hyperspy.Signal.set_signal_type()`
    * :py:meth:`~hyperspy.Signal.set_signal_origin()`
    * and by converting with :py:meth:`~hyperspy.Signal.as_image()` and
      :py:meth:`~hyperspy.Signal.as_spectrum()`.

Signal data type
""""""""""""""""""""""""""""""""""""
Change the data type use to store the signal data internally.

Manual align
""""""""""""""""""""""""""""""""""""
Interactively align the signal.

Statistics
""""""""""""""""""""""""""""""""""""
Print the signal statistics to the console.

Histogram
""""""""""""""""""""""""""""""""""""
Plot a histogram of the signal.

Mirror navigation
""""""""""""""""""""""""""""""""""""
Mirror navigation axes of selected signals.

Share navigation
""""""""""""""""""""""""""""""""""""
Mirror navigation axes of selected signals, and keep only one navigator
plot.

Rebin
""""""""""""""""""""""""""""""""""""
Rebin the signal.



Model
-----------------

Create Model
"""""""""""""""
Add and plot a default model for the selected signal. Note that the
`Signal type`_ is important in order to create the correct model type.

The newly created model is accessible through the `DataWidget`_.


Add component
""""""""""""""""""""""""""""""""""""
Add a component to the currently selected model.

Plot components
"""""""""""""""
Trigger the plotting of each component together with the model, as performed
by :py:meth:`hyprespy.Model1D.enable_plot_components()`.

Adjust component positions
""""""""""""""""""""""""""
Add/remove widgets to adjust the position of the components in the model, as
performed by :py:meth:`hyprespy.Model1D.enable_adjust_position()`.



Decomposition
-----------------

PCA
"""""""""""""""
Performs decomposition if neccessary, then plots the scree for selecting the
number of components to use for a decomposition model. The selection is made
by clicking on the in the scree plot on the first component to
`not be included` in the decomposition. The scree plot will then automatically
close and the decomposition model plotted (see
:py:meth:`hyperspy.Signal.decomposition` and
:py:meth:`hyperspy.Signal.get_decomposition_model`).

BSS
"""""""""""""""

Performs decomposition if neccessary, then plots the scree for selecting the
number of components to use for a blind source separation. The selection
is made by clicking in the scree plot on the first component to
`not be included` in the decomposition. The scree plot will then automatically
close and the BSS algortihm run (see
:py:meth:`hyperspy.Signal.blind_source_separation` and
:py:meth:`hyperspy.Signal.plot_bss_results`).


Decomposition results
"""""""""""""""""""""

Performs decomposition if necessary, then plots the decomposition results
according to the hyperspy's
:py:meth:`hyperspy.Signal.plot_decomposition_results`.



Spectrum
-----------------

Smooth Savitzky-Golay
""""""""""""""""""""""""""""""""""""
Apply a Savitzky-Golay filter.

Smooth Lowess
""""""""""""""""""""""""""""""""""""
Apply a Lowess smoothing filter.

Smooth Total variation
""""""""""""""""""""""""""""""""""""
Total variation data smoothing.

Butterworth filter
""""""""""""""""""""""""""""""""""""
Apply a Butterworth filter.

Hanning taper
""""""""""""""""""""""""""""""""""""
Apply a Hanning taper to both ends of the data.



EELS
-----------------

Remove Background
""""""""""""""""""""""""""""""""""""
Interactively define the background, and remove it.

Fourier Ratio Deconvoloution
""""""""""""""""""""""""""""""""""""
Use the Fourier-Ratio method to deconvolve one signal from another.

Estimate thickness
""""""""""""""""""""""""""""""""""""
Estimates the thickness (relative to the mean free path) of a sample using the log-ratio method.

Browse EELSDB
""""""""""""""""""""""""""""""""""""
Browse the EELSDB online database of standard EEL spectra.



Image
-----------------

Gaussian Filter
""""""""""""""""""""""""""""""""""""
Apply a gaussian filter.

Rotate
""""""""""""""""""""""""""""""""""""
Rotate an image.



Diffraction
-----------------

Virtual aperture
""""""""""""""""""""""""""""""""""""
Add a virtual aperture to the diffraction image.

Virtual navigator
""""""""""""""""""""""""""""""""""""
Set the navigator intensity by a virtual aperture. Setting this, will replot
the signal, so any existing apertures will be lost.



Math
-----------------

Mean
""""""""""""""""""""""""""""""""""""
Plot the mean of the current signal.

Sum
""""""""""""""""""""""""""""""""""""
Plot the sum of the current signal.

Maximum
""""""""""""""""""""""""""""""""""""
Plot the maximum of the current signal.

Minimum
""""""""""""""""""""""""""""""""""""
Plot the sum of the current signal.

Std.dev.
""""""""""""""""""""""""""""""""""""
Plot the standard deviation of the current signal.

Variance
""""""""""""""""""""""""""""""""""""
Plot the variances of the current signal.


FFT
""""""""""""""""""""""""""""""""""""
Perform a fast fourier transform on the active part of the signal.

Live FFT
"""""""""""""""
Perform a fast fourier transform on the active part of the signal. The live
FFT updates the FFT as the signal is navigated.

Signal FFT
""""""""""""""""""""""""""""""""""""
Perform a fast fourier transform on the entire signal, not just the active
part.

Inverse FFT
""""""""""""""""""""""""""""""""""""
Perform an inverse fast fourier transform on the active part of the signal.

Inverse Signal FFT
""""""""""""""""""""""""""""""""""""
Perform an inverse fast fourier transform on the entire signal.



Plot
---------------

Tight layout
""""""""""""""""""""""""""""""""""""
Apply a tight layout to the selected plot.



Settings
-----------------

Version selector
""""""""""""""""""""""""""""""""""""
Open dialog to select branch/version of HyperSpy/HyperSpyUI.

Check for updates
""""""""""""""""""
Checks for updates to HyperSpy and HyperSpyUI. If the packages are not source
installs, it checks for a new version on `PyPI`_.

Plugin manager
""""""""""""""""""""""""""""""""""""
Show the plugin manager.

Reset layout
""""""""""""""""""""""""""""""""""""
Resets layout of toolbars and widgets.

HyperSpy settings
""""""""""""""""""""""""""""""""""""
Edit the HyperSpy package settings.

Edit settings
"""""""""""""""
Shows a dialog for editing the application and plugins settings.



Windows
-----------------

Tile
""""""""""""""""""""""""""""""""""""
Arranges all figures in a tile pattern.

Cascade
""""""""""""""""""""""""""""""""""""
Arranges all figures in a cascade pattern.


Close all (windows)
""""""""""""""""""""""""""""""""""""
Closes all matplotlib figures.

