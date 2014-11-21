# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 22:22:33 2014

@author: vidarton
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import hyperspy.signals

from extendedqwidgets import QToolWindow
from periodictable import PeriodicTableWidget

class ElementPickerWidget(QToolWindow):
    element_toggled = Signal(str)
    
    def __init__(self, signal, parent):
        super(ElementPickerWidget, self).__init__(parent)
        self.signal = signal
        self.setWindowTitle("Select elements for " + signal.name)  #TODO: tr
        self.create_controls()
        
        if not hasattr(signal.signal.metadata, 'Sample'):
            signal.signal.metadata.add_node('Sample')
            signal.signal.metadata.Sample.elements = []
        
        if isinstance(signal.signal, hyperspy.signals.EELSSpectrum):
            f = self._toggle_element_eels
        else:
            f = self._toggle_element_eds
            
        self.table.element_toggled.connect(f)
        self.set_elements(signal.signal.metadata.Sample.elements)
            
    def _toggle_element_eds(self, element):
        if element in self.signal.signal.metadata.Sample.elements:
            self.signal.signal.metadata.Sample.elements.remove(element)
        else:
            self.signal.signal.add_elements((element,))
                
    def _toggle_element_eels(self, element):
        if element in self.signal.signal.metadata.Sample.elements:
            self.signal.signal.elements.remove(element)
            self.signal.signal.subshells = set()
            self.signal.signal.add_elements([])
        else:
            self.signal.signal.add_elements((element,))
        
    def set_elements(self, elements):
        self.table.set_elements(elements)
        
    def make_map(self):
        if isinstance(self.signal.signal, hyperspy.signals.EELSSpectrum):
            pass
        else:
            imgs = self.signal.signal.get_lines_intensity()
            for im in imgs:
                self.parent().add_signal_figures(im, im.metadata.General.title)
    
    def create_controls(self):
        self.table = PeriodicTableWidget(self)
        self.table.element_toggled.connect(self.element_toggled)    # Forward
        
        self.map_btn = QPushButton("Map")
        self.map_btn.clicked.connect(self.make_map)
        
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.table)
        vbox.addWidget(self.map_btn)
        
        self.setLayout(vbox)