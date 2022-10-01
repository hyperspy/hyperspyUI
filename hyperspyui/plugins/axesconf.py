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
Created on Wed Jan 07 19:56:18 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.widgets.traitswidget import TraitsWidget
from hyperspyui.util import win2sig

from hyperspyui.plugins.plugin import Plugin


class AxesConf(Plugin):

    """
    Makes a widget that allows the configuration of the signal axes. The widget
    captures and displays the traitsui dialog shown by
    signal.axes_manager.show().
    """
    name = "Axes Configuration"

    def __init__(self, main_window):
        super().__init__(main_window)  # Sets self.ui
        self.widget = None

    def create_widgets(self):
        """
        Creates the TraitsWidget (inherits QDockWidget), and adds it to
        self.ui.
        """
        self.widget = TraitsWidget(self.ui, self.make_traits_dialog,
                                   self.valid_window, self.ui)
        self.widget.setWindowTitle("Axes configuration")
        self.widget.hide()  # Initial state hidden
        self.add_widget(self.widget)

    def valid_window(self, window):
        """
        Check whether the window belongs to a signalwrapper.
        """
        sig = win2sig(window)
        return sig is not None

    def make_traits_dialog(self, window):
        """
        Creates the taitsui dialog. The TraitsWidget captures and displays it.
        """
        sig = win2sig(window)
        sig.signal.axes_manager.gui()
