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
Created on Sat Feb 21 12:03:33 2015

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore

from .plugincreator import create_plugin_code


class Recorder(QtCore.QObject):
    record = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        self.steps = list()
        self.pause_recording = False
        self.filter = {'actions': True, 'code': True}

    # ------ Recording API ------
    def add_code(self, code):
        if self.filter['code'] and not self.pause_recording:
            step = ('code', code.rstrip('\n'))
            self.steps.append(step)
            self._on_record(step)

    def add_action(self, action_key):
        if self.filter['actions'] and not self.pause_recording:
            step = ('action', action_key)
            self.steps.append(step)
            self._on_record(step)

    # ------ Event processing ------
    def _on_record(self, step):
        self.record.emit(self.step_to_code(step))

    # ------ Output API ------
    @staticmethod
    def step_to_code(step):
        if step[0] == 'code':
            value = step[1] + '\n'
        elif step[0] == 'action':
            value = "ui.actions['{0}'].trigger()\n".format(step[1])
        else:
            value = None
        return value

    def to_code(self):
        code = ""
        for step in self.steps:
            code += self.step_to_code(step)
        return code

    def to_plugin(self, name, category=None, menu=False, toolbar=False,
                  icon=None):
        code = "ui = self.ui\n"
        code += "siglist = ui.hspy_signals\n"
        code += self.to_code()

        return create_plugin_code(code, name, category, menu, toolbar, icon)
