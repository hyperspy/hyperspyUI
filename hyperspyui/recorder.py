# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 12:03:33 2015

@author: Vidar Tonaas Fauske
"""

import plugin_creator

class Recorder(object):
    def __init__(self):
        super(Recorder, self).__init__()
        
        self.steps = list()
        
    def add_code(self, code):
        self.steps.append(('code', code))
    
    def add_action(self, action_key):
        self.steps.append(('action', action_key))
        
    def to_code(self):
        code = ""
        for step_type, step in self.steps:
            if step_type == 'code':
                code += step + '\n'
            elif step_type == 'action':
                code += "ui.actions['{0}'].trigger()".format(step)
        return code
        
    def to_plugin(self, name, category=None, menu=False, toolbar=False):
        code = r"ui = self.ui"
        code += r"siglist = ui.signals"
        code += self.to_code()
        
        fn = plugin_creator.create_plugin(code, name, category, menu, toolbar)
        return fn