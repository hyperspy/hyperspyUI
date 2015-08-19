from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs
from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.tools import SelectionTool

from hyperspy.roi import BaseInteractiveROI


class AlignPlugin(Plugin):
    name = "Align"

    def create_tools(self):
        tools = []

        # 1D tool
        self.tool_1D = SelectionTool(
            name='Align 1D tool', icon="align1d.svg",
            description="Align spectra across the stack")
        self.tool_1D.accepted[BaseInteractiveROI].connect(self.align_1D)
        self.tool_1D.valid_dimensions = (1,)
        tools.append(self.tool_1D)

        # 2D tool
        self.tool_2D = SelectionTool(
            name='Align 2D tool', icon="align2d.svg",
            description="Align images across the stack")
        self.tool_2D.accepted[BaseInteractiveROI].connect(
            self.align_2D)
        tools.append(self.tool_2D)

        # Vertical 2D align
        self.tool_vertical = SelectionTool(
            name='Align vertical tool', icon="align_vertical.svg",
            description="Align an image feature vertically across the stack")
        self.tool_vertical.accepted[BaseInteractiveROI].connect(
            self.align_vertical)
        tools.append(self.tool_vertical)

        # Vertical 2D align
        self.tool_horizontal = SelectionTool(
            name='Align horizontal tool', icon="align_horizontal.svg",
            description="Align an image feature horizontally across the stack")
        self.tool_horizontal.accepted[BaseInteractiveROI].connect(
            self.align_horizontal)
        tools.append(self.tool_horizontal)

        for t in tools:
            t.cancel_on_accept = True
            self.add_tool(t, self.ui.select_signal)

    @staticmethod
    def _smooth(y, box_pts):
        box = np.ones(box_pts) / box_pts
        y_smooth = np.convolve(y, box, mode='valid')
        return y_smooth

    def _get_signal(self, signal):
        if signal is None:
            return self.ui.get_selected_signal()
        return signal

    def align_1D(self, roi=None, signal=None):
        signal = self._get_signal(signal)
        if signal is None:
            return
        shifts = signal.estimate_shift1D(
            reference='current',
            roi=(roi.left, roi.right),
            show_progressbar=True)
        s_aligned = signal.deepcopy()
        s_aligned.align1D(shifts=shifts, expand=True)
        s_aligned.plot()
        return s_aligned

    def align_2D(self, roi=None, signal=None):
        signal = self._get_signal(signal)
        if signal is None:
            return
        shifts = signal.estimate_shift2D(
            reference='current',
            roi=(roi.left, roi.right, roi.top, roi.bottom),
            show_progressbar=True)
        s_aligned = signal.deepcopy()
        s_aligned.align2D(shifts=shifts, expand=True)
        s_aligned.plot()
        return s_aligned

    def align_vertical(self, roi=None, signal=None):
        signal = self._get_signal(signal)
        if signal is None:
            return
        return self._align_along_axis(roi, signal, axis=1)

    def align_horizontal(self, roi=None, signal=None):
        signal = self._get_signal(signal)
        if signal is None:
            return
        return self._align_along_axis(roi, signal, axis=0)

    def _align_along_axis(self, roi, signal, axis):
        daxis = signal.axes_manager.signal_axes[axis]
        s_al = roi(signal).sum(axis=daxis.index_in_array+3j)
        s_al.change_dtype(float)
        s_al.unfold()   # Temp signal, so don't need to refold
        # Check that signal axis is last dimension
        if s_al.axes_manager.signal_axes[0].index_in_array < 1:
            s_al.data = s_al.data.T             # Unfolded, so simply transpose
        # From now on, navigation is in first dimension
        d = np.array([self._smooth(s_al.data[i, :], 50)
                      for i in xrange(s_al.data.shape[0])])
        d = np.diff(d, axis=1)      # Differentiate to highlight edges
        sz = d.shape                # Initial shape
        ref = d[0, :]               # Reference row
        # Pad reference with +/- half size at each ends (maximum shift allowed)
        ref = np.pad(ref, (sz[1] / 2, sz[1] / 2), 'edge')
        # Set shift of reference to compensate for padding
        shifts = [sz[1] / 2]
        # Find shifts for each row
        for row in xrange(1, sz[0]):
            corr = np.correlate(ref, d[row, :], 'valid')
            shifts.append(corr.argmax())
        # Remove "padding" from found shifts
        shifts = np.array(shifts) - sz[1] / 2
        # Pad for both x and y shifts, but zero unused one:
        shifts = np.tile(-shifts, (2, 1)).T
        shifts[:, axis] = 0.0
        # Apply shifts using hyperspy routine:
        s_aligned = signal.deepcopy()
        s_aligned.align2D(shifts=shifts, crop=False, expand=True)
        s_aligned.plot()
        return s_aligned
