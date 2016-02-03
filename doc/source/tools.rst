
.. _tools-section:
    
Tools
===========

Tools are different from actions, in that they listen for mouse or keyboard
input on the figures. For example a click and drag manouver to specify a 
region of interest (ROI). Most tools need to be selected to work, as they 
need exclusive access to the input, but some will simply listen for a a key
press in all figures.




Plot tools
--------------------------

Pan/Zoom tool
""""""""""""""""""""""""""
Use the pan/zoom tool to zoom and pan the matplotlib figure plots. Zooming
can be done either by the mouse wheel, or by clicking and dragging with the
right mouse button. To pan, click and drag with the left mouse button.


Home tool
""""""""""""""""""""""""""
Use this tool to reset the pan and zoom of the figure. Either click the button
while the plot in question is active, or press '5' on the keyboard/numpad.

Pointer tool
""""""""""""""""""""""""""
If you've used any other tool that is looking for mouse clicks in a figure,
select this tool to return to a standard cursor.





Signal tools
--------------------------

Crop tool
""""""""""""""""""""""""""
Use the crop tool by clicking and dragging on a signal figure to define an
ROI. The ROI can be moved and resized afterwards. Once you are satisfied with
the selection, press ``Enter`` to crop the signal to only include the selected
area.


.. _alignment-tool:

Alignment tool
""""""""""""""""""""""""""
The alignment tool algins a signal by a registration algorithm. To use it
click and drag to define an ROI which contains one or more features that 
can be used for alignment. The smaller the area, the speedier it operates.

The tool works in either one or two dimensions, relying on 
:py:meth:`hyperspy.signal.Signal1DTools.align1D` and
:py:meth:`hyperspy.signal.Signal2DTools.align2D` under the hood.

.. note::
    To ensure a successfull alignment, a significant portion of the alignment
    feature(s) need to stay within the ROI for the entire sequence. If your
    data is shifting too much, consider using :ref:`manual-alignment`
    to perform an initial coarse-alignment.

A variety of settings for this tool is available in the
:ref:`alignment-settings`.


.. _alignment-horz:

Align horizontal tool
""""""""""""""""""""""""""
Similar to :ref:`alignment-tool`, but is restricted to aligning images in 
the horizontal direction only.


.. _alignment-vert:

Align vertical tool
""""""""""""""""""""""""""
Similar to :ref:`alignment-tool`, but is restricted to aligning images in 
the vertical direction only.




Spectrum tools
--------------------------

Gaussian tool
""""""""""""""""""""""""""
The gaussian tool allows for quick addition and removal of gaussians to a
one-dimensional model. There are two ways to add a gaussian with this tool:
    
    - Click and drag in the spectrum to define a signal range in which
      the gaussian will be fitted.
    - Double click on the spectrum where there is a peak. This will create a
      gaussian at that position with height equal to the spectrum value at 
      that point (`i.e.` only the horizontal position need to be accurate).

The gaussian wil be of the type 
:py:class:`~hyperspy.model.components.gaussianhf.GaussianHF`, and will be added
to the currently selected model of the signal. If no model exists, a model will
be added. The :ref:`plot-components` option will also be turned on.

Additionally, right-clicking on a gaussian component with this tool will remove
that gaussian from the model.


Regression tool
""""""""""""""""""""""""""
A simple click and drag regression tool for one-dimenional plots. It will
add a regression line and regression result directly on the plot. Replot
the signal to remove.




EDS tools
--------------------------

Element picker tool
""""""""""""""""""""""""""
The element picker tool allows you to click anywhere in an 
:py:class:`~hyperspy.signals.EDSSpectrum`, and a list will pop up showing
the xray lines that are nearest in energy to point where you clicked. The list
is sorted by their closeness in energy, and includes minor lines as well. For
this reason, the list should be examined critically. The results are all within
a given energy window away from the point clicked as defined by 
:py:func:`~hyperspy.misc.eds.utils.get_xray_lines_near_energy`.

Selecting a line in the list will add the element that the line belongs to,
to the signal.


