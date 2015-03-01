# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:43:54 2014

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin
import scipy.fftpack
import numpy as np

from hyperspy.drawing.spectrum import SpectrumFigure
from hyperspy.drawing.image import ImagePlot
from hyperspy.axes import AxesManager
import hyperspy.signals

from threaded import ProgressThreaded
# TODO tr


class FFT_Plugin(Plugin):
    name = 'FFT'

    def create_actions(self):
        self.add_action('fft', "FFT", self.fft,
                        icon='fft.svg',
                        tip="Perform a fast fourier transform on the " +
                        "active part of the signal")

        self.add_action('live_fft', "Live FFT", self.live_fft,
                        icon='live_fft.svg',
                        tip="Perform a fast fourier transform on the " +
                        "active part of the signal, and link it to the " +
                        "navigator")

        self.add_action('nfft', "Signal FFT", self.nfft,
                        icon='nfft.svg',
                        tip="Perform a fast fourier transform on the " +
                            "entire signal")

        self.add_action('ifft', "Inverse FFT", self.ifft,
                        icon='ifft.svg',
                        tip="Perform an inverse fast fourier transform on " +
                            "the active part of the signal")

        self.add_action('infft', "Inverse Signal FFT", self.infft,
                        icon='infft.svg',
                        tip="Perform an inverse fast fourier transform on" +
                        " the entire signal")

    def create_toolbars(self):
        self.add_toolbar_button("Math", self.ui.actions['fft'])
        self.add_toolbar_button("Math", self.ui.actions['live_fft'])
        self.add_toolbar_button("Math", self.ui.actions['nfft'])
        self.add_toolbar_button("Math", self.ui.actions['ifft'])
        self.add_toolbar_button("Math", self.ui.actions['infft'])

    def fft(self, signals=None, inverse=False, on_complete=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        # Make sure we can iterate
        if isinstance(signals, hyperspy.signals.Signal):
            signals = (signals,)

        fftsignals = []

        def on_ffts_complete():
            for name, fs in fftsignals:
                if inverse:
                    sw = self.ui.add_signal_figure(fs, name + '[IFFT]')
                else:
                    sw = self.ui.add_signal_figure(fs, name + '[FFT]')
                if on_complete is not None:
                    on_complete(sw)

        def do_ffts():
            for i, sw in enumerate(signals):
                s = sw.signal
                if inverse:
                    fftdata = scipy.fftpack.ifftshift(s())
                    fftdata = scipy.fftpack.ifftn(fftdata)
                    fftdata = np.abs(fftdata)
                else:
                    fftdata = scipy.fftpack.fftn(s())
                    fftdata = scipy.fftpack.fftshift(fftdata)

                ffts = s.__class__(
                    fftdata,
                    axes=s.axes_manager._get_signal_axes_dicts(),
                    metadata=s.metadata.as_dictionary(),)
                ffts.axes_manager._set_axis_attribute_values("navigate", False)
                indstr = ' ' + str(s.axes_manager.indices) \
                    if len(s.axes_manager.indices) > 0 else ''
                ffts.metadata.General.title = 'FFT of ' + \
                    ffts.metadata.General.title + indstr

                for i in xrange(ffts.axes_manager.signal_dimension):
                    axis = ffts.axes_manager.signal_axes[i]
                    s_axis = s.axes_manager.signal_axes[i]
                    if not inverse:
                        axis.scale = 1 / (s_axis.size * s_axis.scale)
                    shift = (axis.high_value - axis.low_value) / 2
                    if inverse:
                        shift = -shift
                    axis.offset -= shift
                    if inverse:
                        axis.scale = 1 / (s_axis.size * s_axis.scale)
                    u = s_axis.units
                    if u.endswith('-1'):
                        u = u[:-2]
                    else:
                        u += '-1'
                    axis.units = u
                fftsignals.append((sw.name, ffts))
                yield i + 1

        if len(signals) > 1:
            if inverse:
                label = 'Performing inverse FFT'
            else:
                label = 'Performing FFT'
            t = ProgressThreaded(self.ui, do_ffts(), on_ffts_complete,
                                 label=label,
                                 generator_N=len(signals))
            t.run()
        else:
            for i in do_ffts():
                pass
            on_ffts_complete()

    def nfft(self, signals=None, inverse=False):
        if signals is None:
            signals = self.ui.get_selected_signals()
            if signals is None:
                return
        # Make sure we can iterate
        if isinstance(signals, hyperspy.signals.Signal):
            signals = (signals,)

        if len(signals) < 1:
            return

        fftsignals = []

        def on_ftts_complete():
            for name, fs in fftsignals:
                if inverse:
                    self.ui.add_signal_figure(fs, name + '[IFFT]')
                else:
                    self.ui.add_signal_figure(fs, name + '[FFT]')

        def do_ffts():
            j = 0
            for sw in signals:
                ffts = sw.signal.deepcopy()
                if ffts.data.itemsize <= 4:
                    ffts.change_dtype(np.complex64)
                else:
                    ffts.change_dtype(np.complex128)

                s = sw.signal
                am = AxesManager(s.axes_manager._get_axes_dicts())
                for idx in am:
                    fftdata = s.data[am._getitem_tuple]
                    fftdata = scipy.fftpack.fftn(fftdata)
                    fftdata = scipy.fftpack.fftshift(fftdata)
                    ffts.data[am._getitem_tuple] = fftdata
                    j += 1
                    yield j

                for i in xrange(ffts.axes_manager.signal_dimension):
                    axis = ffts.axes_manager.signal_axes[i]
                    s_axis = s.axes_manager.signal_axes[i]
                    axis.scale = 1 / (s_axis.size * s_axis.scale)
                    shift = (axis.high_value - axis.low_value) / 2
                    axis.offset -= shift
                    u = s_axis.units
                    if u.endswith('-1'):
                        u = u[:-2]
                    else:
                        u += '-1'
                    axis.units = u
                fftsignals.append((sw.name, ffts))

        def do_iffts():
            j = 0
            for sw in signals:
                ffts = sw.signal.deepcopy()
                if ffts.data.itemsize <= 4:
                    ffts.change_dtype(np.float32)
                else:
                    ffts.change_dtype(np.float64)

                s = sw.signal
                am = AxesManager(s.axes_manager._get_axes_dicts())

                for i in xrange(ffts.axes_manager.signal_dimension):
                    axis = ffts.axes_manager.signal_axes[i]
                    s_axis = s.axes_manager.signal_axes[i]
                    shift = (axis.high_value - axis.low_value) / 2
                    axis.offset += shift
                    axis.scale = 1 / (s_axis.size * s_axis.scale)
                    u = s_axis.units
                    if u.endswith('-1'):
                        u = u[:-2]
                    else:
                        u += '-1'
                    axis.units = u

                for idx in am:
                    fftdata = s.data[am._getitem_tuple]
                    fftdata = scipy.fftpack.ifftshift(fftdata)
                    fftdata = scipy.fftpack.ifftn(fftdata)
                    fftdata = np.abs(fftdata)
                    ffts.data[am._getitem_tuple] = fftdata
                    j += 1
                    yield j
                fftsignals.append((sw.name, ffts))

        n_ffts = np.product([d for s in signals
                             for d in s.signal.axes_manager.navigation_shape])
        if inverse:
            label = 'Performing inverse FFT'
            f = do_iffts()
        else:
            label = 'Performing FFT'
            f = do_ffts()
        t = ProgressThreaded(self.ui, f, on_ftts_complete,
                             label=label,
                             cancellable=True,
                             generator_N=n_ffts)
        t.run()

    def live_fft(self, signals=None):
        """
        The live FFT produces the exact same results as the nfft, except nfft
        calculates the FFTs over all signal dimensions and stores the result in
        a new signal. The live FFT dynamically calculates the FFT as the user
        navigates. In other words, nfft is memory intensive, live is cpu
        intensive.
        """
        if signals is None:
            signals = self.ui.get_selected_signals()
            if signals is None:
                return
        # Make sure we can iterate
        if isinstance(signals, hyperspy.signals.Signal):
            signals = (signals,)

        if len(signals) < 1:
            return

        def setup_live(fft_wrapper):
            s = signals[setup_live.i].signal
            setup_live.i += 1

            def data_function(axes_manager=None):
                fftdata = scipy.fftpack.fftn(s(axes_manager=axes_manager))
                fftdata = scipy.fftpack.fftshift(fftdata)
                return fftdata
            fs = fft_wrapper.signal
            sigp = fs._plot.signal_plot
            if isinstance(sigp, SpectrumFigure):
                sigp.ax_lines[0].axes_manager = s.axes_manager
                sigp.ax_lines[0].data_function = data_function
                sigp.ax_lines[1].axes_manager = s.axes_manager
                sigp.ax_lines[1].data_function = data_function
            elif isinstance(sigp, ImagePlot):
                sigp.axes_manager = s.axes_manager
                sigp.data_function = data_function

            def update():   # Wrapper as sigp.updatewould be passed values
                sigp.update()
            s.axes_manager.connect(update)

            def on_closing():
                s.axes_manager.disconnect(update)
            fft_wrapper.closing.connect(on_closing)

        setup_live.i = 0
        self.fft(signals, on_complete=setup_live)

    def ifft(self, signals=None):
        return self.fft(signals, inverse=True)

    def infft(self, signals=None):
        return self.nfft(signals, inverse=True)
