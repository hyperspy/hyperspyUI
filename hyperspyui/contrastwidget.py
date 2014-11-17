# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 16:49:48 2014

@author: vidarton
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from qdoubleslider import QDoubleSlider

class ContrastWidget(QDockWidget):
    def __init__(self, parent=None, figure=None):
        super(ContrastWidget, self).__init__(parent)
        self.create_controls()        
        
        self.on_figure_change(figure)
        
    def apply_cb(self):
        # TODO: Change by modifing matplotlib figure Normalization
        pass
        
    def on_figure_change(self, figure):
        pass
    
    def brightness_changed(self, value):
        pass
    
    def contrast_changed(self, value):
        pass
    
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    def create_controls(self):
        self.sl_brt = QDoubleSlider(self)
        self.lbl_brt = QLabel("Brightness: 0.5")
        self.sl_crt = QDoubleSlider(self)
        self.lbl_brt = QLabel("Contrast: 0.5")
        
        for sl in [self.sl_brt, self.sl_crt]:
            sl.setRange(0.0, 1.0)
            sl.setValue(0.5)
            sl.setPrecision(2)
            
        self.connect(self.sl_brt, SIGNAL('valueChanged(double)'), 
                     self.brightness_changed)
        self.connect(self.sl_crt, SIGNAL('valueChanged(double)'), 
                     self.contrast_changed)