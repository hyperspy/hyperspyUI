# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 00:41:15 2014

@author: Vidar Tonaas Fauske
"""

import os
import sys
import imp

class PluginManager(object):
    def __init__(self, main_window):
        """
        Initializates the manager, and performs discovery of plugins
        """
        self.plugins = []
        self.main_window = main_window
        
        self.discover()
        
    def discover(self):
        """Auto-discover all plugins defined in plugin directory.
        """
        import plugins.plugin
        import plugins
        for plug in plugins.__all__:
            __import__('plugins.' + plug, globals())
        master = plugins.plugin.Plugin
        self.implementors = self._inheritors(master)
    
    @staticmethod
    def _inheritors(klass):
        """Return all defined classes that inherit from 'klass'.
        """
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

    def load(self, plugin_type):
        # Init
        p = plugin_type(self.main_window)
        self.plugins.append(p)
        
        # Order of execution is significant!
        p.create_actions()
        p.create_menu()
        p.create_toolbars()
        p.create_widgets()
        
    def load_from_file(self, path):
        import plugins.plugin
        master = plugins.plugin.Plugin
        prev = self._inheritors(master)
        name = 'hyperspyui.plugins.' + \
                os.path.splitext(os.path.basename(path))[0]
        imp.load_source(name, path)
        loaded = self._inheritors(master).difference(prev)
        
        new_ps = []
        for plug_type in loaded:
            p = plug_type(self.main_window)
            self.plugins.append(p)
            new_ps.append(p)
        for p in new_ps:
            p.create_actions()
        for p in new_ps:
            p.create_menu()
        for p in new_ps:
            p.create_toolbars()
        for p in new_ps:
            p.create_widgets()
        return new_ps
        
    def unload(self, plugin):
        plugin.unload()
        self.plugins.remove(plugin)
        
    def reload(self, plugin):
        new_module = reload(sys.modules[plugin.__module__])
        new_ptype = new_module[plugin.__class__.__name__]
        if new_ptype is not None:
            self.unload(plugin)
            self.load(new_ptype)
            