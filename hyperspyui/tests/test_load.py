
import pytest

import hyperspy.api as hs


@pytest.mark.timeout(30)
def test_load(mainwindow, tmp_path):
    s = hs.datasets.artificial_data.get_core_loss_eels_line_scan_signal()
    filename = tmp_path / 'test_file.hspy'
    s.save(filename)

    assert mainwindow.get_selected_signal() is None
    mainwindow.load([str(filename)])
    assert mainwindow.get_selected_signal() is not None
