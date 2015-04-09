# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 20:01:34 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


class TraitsWidget(QDockWidget):

    """
    DockWidget for TraitsUI dialogs. The default behavior is to update the
    dialog when the active subwindow changes or when the widget becomes visible
    (updates are supressed when widget is hidden). This is done by capturing the
    traitsui dialog as it is created (see code in mainwindowlayer1).
    """

    def __init__(
            self, main_window, cb_make_dialog, cb_check=None, parent=None):
        """
        Create a TraitsWidget. 'main_window' is the application main window,
        cb_make_dialog a callback that will raise the dialog (which will then
        be captured), cb_check is an optional callback which determines whether
        the given window is supported for this dialog.
        """
        super(TraitsWidget, self).__init__(parent)
        self.main_window = main_window
        self.cb_check = cb_check
        self.cb_make_dialog = cb_make_dialog
        self._last_window = None

        self.connect_()
        self.visibilityChanged.connect(self.on_visibility)

    def connect_(self, action=None):
        """
        Connects the widget to its update trigger, which is either a supplied
        action, or by default, the subWindowActivated of the MainWindow.
        """
        if action is None:
            action = self.main_window.main_frame.subWindowActivated
        action.connect(self.on_change)

    def disconnect(self, action=None):
        """
        Disconnects an update trigger connected with connect().
        """
        if action is None:
            action = self.main_window.main_frame.subWindowActivated
        action.disconnect(self.on_change)

    def clear_editor(self):
        """
        Empties out the dockwidget.
        """
        w = self.widget()
        if w is not None:
            w.close()
            self.setWidget(None)

    def _check(self, window):
        if window is None:
            return False
        elif self.cb_check is None:
            return True
        else:
            return self.cb_check(window)

    def on_change(self, window):
        """
        Called when a connected update triggers. If the window is valid, it
        sets up the traitsui dialog capture, and calls cb_make_dialog.  If the
        window is invalid, it clears the widget.
        """
        self._last_window = window

        if self._check(window):
            self.main_window.capture_traits_dialog(self.set_traits_editor)
            self.cb_make_dialog(window)
        else:
            self.clear_editor()

    def on_visibility(self, visible):
        if visible:
            self.on_change(self._last_window)

    def set_traits_editor(self, traits_dialog):
        """
        Called when a traitsui dialog has been captured.
        """
        self.clear_editor()
        # Fix resizing
        sp = traits_dialog.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        sp.setHorizontalPolicy(QSizePolicy.Expanding)
        traits_dialog.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
        traits_dialog.setSizePolicy(sp)

        # Set widget
        self.setWidget(traits_dialog)
        traits_dialog.show()
