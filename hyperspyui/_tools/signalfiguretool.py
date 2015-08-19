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
            return None
        return sw.signal

    def _is_nav(self, event):
        sw = self._get_wrapper(event.inaxes.figure)
        if sw.signal._plot.navigator_plot is not None:
            nav_ax = sw.signal._plot.navigator_plot.ax
            return nav_ax == event.inaxes
        return False

    def _is_sig(self, event):
        sw = self._get_wrapper(event.inaxes.figure)
        if sw.signal._plot.signal_plot is not None:
            sig_ax = sw.signal._plot.signal_plot.ax
            return sig_ax == event.inaxes
        return False

    def _get_axes(self, event):
        sw = self._get_wrapper(event.inaxes.figure)
        # Find out which axes of Signal are plotted in figure
        am = sw.signal.axes_manager
        if self._is_sig(event):
            axes = am.signal_axes
        elif self._is_nav(event):
            axes = am.navigation_axes
        else:
            return
        return axes
