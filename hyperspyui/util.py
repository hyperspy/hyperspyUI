# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 18:47:05 2014

@author: Vidar Tonaas Fauske
"""


import hyperspy.components
from functools import partial
from python_qt_binding import QtGui, QtCore, QtSvg


def tr(text):
    return QtCore.QCoreApplication.translate("MainWindow", text)


def lstrip(string, prefix):
    if string is not None:
        if string.startswith(prefix):
            return string[len(prefix):]


def fig2win(fig, windows):
    # Each figure has FigureCanvas as widget, canvas has figure property
    if fig is None:
        return None
    matches = [w for w in windows if w.widget().figure == fig]
    if len(matches) >= 1:
        return matches[0]
    else:
        return None


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


def dict_rlu(dictionary, value):
    """
    Reverse dictionary lookup.
    """
    for k, v in dictionary.iteritems():
        if v == value or v is value:
            return k
    raise KeyError()


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
                 'Erf', 'Exponential', 'Gaussian', 'Gaussian2', 'Logistic',
                 'Lorentzian', 'Offset', 'PowerLaw', 'SEE', 'RC', 'Vignetting',
                 'Voigt', 'Polynomial', 'PESCoreLineShape',
                 'VolumePlasmonDrude']
    for name in compnames:
        try:
            t = getattr(hyperspy.components, name)
        except AttributeError:
            continue
        ac_name = 'add_component_' + name
        f = partial(callback, t)
        ac = QtGui.QAction(prefix + name + postfix, parent)
        ac.setStatusTip(tr("Add a component of type ") + name)
        ac.connect(ac, QtCore.SIGNAL('triggered()'), f)
        actions[ac_name] = ac
    return actions


class Namespace(dict):

    """A dict subclass that exposes its items as attributes.

    Warning: Namespace instances do not have direct access to the
    dict methods.

    """

    def __init__(self, obj={}):
        super(Namespace, self).__init__(obj)

    def __dir__(self):
        return tuple(self)

    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__, super(Namespace, self).__repr__())

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            msg = tr("'%s' object has no attribute '%s'")
            raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    #------------------------
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

    #------------------------
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
