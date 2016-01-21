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
Created on Sat Feb 21 16:09:45 2015

@author: Vidar Tonaas Fauske
"""

from mainwindowlayer3 import MainWindowLayer3, tr

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


class MainWindowLayer4(MainWindowLayer3):

    """
    Fourth layer in the application stack. Adds recorder functionality.
    """

    def __init__(self, parent=None):
        self.recorders = []
        super(MainWindowLayer4, self).__init__(parent)

    def add_action(self, key, label, callback, tip=None, icon=None,
                   shortcut=None, userdata=None, selection_callback=None):
        ac = super(MainWindowLayer4, self).add_action(key, label, callback,
                                                      tip, icon, shortcut, userdata,
                                                      selection_callback)
        # Monitor events needs to trigger first!
        e = self.actions[key].triggered
        e.disconnect()  # Disconnect everything
        self.monitor_action(key)    # Connect monitor
        # Remake callback connection
        if userdata is None:
            self.connect(ac, SIGNAL('triggered()'), callback)
        else:
            def callback_udwrap():
                callback(userdata)
            self.connect(ac, SIGNAL('triggered()'), callback_udwrap)
        return ac

    def monitor_action(self, key):
        self.actions[key].triggered.connect(lambda: self.record_action(key))

    def record_action(self, key):
        for r in self.recorders:
            r.add_action(key)

    def record_code(self, code):
        for r in self.recorders:
            r.add_code(code)

    def on_console_executing(self, source):
        super(MainWindowLayer4, self).on_console_executing(source)
        self.record_code(source)
