
import pytest


@pytest.mark.timeout(60)
def test_main_window(mainwindow):
    mainwindow.show()
    mainwindow.load_complete.emit()

    assert mainwindow.isVisible()
    assert mainwindow.windowTitle() == 'HyperSpy'
