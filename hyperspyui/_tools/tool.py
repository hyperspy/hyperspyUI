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
Created on Sun Dec 07 03:48:36 2014

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore


class Tool(QtCore.QObject):

    def get_name(self):
        raise NotImplementedError()

    def get_category(self):
        return None

    def get_description(self):
        name = self.get_name()
        if name is None:
            return None
        if self.is_selectable():
            return "Select the " + name + "."
        elif self.single_action():
            return "Run the " + name + "."
        return None

    def get_icon(self):
        return None

    def single_action(self):
        return None

    def is_selectable(self):
        return False

    def connect(self, targets=None):
        pass

    def disconnect(self, targets=None):
        pass
