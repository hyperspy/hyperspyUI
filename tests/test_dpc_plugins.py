from hyperspyui.plugins import dpc_plugins
import hyperspy.api as hs
import numpy as np


class TestDpcPlugins:

    def test_get_beam_shift(self):
        dpcplugin = dpc_plugins.DpcPlugins("")
        s0 = hs.signals.Signal2D(np.ones((10, 10)))
        s1 = hs.signals.Signal2D(np.zeros((10, 10)))
        s2 = hs.signals.Signal2D(np.zeros((10, 10)))
        s3 = hs.signals.Signal2D(np.ones((10, 10)))
        s02, s13 = dpcplugin.get_beam_shifts(
                [s0, s1, s2, s3], plot_output=False)
        assert (s02.data == 1).all()
        assert (s13.data == -1).all()

    def test_subtract_plane(self):
        dpcplugin = dpc_plugins.DpcPlugins("")
        s = hs.signals.Signal2D(np.arange(400).reshape((20, 20)))
        s_subtract = dpcplugin.subtract_plane(
                s, corner_percent=5, plot_output=False)
        assert (np.abs(s_subtract.data) < 1e-11).all()

    def test_make_bivariate_histogram(self):
        dpcplugin = dpc_plugins.DpcPlugins("")
        s0 = hs.signals.Signal2D(np.zeros((10, 10)))
        s1 = hs.signals.Signal2D(np.zeros((10, 10)))
        s_bivariate = dpcplugin.make_bivariate_histogram(
                [s0, s1], plot_output=False)
        assert s_bivariate.isig[0., 0.].data == 100.
        s_bivariate.data[
                s_bivariate.axes_manager[0].value2index(0.),
                s_bivariate.axes_manager[1].value2index(0.)] = 0.
        assert (s_bivariate.data == 0.).all()

        s2 = hs.signals.Signal2D(np.ones((10, 10)))
        s3 = hs.signals.Signal2D(np.ones((10, 10)))
        s_bivariate1 = dpcplugin.make_bivariate_histogram(
                [s2, s3], plot_output=False)
        assert s_bivariate1.isig[1., 1.].data == 100.
        s_bivariate1.data[
                s_bivariate1.axes_manager[0].value2index(1.),
                s_bivariate1.axes_manager[1].value2index(1.)] = 0.
        assert (s_bivariate.data == 0.).all()

    def test_fft_filter_shifts(self):
        dpcplugin = dpc_plugins.DpcPlugins("")
        s0 = hs.signals.Signal2D(np.zeros((100, 100)))
        s1 = hs.signals.Signal2D(np.zeros((100, 100)))
        s0_fft, s1_fft = dpcplugin.fft_filter_shifts(
                [s0, s1],
                mask_radius=20,
                smoothing_factor=0.7,
                plot_output=False)
        assert (s0_fft.data == 0.).all()
        assert (s1_fft.data == 0.).all()
