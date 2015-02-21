# -*- coding: utf-8 -*-
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
        super(MainWindowLayer4, self).add_action(key, label, callback, 
                                                 tip, icon, shortcut, userdata,
                                                 selection_callback)
        self.monitor_action(key)

    def monitor_action(self, key):
        self.actions[key].triggered.connect(lambda: self.record_action(key))

    def record_action(self, key):
        for r in self.recorders:
            r.add_action(key)

    def on_console_executing(self, source):
        super(MainWindowLayer4, self).on_console_executing(source)
        for r in self.recorders:
            r.add_code(source)
