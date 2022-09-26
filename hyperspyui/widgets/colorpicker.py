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
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.


from qtpy import QtGui, QtCore, QtWidgets


class ColorButton(QtWidgets.QPushButton):

    colorChanged = QtCore.Signal([QtGui.QColor])

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(50)
        if color is None:
            color = QtGui.QColor('gray')
        self.color = color
        self.clicked.connect(self.choose_color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self.colorChanged.emit(color)
        self.update()

    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color

    def paintEvent(self, event):
        super().paintEvent(event)
        padding = 5

        rect = event.rect()
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(self.color))
        painter.setPen(QtGui.QColor("#CECECE"))
        rect.adjust(
            padding, padding,
            -1-padding, -1-padding)
        painter.drawRect(rect)
