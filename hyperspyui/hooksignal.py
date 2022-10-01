# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Sat Feb 28 17:52:42 2015

@author: Vidar Tonaas Fauske
"""

import hyperspy.signal
import hyperspy.events
orig_signal = hyperspy.signal.BaseSignal


class HookedSignal(orig_signal):

    def plot(self, *args, **kwargs):
        _on_plotting(self)
        r = super().plot(*args, **kwargs)
        _on_plotted(self)
        return r


def hook_signal():
    """
    Call this function to enable hooks of Signal
    """
    hyperspy.signal.BaseSignal = HookedSignal


def dehook_signal():
    """
    Call this function to remove hooks from Signal
    """
    hyperspy.signal.BaseSignal = orig_signal

_plotting_cbs = hyperspy.events.Event(
    """Event that triggers right before BaseSignal.plot()
    """,
    ('signal',))
_plotted_cbs = hyperspy.events.Event(
    """Event that triggers right after BaseSignal.plot()
    """,
    ('signal',))


def _on_plotting(signal):
    _plotting_cbs.trigger(signal=signal)


def _on_plotted(signal):
    _plotted_cbs.trigger(signal=signal)


def connect_plotting(callback):
    """
    Call to subscribe to Signal plot events. 'callback' is called on the event.
    The Signal being plotted is passed as the first argument, then follows the
    arguments passed to plot(). Plotting event are called just before the plot
    call is executed.
    """
    _plotting_cbs.connect(callback)


def disconnect_plotting(callback):
    """
    Disconnect callback from subscription.
    """
    _plotting_cbs.disconnect(callback)


def connect_plotted(callback, userdata=None):
    """
    Call to subscribe to Signal plot events. 'callback' is called on the event.
    The Signal being plotted is passed as the first argument, then follows the
    arguments passed to plot(). If userdata is not None is is passed as a
    keyword argument, otherwise, it is left out. Plotted event are called just
    after the plot call is executed.
    """
    _plotted_cbs.connect(callback)


def disconnect_plotted(callback):
    """
    Disconnect callback from subscription.
    """
    _plotted_cbs.pop(callback)
