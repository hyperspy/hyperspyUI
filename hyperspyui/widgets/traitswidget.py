# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 20:01:34 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.widgets.extendedqwidgets import FigureWidget

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


class TraitsWidget(FigureWidget):

    """
    DockWidget for TraitsUI dialogs. The default behavior is to update the
    dialog when the active subwindow changes or when the widget becomes visible
    (updates are supressed when widget is hidden). This is done by capturing
    the traitsui dialog as it is created (see code in mainwindowlayer1).
    """

    def __init__(
            self, main_window, cb_make_dialog, cb_check=None, parent=None):
        """
        Create a TraitsWidget. 'main_window' is the application main window,
        cb_make_dialog a callback that will raise the dialog (which will then
        be captured), cb_check is an optional callback which determines whether
        the given window is supported for this dialog.
        """
        self.cb_check = cb_check
        self.cb_make_dialog = cb_make_dialog
        super(TraitsWidget, self).__init__(main_window, parent)

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

    def _on_figure_change(self, window):
        """
        Called when a connected update triggers. If the window is valid, it
        sets up the traitsui dialog capture, and calls cb_make_dialog.  If the
        window is invalid, it clears the widget.
        """
        super(TraitsWidget, self)._on_figure_change(window)

        if self._check(window):
            self.ui.capture_traits_dialog(self.set_traits_editor)
            self.cb_make_dialog(window)
        else:
            self.clear_editor()

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
