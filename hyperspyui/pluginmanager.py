# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 00:41:15 2014

@author: Vidar Tonaas Fauske
"""

class PluginManager(object):
    def __init__(self, main_window):
        """
        Initializates the manager, and performs discovery of plugins
        """
        self.plugins = []
        self.plugin_globals = {}
        self.main_window = main_window
        
        self.discover()
        
    def discover(self):
        import plugins.plugin
        import plugins
        for plug in plugins.__all__:
            __import__('plugins.' + plug, globals())
        master = plugins.plugin.Plugin
        self.implementors = self._inheritors(master)
            
    def _inheritors(self, klass):
        subclasses = set((klass,))
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses
            
    
    def init_plugins(self):
        self.plugins = []
        for plug_type in self.implementors:
            p = plug_type(self.main_window)
            self.plugins.append(p)
            
    def create_actions(self):
        for p in self.plugins:
            p.create_actions()
            
    def create_menu(self):
        for p in self.plugins:
            p.create_menu()
    
    def create_toolbars(self):
        for p in self.plugins:
            p.create_toolbars()
            
    def create_widgets(self):
        for p in self.plugins:
            p.create_widgets()