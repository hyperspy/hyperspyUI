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
Created on Wed Jan 07 20:01:34 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.widgets.extendedqwidgets import FigureWidget

from qtpy import QtWidgets


class TraitsWidget(FigureWidget):

    """
    DockWidget for TraitsUI dialogs. The default behavior is to update the
    dialog when the active subwindow changes or when the widget becomes visible
    (updates are supressed when widget is hidden). This is done by capturing
    the traitsui dialog as it is created (see code in mainwindowbase).
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
        super().__init__(main_window, parent)

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
        super()._on_figure_change(window)

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
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
        sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        traits_dialog.layout().setSizeConstraint(
                QtWidgets.QLayout.SetDefaultConstraint)
        traits_dialog.setSizePolicy(sp)

        # Set widget
        self.setWidget(traits_dialog)
        traits_dialog.show()
