# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:26 2014

@author: Vidar Tonaas Fauske
"""


class Plugin(object):
    def __init__(self, main_window):
        super(Plugin, self).__init__()
        self.ui = main_window
        
    def create_actions(self):
        pass
    
    def create_menu(self):
        pass
    
    def create_toolbars(self):
        pass
    
    def create_widgets(self):
        pass
