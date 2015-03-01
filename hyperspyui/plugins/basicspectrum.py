# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 15:20:55 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.widgets.elementpicker import ElementPickerWidget
from hyperspyui.signallist import SignalList
from hyperspyui.threaded import Threaded
from hyperspyui.util import win2sig

import hyperspy.signals
import numpy as np


def tr(text):
    return QCoreApplication.translate("BasicSpectrumPlugin", text)


class Namespace:
    pass


class SignalTypeFilter(object):

    def __init__(self, signal_type, signal_list):
        self.signal_type = signal_type
        self.signal_list = signal_list

    def __call__(self, win, action):
        sig = win2sig(win, self.signal_list)
        valid = sig is None or isinstance(sig.signal, self.signal_type)
        action.setEnabled(valid)


class BasicSpectrumPlugin(Plugin):
    name = "Basic spectrum tools"

    def create_actions(self):
        self.add_action('remove_background', "Remove Background",
                        self.remove_background,
                        icon='power_law.svg',
                        tip="Interactively define the background, and " +
                            "remove it",
                        selection_callback=SignalTypeFilter(
                            hyperspy.signals.Spectrum, self.ui.signals))

        self.add_action('fourier_ratio', "Fourier Ratio Deconvoloution",
                        self.fourier_ratio,
                        icon='fourier_ratio.svg',
                        tip="Use the Fourier-Ratio method" +
                        " to deconvolve one signal from another",
                        selection_callback=SignalTypeFilter(
                            hyperspy.signals.EELSSpectrum, self.ui.signals))

        self.add_action('pick_elements', "Pick elements", self.pick_elements,
                        icon='periodic_table.svg',
                        tip="Pick the elements for the spectrum",
                        selection_callback=SignalTypeFilter(
                            (hyperspy.signals.EELSSpectrum,
                             hyperspy.signals.EDSSEMSpectrum,
                             hyperspy.signals.EDSTEMSpectrum),
                            self.ui.signals))

    def create_menus(self):
        self.add_menuitem("EELS", self.ui.actions['remove_background'])
        self.add_menuitem('EELS', self.ui.actions['fourier_ratio'])
        self.add_menuitem('Signal', self.ui.actions['pick_elements'])

    def create_toolbars(self):
        self.add_toolbar_button("EELS", self.ui.actions['remove_background'])
        self.add_toolbar_button("EELS", self.ui.actions['fourier_ratio'])
        self.add_toolbar_button("Signal", self.ui.actions['pick_elements'])

    def fourier_ratio(self):
        wrap = QWidget(self.ui)
        pickerCL = SignalList(self.ui.signals, wrap, False)
        pickerLL = SignalList(self.ui.signals, wrap, False)
        grid = QGridLayout(wrap)
        grid.addWidget(QLabel(tr("Core loss")), 1, 1)
        grid.addWidget(QLabel(tr("Low loss")), 1, 2)
        grid.addWidget(pickerCL, 2, 1)
        grid.addWidget(pickerLL, 2, 2)
        wrap.setLayout(grid)

        diag = self.ui.show_okcancel_dialog("Select signals", wrap, True)

        if diag.result() == QDialog.Accepted:
            s_core = pickerCL.get_selected()
            s_lowloss = pickerLL.get_selected()

            # Variable to store return value in
            ns = Namespace()
            ns.s_return = None

#            s_core.signal.remove_background()
            def run_fr():
                ns.s_return = s_core.signal.fourier_ratio_deconvolution(
                    s_lowloss.signal)
                ns.s_return.data = np.ma.masked_array(ns.s_return.data,
                                                      mask=(np.isnan(ns.s_return.data) |
                                                            np.isinf(ns.s_return.data)))

            def fr_complete():
                self.ui.add_signal_figure(ns.s_return, 
                                          s_core.name + "[Fourier-ratio]")

            t = Threaded(self.ui, run_fr, fr_complete)
            t.run()
        pickerCL.unbind(self.ui.signals)
        pickerLL.unbind(self.ui.signals)

    def remove_background(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        signal.run_nonblock(signal.signal.remove_background,
                            "Background removal tool")

    def pick_elements(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()

        ptw = ElementPickerWidget(signal, self.ui)
        ptw.show()
