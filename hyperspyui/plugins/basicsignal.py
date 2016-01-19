# -*- coding: utf-8 -*-
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

    def create_actions(self):
        self.add_action('stats', tr("Statistics"),
                        self.statistics,
                        icon=None,
                        tip=tr("Print the signal statistics to the console."),
                        selection_callback=self.ui.select_signal)

        self.add_action('mean', tr("Mean Signal"),
                        self.mean,
                        icon=None,
                        tip=tr("Plot the mean of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('sum', tr("Summed Signal"),
                        self.sum,
                        icon=None,
                        tip=tr("Plot the sum of the current signal"),
                        selection_callback=self.ui.select_signal)

    def create_menu(self):
        self.add_menuitem("Signal", self.ui.actions['stats'])
        self.add_menuitem("Signal", self.ui.actions['mean'])
        self.add_menuitem('Signal', self.ui.actions['sum'])

    def statistics(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        # If we're using an external console for errors, we need to temporarily
        # redirect stdout
        _old_stdout = None
        if self.ui.settings['Output to console'].lower() != 'true':
            _old_stdout = sys.stdout
            sys.stdout = self.ui.console.kernel.stdout
        try:
            signal.print_summary_statistics()
        finally:
            if self.ui.settings['Output to console'].lower() != 'true':
                sys.stdout = _old_stdout

    def mean(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        try:
            signal.mean().plot()
        except TypeError:
            # hyperspy < 0.9 compatibility
            for ax in signal.axes_manager.navigation_axes:
                signal = signal.mean(ax.index_in_array + 3j)
            signal.plot()

    def sum(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        try:
            signal.sum().plot()
        except TypeError:
            for ax in signal.axes_manager.navigation_axes:
                signal = signal.sum(ax.index_in_array + 3j)
            signal.plot()
