# -*- coding: utf-8 -*-
"""
Created on Sat Dec 13 00:41:15 2014

@author: Vidar Tonaas Fauske
"""

import os
import sys
import imp
import warnings
from hyperspyui.plugins.plugin import Plugin


class PluginManager(object):

    def __init__(self, main_window):
        """
        Initializates the manager, and performs discovery of plugins
        """
        self.plugins = {}
        self.main_window = main_window

        self.discover()

    def discover(self):
        """Auto-discover all plugins defined in plugin directory.
        """
        import plugins
        for plug in plugins.__all__:
            try:
                __import__('plugins.' + plug, globals())
            except Exception as e:
                warnings.warn(("Could not import hyperspyui plugin \"{0}\"" +
                               " error: {1}").format(plug, e.message))
        master = Plugin
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
        self.plugins = {}
        for plug_type in self.implementors:
            p = plug_type(self.main_window)
            self.plugins[p.name] = p

    def create_actions(self):
        for p in self.plugins.itervalues():
            p.create_actions()

    def create_menu(self):
        for p in self.plugins.itervalues():
            p.create_menu()

    def create_tools(self):
        for p in self.plugins.itervalues():
            p.create_tools()

    def create_toolbars(self):
        for p in self.plugins.itervalues():
            p.create_toolbars()

    def create_widgets(self):
        for p in self.plugins.itervalues():
            p.create_widgets()

    def load(self, plugin_type):
        # Init
        p = plugin_type(self.main_window)
        self.plugins[p.name] = p

        # Order of execution is significant!
        p.create_actions()
        p.create_menu()
        p.create_toolbars()
        p.create_widgets()

    def load_from_file(self, path):
        master = Plugin
        prev = self._inheritors(master)
        name = os.path.splitext(os.path.basename(path))[0]
        mod_name = 'hyperspyui.plugins.' + name
        reload_plugins = mod_name in sys.modules
        imp.load_source(mod_name, path)
        loaded = self._inheritors(master).difference(prev)

        new_ps = []
        for plug_type in loaded:
            if reload_plugins and plug_type.name in self.plugins:
                 # Unload any plugins with same name
                self.unload(self.plugins[plug_type.name])
            p = plug_type(self.main_window)
            self.plugins[p.name] = p
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
        self.plugins.pop(plugin.name)

    def reload(self, plugin):
        new_module = reload(sys.modules[plugin.__module__])
        new_ptype = new_module[plugin.__class__.__name__]
        if new_ptype is not None:
            self.unload(plugin)
            self.load(new_ptype)
