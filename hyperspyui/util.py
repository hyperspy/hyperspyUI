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
Created on Mon Oct 27 18:47:05 2014

@author: Vidar Tonaas Fauske
"""


import hyperspy.components1d
from hyperspy.misc.utils import slugify
from functools import partial
from qtpy import QtGui, QtCore, QtSvg, QtWidgets
import os
from contextlib import contextmanager


def tr(text):
    return QtCore.QCoreApplication.translate("MainWindow", text)


@contextmanager
def dummy_context_manager(*args, **kwargs):
    yield


@contextmanager
def block_signals(target):
    old = target.blockSignals(True)
    try:
        yield
    finally:
        target.blockSignals(old)


def lstrip(string, prefix):
    if string is not None:
        if string.startswith(prefix):
            return string[len(prefix):]
    return None


def debug_trace():
    '''Set a tracepoint in the Python debugger that works with Qt'''
    from qtpy.QtCore import pyqtRemoveInputHook
    from pdb import set_trace
    pyqtRemoveInputHook()
    set_trace()


def fig2win(fig, windows):
    # Each figure has FigureCanvas as widget, canvas has figure property
    if fig is None:
        return None
    matches = [w for w in windows if w.widget().figure == fig]
    if len(matches) >= 1:
        return matches[0]
    else:
        return None


def fig2image_plot(fig, signals):
    from hyperspy.drawing.mpl_he import MPL_HyperExplorer
    from hyperspy.drawing.image import ImagePlot
    for s in signals:
        p = s.signal._plot
        if isinstance(p, MPL_HyperExplorer):
            if isinstance(p.signal_plot, ImagePlot):
                if p.signal_plot.figure is fig:
                    return p.signal_plot
            if isinstance(p.navigator_plot, ImagePlot):
                if p.navigator_plot.figure is fig:
                    return p.navigator_plot
    return None


def fig2sig(fig, signals):
    from hyperspy.drawing.mpl_he import MPL_HyperExplorer
    for s in signals:
        p = s.signal._plot
        if isinstance(p, MPL_HyperExplorer):
            if p.signal_plot and p.signal_plot.figure is fig:
                return s, p.signal_plot
            elif p.navigator_plot and p.navigator_plot.figure is fig:
                return s, p.navigator_plot
    return None, None


def win2fig(window):
    # Each figure has FigureCanvas as widget, canvas has figure property
    return window.widget().figure


def win2sig(window, signals=None, plotting_signal=None):
    r = None
    if window is not None:
        if signals is None:
            # Returns None if no such property
            r = window.property('hyperspyUI.SignalWrapper')
        else:
            for s in signals:
                if window in (s.navigator_plot, s.signal_plot):
                    return s
    if r is None and plotting_signal is not None:
        return plotting_signal
    return r


class SignalTypeFilter:

    def __init__(self, signal_type, ui, space=None):
        self.signal_type = signal_type
        self.ui = ui
        self.space = space

    def __call__(self, win, action):
        sig = win2sig(win, self.ui.signals, self.ui._plotting_signal)
        valid = sig is not None and isinstance(sig.signal, self.signal_type)
        if valid and self.space:
            # Check that we have right figure
            if not ((self.space == "navigation" and win is sig.navigator_plot)
                    or
                    (self.space == "signal" and win is sig.signal_plot)):
                valid = False
        action.setEnabled(valid)


def dict_rlu(dictionary, value):
    """
    Reverse dictionary lookup.
    """
    for k, v in dictionary.items():
        if v == value or v is value:
            return k
    raise KeyError()


def crosshair_cursor():
    if os.name == 'nt':
        # On windows, cursors support "inversion" mode, where they invert the
        # underlying color. This is achived with two bitmap.
        # Final cursor has mask all 0
        # When main bitmap is 0, this means transparent, when 1, inversion.
        bm = QtGui.QBitmap(16, 16)
        ma = QtGui.QBitmap(16, 16)
        bm.clear()
        ma.clear()
        # Paint a crosshair on the main bitmap with color1.
        pbm = QtGui.QPainter(bm)
        pbm.setPen(QtCore.Qt.color1)
        pbm.drawLine(8, 0, 8, 15)
        pbm.drawLine(0, 8, 15, 8)
        pbm.setPen(QtCore.Qt.color0)
        pbm.drawPoint(8, 8)
        pbm.end()
        return QtGui.QCursor(bm, ma, 8, 8)
    else:
        fn = os.path.dirname(__file__) + '/images/picker.svg'
        return load_cursor(fn, 8, 8)


def load_cursor(filename, hotX=-1, hotY=-1):
    renderer = QtSvg.QSvgRenderer(filename)
    pm = QtGui.QPixmap(16, 16)
    pm.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pm)
    renderer.render(painter)
    del painter, renderer
    return QtGui.QCursor(pm, hotX, hotY)


def create_add_component_actions(parent, callback, prefix="", postfix=""):
    actions = {}
    compnames = ['Arctan', 'Bleasdale', 'DoubleOffset', 'DoublePowerLaw',
                 'Erf', 'Exponential', 'Gaussian', 'GaussianHF', 'Logistic',
                 'Lorentzian', 'Offset', 'PowerLaw', 'SEE', 'RC', 'Vignetting',
                 'Voigt', 'Polynomial', 'PESCoreLineShape', 'Expression',
                 'VolumePlasmonDrude']
    for name in compnames:
        try:
            t = getattr(hyperspy.components1d, name)
        except AttributeError:
            continue
        ac_name = 'add_component_' + name
        f = partial(callback, t)
        ac = QtWidgets.QAction(prefix + name + postfix, parent)
        ac.setStatusTip(tr("Add a component of type ") + name)
        ac.triggered.connect(f)
        actions[ac_name] = ac
    return actions


class AttributeDict(dict):

    """A dict subclass that exposes its items as attributes.
    """

    def __init__(self, obj=None):
        if obj is None:
            obj = {}
        super().__init__(obj)

    def __dir__(self):
        return [slugify(k, True) for k in self]

    def __repr__(self):
        return f"{type(self).__name__}({dict.__repr__(self)})"

    def __getattr__(self, key):
        value = None
        if key in self:
            value = self[key]
        else:
            for k in self:
                if key == slugify(k, True):
                    value = self[k]
                    break
        return value

    def __setattr__(self, name, value):
        if name in self:
            self[name] = value
        else:
            for k in self:
                if name == slugify(k, True):
                    self[k] = value
                    break
            else:
                self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            for k in self:
                if name == slugify(k, True):
                    del self[k]

    # ------------------------
    # "copy constructors"

    @classmethod
    def from_object(cls, obj, names=None):
        if names is None:
            names = dir(obj)
        ns = {name: getattr(obj, name) for name in names}
        return cls(ns)

    @classmethod
    def from_mapping(cls, ns, names=None):
        if names:
            ns = {name: ns[name] for name in names}
        return cls(ns)

    @classmethod
    def from_sequence(cls, seq, names=None):
        if names:
            seq = {name: val for name, val in seq if name in names}
        return cls(seq)

    # ------------------------
    # static methods

    @staticmethod
    def hasattr(ns, name):
        try:
            object.__getattribute__(ns, name)
        except AttributeError:
            return False
        return True

    @staticmethod
    def getattr(ns, name):
        return object.__getattribute__(ns, name)

    @staticmethod
    def setattr(ns, name, value):
        return object.__setattr__(ns, name, value)

    @staticmethod
    def delattr(ns, name):
        return object.__delattr__(ns, name)


class Namespace(AttributeDict):

    """
    A dict subclass that exposes its items as attributes.

    Warning: Namespace instances do not have direct access to the
    dict methods.
    """

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            msg = tr("'%s' object has no attribute '%s'")
            raise AttributeError(msg % (type(self).__name__, name))
