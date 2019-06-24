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
import scipy.fftpack

from qtpy import QtCore
from qtpy.QtWidgets import QMessageBox

from hyperspy.drawing.signal1d import Signal1DFigure
from hyperspy.drawing.image import ImagePlot
import hyperspy.signals

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

        self.add_action('decompose', "FFT Magnitude/Phase", self.decompose,
                        icon=None,
                        tip="Decompose a fast fourier transformation result " +
                        "into its magnitude and phase.",
                        selection_callback=self.ui.select_signal)

    def create_menu(self):
        self.add_menuitem("Math", self.ui.actions['fft'])
        self.add_menuitem("Math", self.ui.actions['live_fft'])
        self.add_menuitem("Math", self.ui.actions['ifft'])
        self.add_menuitem("Math", self.ui.actions['decompose'])

    def create_toolbars(self):
        self.add_toolbar_button("Math", self.ui.actions['fft'])
        self.add_toolbar_button("Math", self.ui.actions['live_fft'])
        self.add_toolbar_button("Math", self.ui.actions['ifft'])

    def fft(self, signals=None, shift=True, power_spectrum=True, inverse=False,
            on_complete=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        if isinstance(signals, hyperspy.signal.BaseSignal):
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
                                 label=label,
                                 generator_N=len(signals))
            t.run()
        else:
            for i in do_ffts():
                pass
            on_ffts_complete()

    def live_fft(self, signals=None):
        """
        The live FFT dynamically calculates the FFT as the user navigates.
        """
        if signals is None:
            signals = self.ui.get_selected_signals()
            if signals is None:
                return
        # Make sure we can iterate
        if isinstance(signals, hyperspy.signal.BaseSignal):
            signals = (signals,)

        if len(signals) < 1:
            return

        def setup_live(fft_wrapper):
            s = signals[setup_live.i]
            setup_live.i += 1

            def data_function(axes_manager=None):
                fftdata = scipy.fftpack.fftn(s(axes_manager=axes_manager))
                fftdata = scipy.fftpack.fftshift(fftdata)
                return fftdata
            fs = fft_wrapper.signal
            sigp = fs._plot.signal_plot
            if isinstance(sigp, Signal1DFigure):
                sigp.ax_lines[0].axes_manager = s.axes_manager
                sigp.ax_lines[0].data_function = data_function
                sigp.ax_lines[1].axes_manager = s.axes_manager
                sigp.ax_lines[1].data_function = data_function
            elif isinstance(sigp, ImagePlot):
                sigp.axes_manager = s.axes_manager
                sigp.data_function = data_function

            s.axes_manager.events.indices_changed.connect(sigp.update, [])

            def on_closing():
                s.axes_manager.events.indices_changed.disconnect(sigp.update)
            fft_wrapper.closing.connect(on_closing)

        setup_live.i = 0
        self.fft(signals, on_complete=setup_live)

    def ifft(self, signals=None):
        return self.fft(signals, inverse=True)

    def decompose(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        if not isinstance(signal,
                          hyperspy._signals.complex_signal.ComplexSignal):
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Information)
            mb.setText("A complex signal is required")
            mb.setStandardButtons(QMessageBox.Ok)
            mb.exec_()
        signal.real.plot()
        signal.phase.plot()
