# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:35:52 2014

@author: vidarton
"""

from python_qt_binding import QtCore, QtGui
from collections import OrderedDict

class Actionable(QtCore.QObject):
    """
    Base class for simple action management utilities. Manages actions dict,
    and adds actions through add_action().
    """
    def __init__(self):
        super(Actionable, self).__init__()
        self.actions = OrderedDict()
        self.sep_counter = 0
    
    def add_action(self, key, title, on_trig):
        ac = QtGui.QAction(title, self) # TODO: tr()
        self.connect(ac, QtCore.SIGNAL('triggered()'), on_trig)
        self.actions[key] = ac
        
    def add_separator(self):
        self.sep_counter += 1
        ac = QtGui.QAction(self)
        ac.setSeparator(True)
        self.actions[self.sep_counter] = ac