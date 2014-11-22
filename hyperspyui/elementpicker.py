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
    """
    Tool window for picking elements of an interactive periodic table.
    Takes a signal in the constructor, and 
    """
    element_toggled = Signal(str)
    
    def __init__(self, signal, parent):
        super(ElementPickerWidget, self).__init__(parent)
        self.signal = signal
        self.setWindowTitle("Select elements for " + signal.name)  #TODO: tr
        self.create_controls()
        
        # Make sure we have the Sample node, and Sample.elements
        if not hasattr(signal.signal.metadata, 'Sample'):
            signal.signal.metadata.add_node('Sample')
            signal.signal.metadata.Sample.elements = []

        self.table.element_toggled.connect(self._toggle_element)
        self._set_elements(signal.signal.metadata.Sample.elements)
        
    def _toggle_element(self, element):
        """
        Makes sure the element is toggled correctly for both EDS and EELS.
        Dependent on hyperspy implementation, as there are currently no
        remove_element functions.
        """
        if isinstance(self.signal.signal, hyperspy.signals.EELSSpectrum):
            self._toggle_element_eels(element)
        else:
            self._toggle_element_eds(element)
            
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
        
    def _set_elements(self, elements):
        """
        Sets the table elements. Does not set elements in signal!
        """
        self.table.set_elements(elements)
        
    def make_map(self):
        """
        Make integrated intensity maps for the defines elements. Currently
        only implemented for EDS signals.
        """
        if isinstance(self.signal.signal, hyperspy.signals.EELSSpectrum):
            pass
        else:
            imgs = self.signal.signal.get_lines_intensity()
            for im in imgs:
                self.parent().add_signal_figure(im, im.metadata.General.title)
    
    def create_controls(self):
        """
        Create UI controls.
        """
        self.table = PeriodicTableWidget(self)
        self.table.element_toggled.connect(self.element_toggled)    # Forward
        
        self.map_btn = QPushButton("Map")
        self.map_btn.clicked.connect(self.make_map)
        
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.table)
        vbox.addWidget(self.map_btn)
        
        self.setLayout(vbox)