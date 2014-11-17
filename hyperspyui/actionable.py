# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:35:52 2014

@author: vidarton
"""

from python_qt_binding import QtCore, QtGui

class Actionable(QtCore.QObject):
    def __init__(self):
        super(Actionable, self).__init__()
        self.actions = {}
    
    def add_action(self, key, title, on_trig):
        ac = QtGui.QAction(title, self) # TODO: tr()
        self.conenct(ac, QtCore.SIGNAL('triggered()'), on_trig)
        self.actions[key] = ac