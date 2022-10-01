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
Created on Mon Nov 17 11:35:52 2014

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore, QtWidgets
from collections import OrderedDict


class Actionable(QtCore.QObject):

    """
    Base class for simple action management utilities. Manages actions dict,
    and adds actions through add_action().
    """

    def __init__(self):
        super().__init__()
        self.actions = OrderedDict()
        self.sep_counter = 0

    def add_action(self, key, title, on_trig):
        ac = QtWidgets.QAction(title, self)  # TODO: tr()?
        ac.triggered.connect(on_trig)
        self.actions[key] = ac

    def add_separator(self):
        self.sep_counter += 1
        ac = QtWidgets.QAction(self)
        ac.setSeparator(True)
        self.actions[self.sep_counter] = ac
