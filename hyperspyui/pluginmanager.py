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
Created on Sat Dec 13 00:41:15 2014

@author: Vidar Tonaas Fauske
"""

import os
import sys
import glob
import importlib
import warnings
import traceback

from hyperspyui.log import logger
from hyperspyui.plugins.plugin import Plugin
from hyperspyui.settings import Settings
from hyperspyui.util import AttributeDict


class ReadOnlyDict(dict):
    _readonly = False

    def __setitem__(self, key, value):

        if self._readonly:
            raise TypeError("This dictionary is read only")
        return dict.__setitem__(self, key, value)

    def __delitem__(self, key):

        if self._readonly:
            raise TypeError("This dictionary is read only")
        return dict.__delitem__(self, key)

    def pop(self, *args, **kwargs):
        if self._readonly:
            raise TypeError("This dictionary is read only")
        return dict.pop(*args, **kwargs)

    def update(self, *args, **kwargs):
        if self._readonly:
            raise TypeError("This dictionary is read only")
        return dict.update(*args, **kwargs)


class PluginManager:

    def __init__(self, main_window):
        """
        Initializates the manager, and performs discovery of plugins
        """
        self.plugins = AttributeDict()
        self.ui = main_window
        self._enabled = {}
        self.settings = Settings(self.ui, group="General")
        self.settings.set_default("extra_plugin_directories", "")
        self.enabled_store = Settings(self.ui, group="PluginManager/enabled")

        self.discover()

    @property
    def enabled(self):
        """Returns a read-only dictionary showing the enabled/disabled state
        of all plugins.
        """
        d = ReadOnlyDict()
        for name, (enabled, _) in d.items():
            d[name] = enabled
        d._readonly = True
        return d

    def enable_plugin(self, name, value=True):
        """Enable/disable plugin functionality. Also loads/unloads plugin. If
        enabling and the plugin is already loaded, this will reload the plugin.
        """
        self.enabled_store[name] = value
        ptype = self._enabled[name][1]
        self._enabled[name] = (value, ptype)
        if name in self.plugins:
            self.unload(self.plugins[name])
        if value:
            self.load(ptype)

    def disable_plugin(self, name):
        """Disable plugin functionality. Also unloads plugin.
        """
        self.enable_plugin(name, False)

    def _import_plugin_from_path(self, name, path):
        try:
            mname = "hyperspyui.plugins." + name
            if sys.version_info >= (3, 5):
                import importlib.util
                spec = importlib.util.spec_from_file_location(mname, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                from importlib.machinery import SourceFileLoader
                loader = SourceFileLoader(mname, path)
                loader.load_module()
        except Exception:
            self.warn("import", path)

    def discover(self):
        """Auto-discover all plugins defined in plugin directory.
        """
        import hyperspyui.plugins as plugins
        for plug in plugins.__all__:
            try:
                __import__('hyperspyui.plugins.' + plug, globals())

            except Exception:
                self.warn("import", plug)

        # Import any plugins in extra dirs.
        extra_paths = self.settings['extra_plugin_directories']
        if extra_paths:
            extra_paths = extra_paths.split(os.path.pathsep)
            for path in extra_paths:
                if not os.path.isdir(path):
                    path = os.path.dirname(path)
                modules = glob.glob(path + "/*.py")
                # TODO: In release form, we should consider supporting
                # compiled plugins in pyc/pyo format
                # modules.extend(glob.glob(os.path.dirname(__file__)+"/*.py?"))
                # If so, ensure that duplicates are removed (picks py over pyc)
                modules = [m for m in modules
                           if not os.path.basename(m).startswith('_')]

                for m in modules:
                    name = os.path.splitext(os.path.basename(m))[0]
                    self._import_plugin_from_path(name, m)

        master = Plugin
        self.implementors = sorted(self._inheritors(master), key=lambda x: x.name)
        logger.debug("Found plugins: %s", self.implementors)

    @staticmethod
    def _inheritors(klass):
        """Return all defined classes that inherit from 'klass'.
        """
        subclasses = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    def warn(self, f_name, p_name, category=RuntimeWarning):
        tbf = ''.join(traceback.format_exception(*sys.exc_info())[2:])
        warnings.warn(("Exception in {0} of hyperspyui plugin " +
                       "\"{1}\" error:\n{2}").format(f_name, p_name, tbf),
                      RuntimeWarning, 2)

    def init_plugins(self):
        self.plugins.clear()
        for plug_type in self.implementors:
            try:
                self._load_if_enabled(plug_type)
            except Exception:
                self.warn("initialization", plug_type.name)

    def create_actions(self):
        for p in self.plugins.values():
            try:
                p.create_actions()
            except Exception:
                self.warn(sys._getframe().f_code.co_name, p.name)

    def create_menu(self):
        for p in self.plugins.values():
            try:
                p.create_menu()
            except Exception:
                self.warn(sys._getframe().f_code.co_name, p.name)

    def create_tools(self):
        for p in self.plugins.values():
            try:
                p.create_tools()
            except Exception:
                self.warn(sys._getframe().f_code.co_name, p.name)

    def create_toolbars(self):
        for p in self.plugins.values():
            try:
                p.create_toolbars()
            except Exception:
                self.warn(sys._getframe().f_code.co_name, p.name)

    def create_widgets(self):
        for p in self.plugins.values():
            try:
                p.create_widgets()
            except Exception:
                self.warn(sys._getframe().f_code.co_name, p.name)

    def _load_if_enabled(self, p_type):
        if p_type is None or p_type.name is None:
            return None
        if self.enabled_store[p_type.name] is None:
            # Init setting to True on first encounter
            self.enabled_store[p_type.name] = True
        enabled = self.enabled_store[p_type.name, bool]
        self._enabled[p_type.name] = (enabled, p_type)
        if enabled:
            # Init
            logger.debug("Initializing plugin: %s", p_type)
            p = p_type(self.ui)
            self.plugins[p.name] = p
            logger.debug("Plugin loaded: %s", p.name)
            return p
        return None

    def load(self, plugin_type):
        try:
            p = self._load_if_enabled(plugin_type)

            if p is not None:
                # Order of execution is significant!
                p.create_actions()
                p.create_menu()
                p.create_tools()
                p.create_toolbars()
                p.create_widgets()
        except Exception:
            self.warn(sys._getframe().f_code.co_name, plugin_type)

    def load_from_file(self, path):
        master = Plugin
        prev = self._inheritors(master)
        name = os.path.splitext(os.path.basename(path))[0]
        mod_name = 'hyperspyui.plugins.' + name
        reload_plugins = mod_name in sys.modules
        try:
            if sys.version_info >= (3, 5):
                spec = importlib.util.spec_from_file_location(
                    mod_name, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            else:
                importlib.machinery.SourceFileLoader(
                    mod_name, path).load_module()
        except Exception:
            self.warn("import", name)
        loaded = self._inheritors(master).difference(prev)

        new_ps = []
        for plug_type in loaded:
            if reload_plugins and plug_type.name in self.plugins:
                # Unload any plugins with same name
                self.unload(self.plugins[plug_type.name])
            try:
                p = self._load_if_enabled(plug_type)
            except Exception:
                self.warn('load', plug_type.name)
            if p is not None:
                new_ps.append(p)
        for p in new_ps:
            try:
                p.create_actions()
            except Exception:
                self.warn('create_actions', p.name)
        for p in new_ps:
            try:
                p.create_menu()
            except Exception:
                self.warn('create_menu', p.name)
        for p in new_ps:
            try:
                p.create_tools()
            except Exception:
                self.warn('create_tools', p.name)
        for p in new_ps:
            try:
                p.create_toolbars()
            except Exception:
                self.warn('create_toolbars', p.name)
        for p in new_ps:
            try:
                p.create_widgets()
            except Exception:
                self.warn('create_widgets', p.name)
        return new_ps

    def unload(self, plugin):
        plugin.unload()
        self.plugins.pop(plugin.name)

    def reload(self, plugin):
        new_module = importlib.reload(sys.modules[plugin.__module__])
        new_ptype = new_module[plugin.__class__.__name__]
        if new_ptype is not None:
            self.unload(plugin)
            self.load(new_ptype)
