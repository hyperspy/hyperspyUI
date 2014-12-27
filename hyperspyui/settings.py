# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 14:21:00 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

class Settings(object):
    def __init__(self, parent=None, group=None, sep='.'):
        self.sep = sep
        self.group = group
        self.parent = parent
        
    def __getitem__(self, key):
        if isinstance(key, tuple):
            key, t = key
        else:
            t = None
        groupings = (self.group + self.sep + key).split(self.sep)
        key = groupings.pop()
        settings = QSettings(self.parent)
        for g in groupings:
            settings.beginGroup(g)
        ret = settings.value(key, t)
        for g in groupings:
            settings.endGroup()
        return ret
        
    def __setitem__(self, key, value):
        groupings = (self.group + self.sep + key).split(self.sep)
        key = groupings.pop()
        settings = QSettings(self.parent)
        for g in groupings:
            settings.beginGroup(g)
        settings.setValue(key, value)
        for g in groupings:
            settings.endGroup()
            
        
    def write(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)
        
        for k, v in d.iteritems():
            settings.setValue(k, v)
        
        if group is not None:
            settings.endGroup()
            
    def read(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)
        
        for k, v in d.iteritems():
            if isinstance(v, tuple):
                settings.value(k, v)
        
        if group is not None:
            settings.endGroup()       