# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 15:20:55 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


def tr(text):
    return QCoreApplication.translate("BasicSignalPlugin", text)


class BasicSignalPlugin(Plugin):
    name = "Basic signal tools"

    def create_actions(self):
        self.add_action('mean', "Mean Signal",
                        self.mean,
                        icon=None,
                        tip="Plot the mean of the current signal")

        self.add_action('sum', "Summed Signal",
                        self.sum,
                        icon=None,
                        tip="Plot the sum of the current signal")

    def create_menu(self):
        self.add_menuitem("Signal", self.ui.actions['mean'])
        self.add_menuitem('Signal', self.ui.actions['sum'])

    def mean(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        try:
            signal.mean().plot()
        except TypeError:
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
