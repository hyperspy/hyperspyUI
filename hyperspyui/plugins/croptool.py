# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 02:03:23 2014

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

import os
import numpy as np

from hyperspy.roi import BaseInteractiveROI
from hyperspyui.tools import SelectionTool
from hyperspyui.util import load_cursor


class CropToolPlugin(Plugin):
    name = "Crop tool"

    def create_tools(self):
        self.tool = CropTool()
        self.tool.accepted[BaseInteractiveROI].connect(self.crop)
        self.add_tool(self.tool, self.ui.select_signal)

    def crop(self, roi, signal=None, axes=None):
        if signal is None:
            f = self.tool.widget.ax.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            signal = sw.signal
        sig_axes = signal.axes_manager._axes
        if axes is None:
            axes = self.tool.axes
        else:
            old_axes = axes
            axes = []
            for a in old_axes:
                axes.append(sig_axes[a])
        slices = roi._make_slices(sig_axes, axes)
        new_offsets = np.array(roi.coords)[:, 0]
        signal.data = signal.data[slices]
        for i, ax in enumerate(axes):
            signal.axes_manager[ax.name].offset = new_offsets[i]
        signal.get_dimensions_from_data()
        signal.squeeze()

        self.record_code("s_crop = ui.get_selected_signal()")
        self.record_code("axes = " +
                         str(tuple([sig_axes.index(a) for a in axes])))
        self.record_code("roi = utils.roi." + str(roi))
        self.record_code("<p>.crop(roi, s_crop, axes)")
        self.tool.cancel()   # Turn off functionality as we are finished


class CropTool(SelectionTool):

    """
    Tool to crop signal interactively. Simply click and drag in a figure to
    create an ROI, and then press enter to apply cropping operation, or ESC to
    abort cropping. The cropping can also be aborted simply by selecting a
    different tool.
    """

    def get_name(self):
        return "Crop tool"

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/crop.svg'

    def make_cursor(self):
        return load_cursor(os.path.dirname(__file__) +
                           '/../images/crop.svg', 8, 8)
