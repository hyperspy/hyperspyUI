# -*- coding: utf-8 -*-
# Copyright 2007-2016 The HyperSpyUI developers
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
Created on Sun Mar 01 15:20:55 2015

@author: Vidar Tonaas Fauske
"""

import sys

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


def tr(text):
    return QCoreApplication.translate("BasicSignalPlugin", text)


class BasicSignalPlugin(Plugin):
    name = "Basic signal tools"

    def __init__(self, *args, **kwargs):
        super(BasicSignalPlugin, self).__init__(*args, **kwargs)
        self.settings.set_default('histogram_bins_method', 'freedman')

    def create_actions(self):
        self.add_action('stats', tr("Statistics"),
                        self.statistics,
                        icon=None,
                        tip=tr("Print the signal statistics to the console."),
                        selection_callback=self.ui.select_signal)

        self.add_action('histogram', tr("Histogram"),
                        self.histogram,
                        icon=None,
                        tip=tr("Plot a histogram of the signal."),
                        selection_callback=self.ui.select_signal)

        self.add_action('mean', tr("Mean"),
                        self.mean,
                        icon=None,
                        tip=tr("Plot the mean of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('sum', tr("Sum"),
                        self.sum,
                        icon='sum.svg',
                        tip=tr("Plot the sum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('max', tr("Maximum"),
                        self.max,
                        icon=None,
                        tip=tr("Plot the maximum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('min', tr("Minimum"),
                        self.min,
                        icon=None,
                        tip=tr("Plot the sum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('std', tr("Std.dev."),
                        self.std,
                        icon=None,
                        tip=tr("Plot the standard deviation of the current "
                               "signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('var', tr("Variance"),
                        self.var,
                        icon=None,
                        tip=tr("Plot the variances of the current signal"),
                        selection_callback=self.ui.select_signal)

#        max, min, std, var, diff?, derivate?, integrate_simpson, integrate1D,
#        indexmax, valuemax

    def create_menu(self):
        self.add_menuitem("Signal", self.ui.actions['stats'])
        self.add_menuitem("Signal", self.ui.actions['histogram'])
        self.add_menuitem("Math", self.ui.actions['mean'])
        self.add_menuitem('Math', self.ui.actions['sum'])
        self.add_menuitem('Math', self.ui.actions['max'])
        self.add_menuitem('Math', self.ui.actions['min'])
        self.add_menuitem('Math', self.ui.actions['std'])
        self.add_menuitem('Math', self.ui.actions['var'])

    def statistics(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        # If we're using an external console for errors, we need to temporarily
        # redirect stdout
        _old_stdout = None
        if self.ui.settings['output_to_console', bool]:
            _old_stdout = sys.stdout
            sys.stdout = self.ui.console.kernel.stdout
        try:
            signal.print_summary_statistics()
            self.record_code("signal = ui.get_selected_signal()")
            self.record_code("signal.print_summary_statistics()")
        finally:
            if self.ui.settings['output_to_console', bool]:
                sys.stdout = _old_stdout

    def histogram(self, signal=None):
        signal = signal or self.ui.get_selected_signal()
        if signal is not None:
            method = self.settings['histogram_bins_method']
            signal.get_histogram(bins=method).plot()
            self.record_code("signal = ui.get_selected_signal()")
            self.record_code("histogram = signal.get_histogram(bins=%s)" %
                             method)

    def _np_method(self, name, signal):
        if signal is None:
            signal = self.ui.get_selected_signal()
        f = getattr(signal, name)
        try:
            f().plot()
        except TypeError:
            # hyperspy < 0.9 compatibility
            for ax in signal.axes_manager.navigation_axes:
                signal = f(ax.index_in_array + 3j)
            signal.plot()
        self.record_code("signal = ui.get_selected_signal()")
        self.record_code("result = signal.%s()" % name)

    def mean(self, signal=None):
        self._np_method('mean', signal)

    def sum(self, signal=None):
        self._np_method('sum', signal)

    def max(self, signal=None):
        self._np_method('max', signal)

    def min(self, signal=None):
        self._np_method('min', signal)

    def std(self, signal=None):
        self._np_method('std', signal)

    def var(self, signal=None):
        self._np_method('var', signal)
