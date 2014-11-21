# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 19:31:50 2014

@author: vidarton
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from functools import partial
from _elements import elements
from extendedqwidgets import QClickLabel
        
class PeriodicTableWidget(QWidget):
    element_toggled = Signal(str)
    
    def __init__(self, parent=None):
        super(PeriodicTableWidget, self).__init__(parent)
        self.elements = {}
        self.toggled = {}
        self.style_off = "* { background-color: rgba(0,0,0,20); padding: 0px}"
        self.style_on = "* { background-color: rgba(128,180,255,255); padding: 0px}"
        self.create_controls()
    
    def parse_elements(self, grid):
#        btn_color = QColor(128, 128, 128)
        for i, row in enumerate(elements):
            j = 0
            for e in row:
                if isinstance(e, tuple):
                    w = QLabel(e[1], self)
                    grid.addWidget(w, i, j, 1, e[0], Qt.AlignRight)
                    j += e[0]
                elif isinstance(e, dict):
                    w = QClickLabel(e['id'], self)
                    w.setToolTip(e['name'])
                    w.setAlignment(Qt.AlignCenter)
                    w.setMinimumSize(10, 10)
                    
                    f = partial(self.on_element_click, e)
                    w.clicked.connect(f)
                    
                    self.elements[e['id']] = w
                    self.toggled[e['id']] = False
                    w.setStyleSheet(self.style_off)
                    
                    grid.addWidget(w, i, j)
                    j += 1
                    
    def set_elements(self, elements):
        for e in elements:
            self.set_element(e, True)
        
    def set_element(self, element, value):
        if self.toggled[element] == value:
            return
        self.toggled[element] = value
        btn = self.elements[element]
        if value:
            style = self.style_on
        else:
            style = self.style_off
        btn.setStyleSheet(style)
                    
    def on_element_click(self, value):
        elid = value['id']
        self.set_element(elid, not self.toggled[elid] )
        self.element_toggled.emit(value['id'])
        
    def sizeHint(self):
        return QSize(350, 140)
        
    def create_controls(self):
        grid = QGridLayout(self)
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)
        self.parse_elements(grid)
        
      