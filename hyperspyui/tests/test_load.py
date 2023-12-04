
import numpy as np
import pytest

import hyperspy.api as hs


@pytest.mark.timeout(30)
def test_load(mainwindow, tmp_path):
    s = hs.signals.Signal2D(np.arange(25*25).reshape(25, 25))
    filename = tmp_path / 'test_file.hspy'
    s.save(filename)

    assert mainwindow.get_selected_signal() is None
    mainwindow.load([str(filename)])
    assert mainwindow.get_selected_signal() is not None


def test_get_accepted_extensions(mainwindow):
    extensions = mainwindow.get_accepted_extensions()
    assert 'dm3' in extensions
