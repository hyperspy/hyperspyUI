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
Created on Thu Jul 30 11:35:49 2015

@author: Vidar Tonaas Fauske
"""

import os

from hyperspyui.plugins.plugin import Plugin
from hyperspy.roi import BaseInteractiveROI
from hyperspyui._tools.linetool import LineTool


class LineMeasure(Plugin):
    name = "LineMeasure"

    def create_tools(self):
        self.tool = LineMeasureTool()
        self.tool.accepted[BaseInteractiveROI].connect(self.measure)
        self.tool.updated[BaseInteractiveROI].connect(self._continuous_update)
        self.add_tool(self.tool, self.ui.select_signal)

    def measure(self, roi):
        if self.tool.ndim == 2:
            self.ui.set_status("Line length: %G" % roi.length)

            s = self.tool._get_signal(self.tool.widget.ax.figure)
            roi(s).plot()
        else:
            print(roi)

    def _continuous_update(self, roi):
        if self.tool.ndim == 2:
            self.ui.set_status("Line length: %G" % roi.length)


class LineMeasureTool(LineTool):

    """
    Tool to crop signal interactively. Simply click and drag in a figure to
    create an ROI, and then press enter to apply cropping operation, or ESC to
    abort cropping. The cropping can also be aborted simply by selecting a
    different tool.
    """

    def get_name(self):
        return "Line measure"

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/ruler.svg'
