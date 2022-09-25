import hyperspy.api as hs
import pytest
import numpy as np


@pytest.mark.timeout(30)
def test_plotting_signal1D(mainwindow):
    s = hs.datasets.artificial_data.get_core_loss_eels_line_scan_signal()

    s.plot()

    s.axes_manager.indices = (2, )
    assert s.axes_manager.indices == (2, )


@pytest.mark.timeout(30)
def test_plotting_signal2D(mainwindow):
    s = hs.signals.Signal2D(np.arange(400).reshape(4, 10, 10))
    s.plot()

    s.axes_manager.indices = (2, )
    assert s.axes_manager.indices == (2, )
