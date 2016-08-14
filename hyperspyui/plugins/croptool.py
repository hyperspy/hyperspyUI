# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Sun Dec 07 02:03:23 2014

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

import os

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
        signal.data = signal.data[slices]
        if roi.ndim > 0:
            signal.axes_manager[axes[0]].offset = roi.left
        if roi.ndim > 1:
            signal.axes_manager[axes[1]].offset = roi.top

        signal.squeeze()
        signal.get_dimensions_from_data()
        signal.events.data_changed.trigger(signal)

        self.record_code("s_crop = ui.get_selected_signal()")
        self.record_code("axes = " +
                         str(tuple([sig_axes.index(a) for a in axes])))
        self.record_code("roi = hs.roi." + str(roi))
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
