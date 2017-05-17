from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs
from hyperspyui.widgets.stringinput import StringInputDialog
from scipy.ndimage.filters import gaussian_filter


class DpcFFTFilterShifts(Plugin):
    """
    Do FFT filtering of x and y beam shift signals by removing the high
    frequency contributions. This is useful for reducing the effects
    from diffraction contrast, since these normally vary at a higher
    frequency compared to the DPC contrast.

    This is done by:
    - Fourier transforming the signal
    - Masking the low frequencies in the Fourier transformed signal
    - Inverse Fourier transforming this masked signal
    - Subtracting a factor of this masked and inverted signal from the
        original signal
    This process is done separately for each signal.

    Input parameters:
    Mask radius : number
        The size of the mask used on the Fourier transformed signal.
        A smaller number will subtract more of the signal.
    Smoothing factor : number
        The amount of intensity from the masked and inverted signal
        which is subtracted from the original signal.
    """
    name = "DPC FFT filter beam shifts"

    def create_actions(self):
        self.add_action(
                self.name + '.fft_filter_shifts',
                "FFT filter beam shift signal",
                self.fft_filter_shifts,
                tip="Do FFT filtering on a beam shift signal, to suppress "
                    " high frequencies ")

    def create_menu(self):
        self.add_menuitem(
                'DPC', self.ui.actions[self.name + '.fft_filter_shifts'])

    def fft_filter_shifts(self):
        ui = self.ui
        signals = [s.signal for s in ui.select_x_signals(
            2, ["dif02", "dif13"])]
        dialog = StringInputDialog("Mask radius:", "20")
        mask_radius = dialog.prompt_modal(rejection=None)
        if mask_radius is None:
            return
        s_dif02 = signals[0]
        s_dif13 = signals[1]
        fft02 = np.fft.fftshift(np.fft.fft2(s_dif02.data))
        fft13 = np.fft.fftshift(np.fft.fft2(s_dif13.data))
        a, b = s_dif02.axes_manager[0].size / \
            2, s_dif02.axes_manager[0].size / 2
        n = s_dif02.axes_manager[0].size
        r = float(mask_radius)
        y, x = np.ogrid[-a:n - a, -b:n - b]
        mask = x * x + y * y <= r * r
        mask = np.zeros_like(mask, dtype="float64") + 1 - mask
        mask_blurred = gaussian_filter(mask, sigma=7)
        fft02 *= mask_blurred
        fft02 = np.fft.fftshift(fft02)
        fft13 *= mask_blurred
        fft13 = np.fft.fftshift(fft13)
        ifft02 = np.fft.ifft2(fft02)
        ifft13 = np.fft.ifft2(fft13)
        s_ifft02 = hs.signals.Signal2D(np.real(ifft02))
        s_ifft13 = hs.signals.Signal2D(np.real(ifft13))
        dialog = StringInputDialog("Smoothing factor:", "0.7")
        smoothing_factor = dialog.prompt_modal(rejection=None)
        if smoothing_factor is None:
            return
        s_ifft02.data *= float(smoothing_factor)
        s_ifft13.data *= float(smoothing_factor)
        s_dif02_filtered = s_dif02 - s_ifft02
        s_dif13_filtered = s_dif13 - s_ifft13
        s_dif02_filtered.change_dtype('float32')
        s_dif13_filtered.change_dtype('float32')
        name_02 = s_dif02_filtered.metadata.General.title + ' filtered'
        name_13 = s_dif13_filtered.metadata.General.title + ' filtered'
        s_dif02_filtered.metadata.General.title = name_02
        s_dif13_filtered.metadata.General.title = name_13
        s_dif02_filtered.plot()
        s_dif13_filtered.plot()
