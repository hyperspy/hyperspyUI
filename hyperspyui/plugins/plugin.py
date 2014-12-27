# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:26 2014

@author: Vidar Tonaas Fauske
"""

from hyperspyui.settings import Settings

class Plugin(object):
    name = None
    
    def __init__(self, main_window):
        super(Plugin, self).__init__()
        self.ui = main_window
        if self.name is None:
            set_group = 'plugins.' + str.lower(self.__class__.__name__)
            set_group = set_group.replace('.', '')
        else:
            set_group = 'plugins.' + self.name
        self.settings = Settings(self.ui, group=set_group)
        
    def create_actions(self):
        pass
    
    def create_menu(self):
        pass
    
    def create_toolbars(self):
        pass
    
    def create_widgets(self):
        pass
