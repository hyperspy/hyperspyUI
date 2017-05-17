from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs


class MakeBivariateHistogram(Plugin):
    name = "Make bivariate histogram"

    def create_actions(self):
        self.add_action(
                self.name + '.make_bivariate_histogram',
                self.name,
                self.make_bivariate_histogram,
                tip="Make a bivariate histogram from x and y beam shift "
                    "signals.")

    def create_menu(self):
        self.add_menuitem(
                'DPC',
                self.ui.actions[self.name + '.make_bivariate_histogram'])

    def make_bivariate_histogram(self):
        ui = self.ui
        signal_wrapper_list = ui.select_x_signals(
            2, ["Deflection X", "Deflection Y"])
        signal0 = signal_wrapper_list[0].signal
        signal1 = signal_wrapper_list[1].signal
        s0_flat = signal0.data.flatten()
        s1_flat = signal1.data.flatten()
        spatial_std = 3
        bins = 200

        if (s0_flat.std() > s1_flat.std()):
            s0_range = (
                s0_flat.mean() - s0_flat.std() * spatial_std,
                s0_flat.mean() + s0_flat.std() * spatial_std)
            s1_range = (
                s1_flat.mean() - s0_flat.std() * spatial_std,
                s1_flat.mean() + s0_flat.std() * spatial_std)
        else:
            s0_range = (
                s0_flat.mean() - s1_flat.std() * spatial_std,
                s0_flat.mean() + s1_flat.std() * spatial_std)
            s1_range = (
                s1_flat.mean() - s1_flat.std() * spatial_std,
                s1_flat.mean() + s1_flat.std() * spatial_std)

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
