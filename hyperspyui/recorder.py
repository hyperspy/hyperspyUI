# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 12:03:33 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtCore

from plugincreator import create_plugin_code

class Recorder(QtCore.QObject):
    record = QtCore.Signal(basestring)
    
    def __init__(self):
        super(Recorder, self).__init__()
        
        self.steps = list()
        self.pause_recording = False
    
    # ------ Recording API ------
    def add_code(self, code):
        if not self.pause_recording:
            step = ('code', code.rstrip('\n'))
            self.steps.append(step)
            self._on_record(step)
    
    def add_action(self, action_key):
        if not self.pause_recording:
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
            return step[1] + '\n'
        elif step[0] == 'action':
            return "ui.actions['{0}'].trigger()\n".format(step[1])
    
    def to_code(self):
        code = ""
        for step in self.steps:
            code += self.step_to_code(step)
        return code
    
    def to_plugin(self, name, category=None, menu=False, toolbar=False, 
                  icon=None):
        code = "ui = self.ui\n"
        code += "siglist = ui.signals\n"
        code += self.to_code()
        
        return create_plugin_code(code, name, category, menu, toolbar, icon)
