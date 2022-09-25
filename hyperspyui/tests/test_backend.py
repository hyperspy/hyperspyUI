
import matplotlib
matplotlib.use('module://hyperspyui.mdi_mpl_backend')
matplotlib.interactive(True)

from hyperspyui.mdi_mpl_backend import (
    connect_on_new_figure, disconnect_on_new_figure,
    connect_on_destroy, disconnect_on_destroy)

import matplotlib.pyplot as plt


def test_new_figure(qapp):
    fig = plt.figure()
    plt.plot(range(10))
    plt.close(fig)


def test_new_figure_callback(qapp):
    call_count = 0

    def trigger(figure):
        nonlocal call_count
        assert figure
        call_count += 1

    connect_on_new_figure(trigger)
    plt.figure()
    plt.plot(range(10))
    plt.close()

    disconnect_on_new_figure(trigger)
    plt.figure()
    plt.plot(range(10))
    plt.close()

    assert call_count == 1


def test_destroyed_figure_callback(qapp):
    call_count = 0

    def trigger(figure):
        nonlocal call_count
        assert figure
        call_count += 1

    connect_on_destroy(trigger)
    plt.figure()
    plt.plot(range(10))
    plt.close()

    disconnect_on_destroy(trigger)
    plt.figure()
    plt.plot(range(10))
    plt.close()

    assert call_count == 1
