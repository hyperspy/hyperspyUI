# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 11:35:49 2015

@author: Vidar Tonaas Fauske
"""

import os

from hyperspyui.plugins.plugin import Plugin
from hyperspy.roi  import BaseInteractiveROI
from hyperspyui.tools import LineTool


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
            print(roi.length)
        else:
            print(roi)
        # Finished with tool, so turn off
        self.tool.cancel()

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
        return os.path.dirname(__file__) + '/../images/crop.svg'
