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
Created on Fri Oct 31 14:22:53 2014

@author: Vidar Tonaas Fauske
"""

import os

import matplotlib.backends.backend_qt4agg
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import FigureManagerBase
from matplotlib import __version__ as mplversionstring

mpl13 = mplversionstring.startswith('1.3')
mpl14 = mplversionstring.startswith('1.4')
mpl15 = mplversionstring.startswith('1.5')

if mpl13:
    from matplotlib.backends.qt4_compat import QtCore, QtGui, _getSaveFileName, __version__
else: # mpl14 or mpl15, or higher
    from matplotlib.backends.qt_compat import QtCore, QtGui, _getSaveFileName, __version__

if mpl13:
    from matplotlib.backends.backend_qt4 import (QtCore, QtGui, FigureManagerQT, FigureCanvasQT,
                                                 show, draw_if_interactive, backend_version,
                                                 NavigationToolbar2QT)
else: # mpl14 or mpl15, or higher
    from matplotlib.backends.backend_qt5 import (SPECIAL_KEYS, SUPER, ALT, CTRL,
                                                 SHIFT, MODIFIER_KEYS, fn_name, cursord,
                                                 draw_if_interactive, _create_qApp, show, TimerQT,
                                                 FigureManagerQT,
                                                 SubplotToolQt, error_msg_qt, exception_handler)

# FigureCanvas definition
if mpl13:
    FigureCanvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg
else:  # mpl14 or mpl15, or higher
    FigureCanvas = matplotlib.backends.backend_qt4agg.FigureCanvas

# =================
# Event managers
# =================

_new_fig_cbs = {}
_destroy_cbs = {}


def connect_on_new_figure(callback, userdata=None):
    """
    Call to subscribe to new MPL figure events. 'callback' is called on the
    event, with the figure as it's first parameter, and 'userdata' as it's
    second parameter if it is not None. If it's None, only one parameter is
    passed.
    """
    global _new_fig_cbs
    _new_fig_cbs[callback] = userdata


def disconnect_on_new_figure(callback):
    """
    Disconnect callback from subscription.
    """
    global _new_fig_cbs
    if callback in _new_fig_cbs:
        _new_fig_cbs.pop(callback)


def _on_new_figure(figure):
    """
    New MPL figure event, calls subscribers.
    'figure' parameter is of the type FigureWindow defined below
    """
    global _new_fig_cbs
    for callback, userdata in _new_fig_cbs.iteritems():
        try:
            callback(figure, userdata)
        except TypeError:
            callback(figure)


def connect_on_destroy(callback, userdata=None):
    """
    Call to subscribe to destroying MPL figure events. 'callback' is called on
    the event, with the figure as it's first parameter, and 'userdata' as it's
    second parameter if it is not None. If it's None, only one parameter is
    passed.
    """
    global _destroy_cbs
    _destroy_cbs[callback] = userdata


def disconnect_on_destroy(callback):
    """
    Disconnect callback from subscription.
    """
    global _destroy_cbs
    if callback in _destroy_cbs:
        _destroy_cbs.pop(callback)


def _on_destroy(figure):
    """
    Destroying MPL figure event, calls subscribers.
    'figure' parameter is of the type FigureWindow defined below
    """
    global _destroy_cbs
    for callback, userdata in _destroy_cbs.iteritems():
        try:
            callback(figure, userdata)
        except TypeError:
            callback(figure)


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance. MPL backend function.
    """
    FigureClass = kwargs.pop(
        'FigureClass', matplotlib.backends.backend_qt4agg.Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure. MPL backend
    function.
    """
    canvas = FigureCanvas(figure)
    manager = FigureManagerMdi(canvas, num)
    return manager


class FigureWindow(QtGui.QMdiSubWindow):

    """
    A basic MDI sub-window, but with a closing signal, and an activate QAction,
    which allows for switching between all FigureWindows (e.g. by a
    Windows-menu). An exclusive, static action group makes sure only one
    window can be active at the time. If you want to split the windows into
    different groups that can be treated separately, you will need to create
    your own QActionGroups.
    """
    closing = QtCore.Signal()

    activeFigureActionGroup = QtGui.QActionGroup(None)
    activeFigureActionGroup.setExclusive(True)

    def __init__(self, *args, **kwargs):
        super(FigureWindow, self).__init__(*args, **kwargs)
        self._activate_action = None
        if os.environ['QT_API'] != 'pyside':
            self.windowStateChanged.connect(self._windowStateChanged)

    def closeEvent(self, event):
        self.closing.emit()
        super(FigureWindow, self).closeEvent(event)

    def activateAction(self):
        """
        Returns a QAction that will activate the window with setActiveSubWindow
        as long as it has an mdiArea set. If not, it will use activateWindow to
        try to make it the active window.
        """
        if self._activate_action is not None:
            return self._activate_action
        self._activate_action = QtGui.QAction(self.windowTitle(), self)
        self._activate_action.setCheckable(True)
        self._activate_action.triggered.connect(self._activate_triggered)
        self.activeFigureActionGroup.addAction(self._activate_action)
        return self._activate_action

    def setWindowTitle(self, title):
        # Overridden to keep action text updated
        super(FigureWindow, self).setWindowTitle(title)
        if self._activate_action is not None:
            self._activate_action.setText(title)

    def _windowStateChanged(self, oldState, newState):
        # Event for tracking if we're active or not
        isactive = newState & QtCore.Qt.WindowActive
        if isactive == oldState & QtCore.Qt.WindowActive:
            return  # Another window state changed, e.g. activation
        self._activate_action.setChecked(isactive)

    def _activate_triggered(self, checked=True):
        # Activate action triggered, make window active
        if self.mdiArea():
            self.mdiArea().setActiveSubWindow(self)
        else:
            self.activateWindow()   # If not subwindow

        if self.isMinimized():
            self.showNormal()   # Restore minimized window
        if not checked:
            # User unchecked, which makes no sense, recheck
            self._activate_action.setChecked(True)


class FigureManagerMdi(FigureManagerBase):

    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The qt.QToolBar
    window      : The FigureWindow

    Our MPL figure manager class. Much of the code is copied from MPL Qt4
    backend, but adapted for our needs.
    """

    def __init__(self, canvas, num):
        FigureManagerBase.__init__(self, canvas, num)
        self.canvas = canvas
        self.window = FigureWindow()
        self.window.closing.connect(canvas.close_event)
        self.window.closing.connect(self._widgetclosed)

        self.window.setWindowTitle("Figure %d" % num)
        image = os.path.join(matplotlib.rcParams['datapath'],
                             'images', 'matplotlib.png')
        self.window.setWindowIcon(QtGui.QIcon(image))

        # Give the keyboard focus to the figure instead of the
        # manager; StrongFocus accepts both tab and click to focus and
        # will enable the canvas to process event w/o clicking.
        # ClickFocus only takes the focus is the window has been
        # clicked
        # on. http://qt-project.org/doc/qt-4.8/qt.html#FocusPolicy-enum or
        # http://doc.qt.digia.com/qt/qt.html#FocusPolicy-enum
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        self.window._destroying = False

        # No toolbar in figure currently
        self.toolbar = None
        tbs_height = 0

        # resize the main window so it will display the canvas with the
        # requested size:
        cs = canvas.sizeHint()
        self._status_and_tool_height = tbs_height
        height = cs.height() + self._status_and_tool_height
        self.window.resize(cs.width(), height)

        self.window.setWidget(self.canvas)

        _on_new_figure(self.window)

        if matplotlib.is_interactive():
            self.window.show()

        def notify_axes_change(fig):
            # This will be called whenever the current axes is changed
            if self.toolbar is not None:
                self.toolbar.update()
        self.canvas.figure.add_axobserver(notify_axes_change)

    @QtCore.Slot()
    def _show_message(self, s):
        # Fixes a PySide segfault.
        print "Trying to show: " + s
#        self.window.statusBar().showMessage(s)

    def full_screen_toggle(self):
        if self.window.isFullScreen():
            self.window.showNormal()
        else:
            self.window.showFullScreen()

    def _widgetclosed(self):
        if self.window is None or self.window._destroying:
            return
        try:
            Gcf.destroy(self.num)
        except AttributeError:
            pass
            # It seems that when the python session is killed,
            # Gcf can get destroyed before the Gcf.destroy
            # line is run, leading to a useless AttributeError.

    def resize(self, width, height):
        'set the canvas size in pixels'
        self.window.resize(width, height + self._status_and_tool_height)

    def show(self):
        self.window.show()

    def destroy(self, *args):
        _on_destroy(self.window)
        # check for qApp first, as PySide deletes it in its atexit handler
        if QtGui.QApplication.instance() is None:
            return
        if self.window._destroying:
            return
        self.window._destroying = True
        self.window.destroyed.connect(self._widgetclosed)

        if self.toolbar:
            self.toolbar.destroy()
        self.window.close()
        self.window = None
        # self.canvas.figure = None  # Causes exceptions in delayed drawing
        self.canvas = None
        self.toolbar = None

    def get_window_title(self):
        return str(self.window.windowTitle())

    def set_window_title(self, title):
        self.window.setWindowTitle(title)

# Definition for MPL backend:
FigureManager = FigureManagerMdi
