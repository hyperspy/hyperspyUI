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
Created on Fri Dec 12 23:43:54 2014

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore
from qtpy.QtWidgets import QMessageBox

import hyperspy.api as hs

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.threaded import ProgressThreaded


def tr(text):
    return QtCore.QCoreApplication.translate("FFT", text)


class FFT_Plugin(Plugin):
    name = 'FFT'

    def create_actions(self):
        self.add_action('fft', "FFT", self.fft,
                        icon='fft.svg',
                        tip="Perform a fast fourier transform on the " +
                        "active part of the signal",
                        selection_callback=self.ui.select_signal)

        self.add_action('live_fft', "Live FFT", self.live_fft,
                        icon='live_fft.svg',
                        tip="Perform a fast fourier transform on the " +
                        "active part of the signal, and link it to the " +
                        "navigator",
                        selection_callback=self.ui.select_signal)

        self.add_action('ifft', "Inverse FFT", self.ifft,
                        icon='ifft.svg',
                        tip="Perform an inverse fast fourier transform on " +
                            "the active part of the signal",
                        selection_callback=self.ui.select_signal)

        self.add_action('get_real_image', "Real and imaginary",
                        self.get_real_image,
                        icon=None,
                        tip="Decompose a fast fourier transformation result " +
                        "into its real and imaginary part.",
                        selection_callback=self.ui.select_signal)

        self.add_action('get_amplitude_phase', "Amplitude and phase",
                        self.get_amplitude_phase,
                        icon=None,
                        tip="Decompose a fast fourier transformation result " +
                        "into its amplitude and phase.",
                        selection_callback=self.ui.select_signal)

    def create_menu(self):
        self.add_menuitem("Math", self.ui.actions['fft'])
        self.add_menuitem("Math", self.ui.actions['live_fft'])
        self.add_menuitem("Math", self.ui.actions['ifft'])
        self.add_menuitem("Math", self.ui.actions['get_real_image'])
        self.add_menuitem("Math", self.ui.actions['get_amplitude_phase'])

    def create_toolbars(self):
        self.add_toolbar_button("Math", self.ui.actions['fft'])
        self.add_toolbar_button("Math", self.ui.actions['live_fft'])
        self.add_toolbar_button("Math", self.ui.actions['ifft'])

    def fft(self, signals=None, shift=True, power_spectrum=True, inverse=False,
            on_complete=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        if isinstance(signals, hs.signals.BaseSignal):
            signals = (signals,)

        fftsignals = []

        def do_ffts():
            for i, signal in enumerate(signals):
                if inverse:
                    fft = signal.ifft(shift=shift)
                else:
                    fft = signal.fft(shift=shift)
                fftsignals.append(fft)
                yield i + 1

        def on_ffts_complete():
            for fs in fftsignals:
                fs.plot(power_spectrum=power_spectrum)
                sw = self.ui.lut_signalwrapper[fs]
                if on_complete is not None:
                    on_complete(sw)

        if len(signals) > 1:
            if inverse:
                label = tr('Performing inverse FFT')
            else:
                label = tr('Performing FFT')
            t = ProgressThreaded(self.ui,
                                 do_ffts(),
                                 on_ffts_complete,
                                 label=label,)
                                 # This breaks the progress bar...
                                 # generator_N=len(signals))
            t.run()
        else:
            for i in do_ffts():
                pass
            on_ffts_complete()

    def live_fft(self, signals=None, shift=True, power_spectrum=True):
        """
        The live FFT dynamically calculates the FFT as the user navigates.
        """
        if signals is None:
            signals = self.ui.get_selected_signals()
            if signals is None:
                return
        # Make sure we can iterate
        if isinstance(signals, hs.signals.BaseSignal):
            signals = (signals,)

        if len(signals) < 1:
            return

        s = signals[0]

        if isinstance(s, hs.signals.Signal2D):
            extent = s.axes_manager.signal_extent
            left = (extent[1] - extent[0]) / 4 + extent[0]
            right = 3 * (extent[1] - extent[0]) / 4 + extent[0]
            top = (extent[3] - extent[2]) / 4 + extent[2]
            bottom = 3 * (extent[3] - extent[2]) / 4 + extent[2]
            roi = hs.roi.RectangularROI(left, top, right, bottom)
        elif isinstance(s, hs.signals.Signal1D):
            extent = s.axes_manager.signal_extent
            half_range = (extent[1] - extent[0]) / 4
            roi = hs.roi.SpanROI(half_range + extent[0],
                                 3 * half_range + extent[0])
        else:
            mb = QMessageBox(QMessageBox.Information,
                             tr("Live FFT"),
                             tr("Only Signal2D and Signal1D are supported."),
                             QMessageBox.Ok)
            mb.exec_()
            return

        roi.add_widget(s)
        roi_signal = roi.interactive(s, recompute_out_event=False)
        s_roi_fft = hs.interactive(roi_signal.fft,
                                   event=roi.events.changed,
                                   recompute_out_event=False,
                                   shift=shift)

        s_roi_fft.plot(power_spectrum=power_spectrum)

    def ifft(self, signals=None):
        return self.fft(signals, inverse=True)

    def get_real_image(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        if not isinstance(signal,
                          hs.signals.ComplexSignal):
            mb = QMessageBox(QMessageBox.Information,
                             tr("Real and imaginary"),
                             tr("A complex signal is required."),
                             QMessageBox.Ok)
            mb.exec_()
        signal.real.plot()
        signal.imag.plot()

    def get_amplitude_phase(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        if not isinstance(signal,
                          hs.signals.ComplexSignal):
            mb = QMessageBox(QMessageBox.Information,
                             tr("Amplitude and phase"),
                             tr("A complex signal is required."),
                             QMessageBox.Ok)
            mb.exec_()
        signal.amplitude.plot()
        signal.phase.plot()
