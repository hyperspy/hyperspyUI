# -*- coding: utf-8 -*-
# Copyright 2007-2016 The HyperSpyUI developers
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
orig_signal = hyperspy.signal.Signal


class HookedSignal(orig_signal):

    def plot(self, *args, **kwargs):
        _on_plotting(self, navigator="auto", axes_manager=None)
        r = super(HookedSignal, self).plot(*args, **kwargs)
        _on_plotted(self, navigator="auto", axes_manager=None)
        return r


def hook_signal():
    """
    Call this function to enable hooks of Signal
    """
    hyperspy.signal.Signal = HookedSignal


def dehook_signal():
    """
    Call this function to remove hooks from Signal
    """
    hyperspy.signal.Signal = orig_signal

_plotting_cbs = {}
_plotted_cbs = {}


def _cb(cbs, *args, **kwargs):
    for cb, userdata in cbs.iteritems():
        if userdata is None:
            cb(*args, **kwargs)
        else:
            cb(*args, userdata=userdata, **kwargs)


def _on_plotting(*args, **kwargs):
    _cb(_plotting_cbs, *args, **kwargs)


def _on_plotted(*args, **kwargs):
    _cb(_plotted_cbs, *args, **kwargs)


def connect_plotting(callback, userdata=None):
    """
    Call to subscribe to Signal plot events. 'callback' is called on the event.
    The Signal being plotted is passed as the first argument, then follows the
    arguments passed to plot(). If userdata is not None is is passed as a
    keyword argument, otherwise, it is left out. Plotting event are called just
    before the plot call is executed.
    """
    global _plotting_cbs
    _plotting_cbs[callback] = userdata


def disconnect_plotting(callback):
    """
    Disconnect callback from subscription.
    """
    global _plotting_cbs
    if callback in _plotting_cbs:
        _plotting_cbs.pop(callback)


def connect_plotted(callback, userdata=None):
    """
    Call to subscribe to Signal plot events. 'callback' is called on the event.
    The Signal being plotted is passed as the first argument, then follows the
    arguments passed to plot(). If userdata is not None is is passed as a
    keyword argument, otherwise, it is left out. Plotted event are called just
    after the plot call is executed.
    """
    global _plotted_cbs
    _plotted_cbs[callback] = userdata


def disconnect_plotted(callback):
    """
    Disconnect callback from subscription.
    """
    global _plotted_cbs
    if callback in _plotted_cbs:
        _plotted_cbs.pop(callback)
