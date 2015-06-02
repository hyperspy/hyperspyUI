# -*- coding: utf-8 -*-
"""
Created on Fri May 22 12:10:20 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.tools import FigureTool


class SignalFigureTool(FigureTool):

    def __init__(self, windows=None):
        super(SignalFigureTool, self).__init__(windows)

    def _get_wrapper(self, figure):
        # We need to map figure to a hyperspy Signal:
        window = figure.canvas.parent()
        sw = window.property('hyperspyUI.SignalWrapper')
        return sw

    def _get_signal(self, figure):
        sw = self._get_wrapper(figure)
        if sw is None:
            return
        return sw.signal

    def _get_axes(self, event):
        sw = self._get_wrapper(event.figure)
        if sw.signal._plot.signal_plot is not None:
            sig_ax = sw.signal._plot.signal_plot.ax
        else:
            sig_ax = None
        if sw.signal._plot.navigator_plot is not None:
            nav_ax = sw.signal._plot.navigator_plot.ax
        else:
            nav_ax = None

        # Find out which axes of Signal are plotted in figure
        am = sw.signal.axes_manager
        if sig_ax == event.inaxes:
            axes = am.signal_axes
        elif nav_ax == event.inaxes:
            axes = am.navigation_axes
        else:
            return
        # Make sure we have a figure with valid dimensions
        if len(axes) not in self.valid_dimensions:
            return
        self.axes = axes
