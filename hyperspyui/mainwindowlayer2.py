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
Created on Sat Feb 21 15:59:57 2015

@author: Vidar Tonaas Fauske
"""


from mainwindowlayer1 import MainWindowLayer1, tr

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import hooktraitsui

hooktraitsui.hook_traitsui()


class MainWindowLayer2(MainWindowLayer1):

    """
    Second layer in the application stack. Adds traits capture functionality.
    """

    def __init__(self, parent=None):
        # traitsui backend bindings
        hooktraitsui.connect_created(self.on_traits_dialog)
        hooktraitsui.connect_destroyed(self.on_traits_destroyed)

        super(MainWindowLayer2, self).__init__(parent)

    # --------- traitsui Events ---------

    def capture_traits_dialog(self, callback):
        self.should_capture_traits = callback

    def on_traits_dialog(self, dialog, ui, parent):
        self.traits_dialogs.append(dialog)
        if parent is None:
            if self.should_capture_traits:
                self.should_capture_traits(dialog)
                self.should_capture_traits = None
            else:
                dialog.setParent(self, QtCore.Qt.Tool)
                dialog.show()
                dialog.activateWindow()

    def on_traits_destroyed(self, dialog):
        if dialog in self.traits_dialogs:
            self.traits_dialogs.remove(dialog)

    # --------- End traitsui Events ---------
