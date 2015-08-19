# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 03:48:36 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtCore


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
