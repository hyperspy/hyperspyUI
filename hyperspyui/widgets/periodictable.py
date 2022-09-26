# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
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
Created on Fri Nov 21 19:31:50 2014

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Qt

from functools import partial
from hyperspyui._elements import elements
from .extendedqwidgets import ExClickLabel


def tr(text):
    return QtCore.QCoreApplication.translate("PeriodicTable", text)


class PeriodicTableWidget(QtWidgets.QWidget):
    element_toggled = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.elements = {}
        self.toggled = {}
        self.style_off = "* { background-color: rgba(0,0,0,20); padding: 0px}"
        self.style_on = "* { background-color: rgba(128,180,255,255); padding: 0px}"
        self.style_disabled = "* { background-color: rgba(100,0,0,40); padding: 0px}"
        self.create_controls()

    def parse_elements(self, grid):
        #        btn_color = QColor(128, 128, 128)
        for i, row in enumerate(elements):
            j = 0
            for e in row:
                if isinstance(e, tuple):
                    w = QtWidgets.QLabel(e[1], self)
                    grid.addWidget(w, i, j, 1, e[0], Qt.AlignRight)
                    j += e[0]
                elif isinstance(e, dict):
                    w = ExClickLabel(e['id'], self)
                    w.setToolTip(tr(e['name'].capitalize()))
                    w.setAlignment(Qt.AlignCenter)
                    w.setMinimumSize(10, 10)

                    f = partial(self.on_element_click, e)
                    w.clicked.connect(f)

                    self.elements[e['id']] = w
                    self.toggled[e['id']] = False
                    w.setStyleSheet(self.style_off)

                    grid.addWidget(w, i, j)
                    j += 1

    def toggle_element(self, element):
        self.set_element(element, not self.toggled[element])

    def set_elements(self, elements):
        for e in self.elements.keys():
            self.set_element(e, e in elements)

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

    def disable_elements(self, elements):
        for e in elements:
            self.disable_element(e)

    def disable_element(self, element):
        btn = self.elements[element]
        btn.setEnabled(False)
        btn.setStyleSheet(self.style_disabled)

    def enable_elements(self, elements):
        for e in elements:
            self.enable_element(e)

    def enable_element(self, element):
        btn = self.elements[element]
        btn.setEnabled(True)
        btn.setStyleSheet(self.style_disabled)
        if self.toggled[element]:
            style = self.style_on
        else:
            style = self.style_off
        btn.setStyleSheet(style)

    def on_element_click(self, value):
        elid = value['id']
        self.set_element(elid, not self.toggled[elid])
        self.element_toggled.emit(value['id'])

    def sizeHint(self):
        return QtCore.QSize(310, 140)

    def create_controls(self):
        grid = QtWidgets.QGridLayout(self)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        self.parse_elements(grid)
