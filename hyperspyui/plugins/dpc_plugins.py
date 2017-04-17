from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs
from scipy.optimize import leastsq
from hyperspyui.widgets.stringinput import StringInputDialog
from scipy.ndimage.filters import gaussian_filter


class DpcPlugins(Plugin):
    name = 'Differential phase contrast plugins'

    def create_actions(self):
        self.add_action(
                'Beam shifts from segmented.get_beam_shifts',
                'Segmented detector to shifts',
                self.get_beam_shifts,
                tip="Calculate the beam shifts from a segmented STEM DPC "
                    "dataset, requires the four outer segments.")
        self.add_action(
                'FFT filter beam shifts.fft_filter_shifts',
                "FFT filter beam shift signal",
                self.fft_filter_shifts,
                tip="Do FFT filtering on a beam shift signal, to suppress "
                    " high frequencies ")
        self.add_action(
                'Subtract plane from beamshifts.subtract_plane',
                'Subtract plane from beamshifts',
                self.subtract_plane,
                tip="Subtract a plane from a beam shift signal. "
                    "Useful for removing the effects of d-scan.")
        self.add_action(
                'Make color image from beam shifts.make_color_image',
                'Make color image from beam shifts',
                self.make_color_image,
                tip="Make a color RGB signal from beam shift x and y signals")
        self.add_action(
                'Make bivariate histogram.make_bivariate_histogram',
                'Make bivariate histogram',
                self.make_bivariate_histogram,
                tip="Make a bivariate histogram from x and y beam shift "
                    "signals.")

    def create_menu(self):
        self.add_menuitem(
                'DPC',
                self.ui.actions[
                    'Beam shifts from segmented.get_beam_shifts'])
        self.add_menuitem(
                'DPC',
                self.ui.actions[
                    'FFT filter beam shifts.fft_filter_shifts'])
        self.add_menuitem(
                'DPC',
                self.ui.actions[
                    'Subtract plane from beamshifts.subtract_plane'])
        self.add_menuitem(
                'DPC',
                self.ui.actions[
                    'Make color image from beam shifts.make_color_image'])
        self.add_menuitem(
                'DPC',
                self.ui.actions[
                    'Make bivariate histogram.make_bivariate_histogram'])

    def get_beam_shifts(self):
        ui = self.ui
        signal_wrapper_list = ui.select_x_signals(
            4, ["ext 0", "ext 1", "ext 2", "ext 3"])
        if signal_wrapper_list is None:
            return
        s_ext0 = signal_wrapper_list[0].signal
        s_ext1 = signal_wrapper_list[1].signal
        s_ext2 = signal_wrapper_list[2].signal
        s_ext3 = signal_wrapper_list[3].signal
        s_ext0.change_dtype('float64')
        s_ext1.change_dtype('float64')
        s_ext2.change_dtype('float64')
        s_ext3.change_dtype('float64')
        s_ext02 = s_ext0 - s_ext2
        s_ext13 = s_ext1 - s_ext3
        s_ext02.metadata.General.title = 'dif02'
        s_ext13.metadata.General.title = 'dif13'
        s_ext02.plot()
        s_ext13.plot()

    def subtract_plane(self):
        ui = self.ui
        signal = ui.select_x_signals(1, ["signal"]).signal
        dialog = StringInputDialog("Percent of corner", "5")
        corner_percent = dialog.prompt_modal(rejection=None)
        if corner_percent is None:
            return
        corner_size = float(corner_percent) * 0.01
        d_axis0_range = (
            signal.axes_manager[0].high_value -
            signal.axes_manager[0].low_value) * corner_size
        d_axis1_range = (
            signal.axes_manager[1].high_value -
            signal.axes_manager[1].low_value) * corner_size
        s_corner00 = signal.isig[0:d_axis0_range, 0:d_axis1_range]
        s_corner01 = signal.isig[0:d_axis0_range, -d_axis1_range:-1]
        s_corner10 = signal.isig[-d_axis0_range:-1, 0:d_axis1_range]
        s_corner11 = signal.isig[-d_axis0_range:-1, -d_axis1_range:-1]

        corner00 = (
            s_corner00.axes_manager[0].axis.mean(),
            s_corner00.axes_manager[1].axis.mean(),
            s_corner00.data.mean())
        corner01 = (
            s_corner01.axes_manager[0].axis.mean(),
            s_corner01.axes_manager[1].axis.mean(),
            s_corner01.data.mean())
        corner10 = (
            s_corner10.axes_manager[0].axis.mean(),
            s_corner10.axes_manager[1].axis.mean(),
            s_corner10.data.mean())
        corner11 = (
            s_corner11.axes_manager[0].axis.mean(),
            s_corner11.axes_manager[1].axis.mean(),
            s_corner11.data.mean())
        corner_values = np.array((corner00, corner01, corner10, corner11)).T
        p0 = [0.1, 0.1, 0.1, 0.1]

        p = leastsq(self._residuals, p0, args=(None, corner_values))[0]

        xx, yy = np.meshgrid(
            signal.axes_manager[0].axis, signal.axes_manager[1].axis)
        zz = (-p[0] * xx - p[1] * yy - p[3]) / p[2]

        new_signal = signal.deepcopy()
        new_signal.data -= zz
        new_signal.metadata = signal.metadata.deepcopy()
        new_name = new_signal.metadata.General.title + " plane subtracted"
        new_signal.metadata.General.title = new_name
        new_signal.plot()

    def _residuals(self, params, signal, X):
        return self._f_min(X, params)

    def _f_min(self, X, p):
        plane_xyz = p[0:3]
        distance = (plane_xyz * X.T).sum(axis=1) + p[3]
        return distance / np.linalg.norm(plane_xyz)

    def make_color_image(self):
        ui = self.ui

        signal_wrapper_list = ui.select_x_signals(
            2, ["Deflection X", "Deflection Y"])
        if signal_wrapper_list is None:
            return
        signal0 = signal_wrapper_list[0].signal
        signal1 = signal_wrapper_list[1].signal

        signal_rgb = hs.signals.Signal1D(
            self._get_rgb_array(signal0, signal1) * 255)
        signal_rgb.change_dtype("uint8")
        signal_rgb.change_dtype("rgb8")
        signal_rgb.axes_manager = signal0.axes_manager.deepcopy()
        signal_rgb.metadata = signal0.metadata.deepcopy()
        signal_rgb.metadata.General.title = "Deflection color image"
        signal_rgb.plot()

    def _get_color_channel(self, a_array, mu0, si0, mu1, si1, mu2, si2):
        color_array = np.zeros((a_array.shape[0], a_array.shape[1]))
        color_array[:] = 1. - (
            np.exp(-1 * ((a_array - mu0)**2) / si0) +
            np.exp(-1 * ((a_array - mu1)**2) / si1) +
            np.exp(-1 * ((a_array - mu2)**2) / si2))
        return(color_array)

    def _get_rgb_array(self, signal0, signal1):
        arctan_array = np.arctan2(signal0.data, signal1.data) + np.pi

        color0 = self._get_color_channel(
            arctan_array, 3.7, 0.8, 5.8, 5.0, 0.0, 0.3)
        color1 = self._get_color_channel(
            arctan_array, 2.9, 0.6, 1.7, 0.3, 2.4, 0.5)
        color2 = self._get_color_channel(
            arctan_array, 0.0, 1.3, 6.4, 1.0, 1.0, 0.75)

        rgb_array = np.zeros(
            (signal0.data.shape[0], signal0.data.shape[1], 3))
        rgb_array[:, :, 2] = color0
        rgb_array[:, :, 1] = color1
        rgb_array[:, :, 0] = color2
        return(rgb_array)

    def make_bivariate_histogram(self):
        ui = self.ui
        signal_wrapper_list = ui.select_x_signals(
            2, ["Deflection X", "Deflection Y"])
        if signal_wrapper_list is None:
            return
        signal0 = signal_wrapper_list[0].signal
        signal1 = signal_wrapper_list[1].signal
        s0_flat = signal0.data.flatten()
        s1_flat = signal1.data.flatten()
        spatial_std = 3
        bins = 200

        s0_flat_std = s0_flat.std()
        s0_flat_mean = s0_flat.mean()
        s1_flat_std = s1_flat.std()
        s1_flat_mean = s1_flat.mean()
        if (s0_flat_std > s1_flat_std):
            s0_range = (
                s0_flat_mean - s0_flat_std * spatial_std,
                s0_flat_mean + s0_flat_std * spatial_std)
            s1_range = (
                s1_flat_mean - s0_flat_std * spatial_std,
                s1_flat_mean + s0_flat_std * spatial_std)
        else:
            s0_range = (
                s0_flat_mean - s1_flat_std * spatial_std,
                s0_flat_mean + s1_flat_std * spatial_std)
            s1_range = (
                s1_flat_mean - s1_flat_std * spatial_std,
                s1_flat_mean + s1_flat_std * spatial_std)

        hist2d, xedges, yedges = np.histogram2d(
            s0_flat,
            s1_flat,
            bins=bins,
            range=[
                [s0_range[0], s0_range[1]],
                [s1_range[0], s1_range[1]]])

        s = hs.signals.Signal2D(hist2d)
        s.metadata.General.title = "Bivariate histogram"
        s.axes_manager[0].offset = xedges[0]
        s.axes_manager[0].scale = xedges[1] - xedges[0]
        s.axes_manager[1].offset = yedges[0]
        s.axes_manager[1].scale = yedges[1] - yedges[0]

        s.plot()

    def fft_filter_shifts(self):
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
