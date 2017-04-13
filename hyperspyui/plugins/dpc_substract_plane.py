from hyperspyui.plugins.plugin import Plugin
import numpy as np
from scipy.optimize import leastsq
from hyperspyui.widgets.stringinput import StringInputDialog


class SubtractPlane(Plugin):
    name = "Subtract plane from beamshifts"

    def create_actions(self):
        self.add_action(
                self.name + '.subtract_plane',
                self.name,
                self.subtract_plane,
                tip="Subtract a plane from a beam shift signal. "
                    "Useful for removing the effects of d-scan.")

    def create_menu(self):
        self.add_menuitem(
                'DPC', self.ui.actions[self.name + '.subtract_plane'])

    def _residuals(self, params, signal, X):
        return self._f_min(X, params)

    def _f_min(self, X, p):
        plane_xyz = p[0:3]
        distance = (plane_xyz * X.T).sum(axis=1) + p[3]
        return distance / np.linalg.norm(plane_xyz)

    def subtract_plane(self):
        ui = self.ui
        signal = ui.select_x_signals(1, ["signal"]).signal
        dialog = StringInputDialog("Percent of corner", "5")
        corner_percent = dialog.prompt_modal(rejection=5)
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
