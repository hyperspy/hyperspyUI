# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 14:22:53 2014

@author: vidarton
"""

import os

import matplotlib.backends.backend_qt4agg
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import FigureManagerBase

from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets, _getSaveFileName, __version__
#from python_qt_binding import QtGui, QtCore

from matplotlib.backends.backend_qt5 import (SPECIAL_KEYS, SUPER, ALT, CTRL,
                        SHIFT, MODIFIER_KEYS, fn_name, cursord,
                        draw_if_interactive, _create_qApp, show, TimerQT,
                        FigureManagerQT, 
                        SubplotToolQt, error_msg_qt, exception_handler)
                 
                 
# =================     
# Event managers
# =================

_new_fig_cbs = {}
_destroy_cbs = {}
def connect_on_new_figure(callback, userdata=None):
    global _new_fig_cbs
    _new_fig_cbs[callback] = userdata

def disconnect_on_new_figure(callback):
    global _new_fig_cbs
    if _new_fig_cbs.has_key(callback):
        _new_fig_cbs.pop(callback)

def _on_new_figure(figure):
    """
    figure parameter is of the type FigureWindow defined below
    """
    global _new_fig_cbs
    for callback, userdata in _new_fig_cbs.iteritems():
        try:
            callback(figure, userdata)
        except TypeError:
            callback(figure)
        

def connect_on_destroy(callback, userdata=None):
    global _destroy_cbs
    _destroy_cbs[callback] = userdata

def disconnect_on_destroy(callback):
    global _destroy_cbs
    if _destroy_cbs.has_key(callback):
        _destroy_cbs.pop(callback)

def _on_destroy(figure):
    global _destroy_cbs
    for callback, userdata in _destroy_cbs.iteritems():
        try:
            callback(figure, userdata)
        except TypeError:
            callback(figure)

def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    FigureClass = kwargs.pop('FigureClass', matplotlib.backends.backend_qt4agg.Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = matplotlib.backends.backend_qt4agg.FigureCanvas(figure)
    manager = FigureManagerMdi(canvas, num)
    return manager


class FigureWindow(QtWidgets.QMdiSubWindow):
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
        self._activate_action.triggered.connect(self._triggered)
        self.activeFigureActionGroup.addAction(self._activate_action)
        return self._activate_action
        
    def setWindowTitle(self, title):
        super(FigureWindow, self).setWindowTitle(title)
        if self._activate_action is not None:
            self._activate_action.setText(title)

    def _windowStateChanged(self, oldState, newState):
        isactive = newState & QtCore.Qt.WindowActive
        if isactive == oldState & QtCore.Qt.WindowActive:
            return  # Another window state changed, e.g. activation
        self._activate_action.setChecked(isactive)
        
    def _triggered(self, checked):
        if self.mdiArea():
            self.mdiArea().setActiveSubWindow(self)
        else:
            self.activateWindow()
        
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
        if self.window._destroying:
            return
        self.window._destroying = True
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
        if QtWidgets.QApplication.instance() is None:
            return
        if self.window._destroying:
            return
        self.window._destroying = True
        self.window.destroyed.connect(self._widgetclosed)

        if self.toolbar:
            self.toolbar.destroy()
        self.window.close()

    def get_window_title(self):
        return str(self.window.windowTitle())

    def set_window_title(self, title):
        self.window.setWindowTitle(title)


FigureCanvas = matplotlib.backends.backend_qt4agg.FigureCanvas
FigureManager = FigureManagerMdi