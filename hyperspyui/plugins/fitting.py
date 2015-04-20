# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 00:23:43 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

import os
from scipy import stats
import numpy as np

from hyperspyui.tools import SelectionTool
from hyperspy.roi import BaseInteractiveROI
from hyperspy.utils.markers import line_segment, text


class FittingPlugin(Plugin):
    name = "Fitting plugin"

    def create_tools(self):
        self.reg_tool = RegressionTool()
        self.reg_tool.accepted[BaseInteractiveROI].connect(self.regression)
        self.add_tool(self.reg_tool, self.ui.select_signal)

    def regression(self, roi, signal=None, axes=None):
        if signal is None:
            f = self.reg_tool.widget.ax.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            signal = sw.signal
        sig_axes = signal.axes_manager._axes
        if axes is None:
            axes = self.reg_tool.axes
        else:
            axes = sig_axes[axes]

        i_ax = sig_axes.index(axes[0])
        slices = roi._make_slices(sig_axes, axes)
        for i, a in enumerate(sig_axes):
            if i != i_ax:
                slices[i] = a.index

        y = signal.data[slices]
        x = axes[0].axis[slices[i_ax]]

        # TODO: If in signal dim, iterate through navigation space
        reg = stats.linregress(x, y)
        x1, x2 = np.min(x), np.max(x)
        y1, y2 = np.array([x1, x2]) * reg[0] + reg[1]
        m_l = line_segment(x1, y1, x2, y2)
        signal.add_marker(m_l)
        m_t = text((x2+x1)*0.5, (y2+y1)*0.5,
                   "y = %.4gx + %.4g, R=%.4g" % reg[0:3])
        signal.add_marker(m_t)

        self.record_code("signal = ui.get_selected_signal()")
        self.record_code("axes = " +
                         str(tuple([sig_axes.index(a) for a in axes])))
        self.record_code("roi = utils.roi." + str(roi))
        self.record_code("<p>.regression(roi, signal, axes)")
        self.reg_tool.cancel()   # Turn off functionality as we are finished


class RegressionTool(SelectionTool):

    """
    """

    def __init__(self, windows=None):
        super(RegressionTool, self).__init__(windows)
        self.valid_dimensions = [1]

    def get_name(self):
        return "Regression tool"

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/regression.svg'
