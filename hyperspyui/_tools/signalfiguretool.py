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
Created on Fri May 22 12:10:20 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui._tools.figuretool import FigureTool


class SignalFigureTool(FigureTool):

    def __init__(self, windows=None):
        super().__init__(windows)

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
        if (sw.signal._plot is not None and
                sw.signal._plot.navigator_plot is not None):
            nav_ax = sw.signal._plot.navigator_plot.ax
            return nav_ax == event.inaxes
        return False

    def _is_sig(self, event):
        sw = self._get_wrapper(event.inaxes.figure)
        if (sw.signal._plot is not None and
                sw.signal._plot.signal_plot is not None):
            sig_ax = sw.signal._plot.signal_plot.ax
            return sig_ax == event.inaxes
        return False

    def _get_axes(self, event):
        sw = self._get_wrapper(event.inaxes.figure)
        # Find out which axes of Signal are plotted in figure
        if not sw or not sw.signal:
            return None
        am = sw.signal.axes_manager
        if self._is_sig(event):
            axes = am.signal_axes
        elif self._is_nav(event):
            axes = am.navigation_axes
        else:
            return None
        return axes
