from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs


class MakeColorImage(Plugin):
    name = "Make color image from beam shifts"

    def create_actions(self):
        self.add_action(
                self.name + '.make_color_image',
                self.name,
                self.make_color_image,
                tip="Make a color RGB signal from beam shift x and y signals")

    def create_menu(self):
        self.add_menuitem(
                'DPC', self.ui.actions[self.name + '.make_color_image'])

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

    def make_color_image(self):
        ui = self.ui

        signal_wrapper_list = ui.select_x_signals(
            2, ["Deflection X", "Deflection Y"])
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
