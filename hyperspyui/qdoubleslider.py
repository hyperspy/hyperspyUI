# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 18:08:16 2014

@author: vidarton
"""

# Qt
from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import QSlider

class QDoubleSlider(QSlider):

    valueChanged = QtCore.Signal(float)    
    
    def __init__(self, parent=None, orientation=None):
        if orientation is None:
            super(QDoubleSlider, self).__init__(parent)
        else:
            super(QDoubleSlider, self).__init__(orientation, parent)
        self.steps = 1000
        self._range = (0.0, 1.0)
        self.connect(self, SIGNAL('valueChanged(int)'), self._on_change)
        

    def setRange(self, vmin, vmax):
        self._range = (vmin, vmax)
        return super(QDoubleSlider, self).setRange(0, self.steps)
        
    def setValue(self, value):
        vmin, vmax = self._range
        try:
            v = int((value - vmin) * self.steps / (vmax - vmin))
        except ZeroDivisionError:
            v = 0
        return super(QDoubleSlider, self).setValue(v)
        
    def value(self):
        v = super(QDoubleSlider, self).value()
        return self._int2dbl(v)
        
    def _int2dbl(self, intval):
        vmin, vmax = self._range
        return vmin + intval * (vmax - vmin) / self.steps
        
    def _on_change(self, intval):
        dblval = self._int2dbl(intval)
        self.valueChanged.emit(dblval)
        
    