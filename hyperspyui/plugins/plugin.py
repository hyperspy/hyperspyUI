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
        
        self.actions = {}
        self.menu_actions = {}
        self.toolbar_actions = {}
        self.widgets = set()
        
    def add_action(self, key, *args, **kwargs):
        ac = self.ui.add_action(key, *args, **kwargs)
        self.actions[key] = ac
    
    def add_menuitem(self, category, action, *args, **kwargs):
        self.ui.add_menuitem(category, action, *args, **kwargs)
        self.menu_actions[category] = action
    
    def add_toolbar_button(self, category, action, *args, **kwargs):
        self.ui.add_toolbar_button(category, action, *args, **kwargs)
        self.toolbar_actions[category] = action
        
    def add_widget(self, widget, *args, **kwargs):
        dock = self.ui.add_widget(widget, *args, **kwargs)
        self.widgets.add(dock)
        
    def create_actions(self):
        pass
    
    def create_menu(self):
        pass
    
    def create_toolbars(self):
        pass
    
    def create_widgets(self):
        pass
    
    def unload(self):
        for category, action in self.menu_actions.iteritems():
            self.ui.menus[category].removeAction(action)
        for category, action in self.toolbar_actions.iteritems():
            self.ui.toolbars[category].removeAction(action)
        for key in self.actions.iterkeys():
            self.ui.actions.pop(key, None)
        for widget in self.widgets:
            self.ui.removeDockWidget(widget)
            if widget in self.ui.widgets:
                self.ui.widgets.remove(widget)
            else:
                # Our widget was wrapped, original is in ui.widgets.
                self.ui.widgets.remove(widget.widget())
        self.actions.clear()
        self.menu_actions.clear()
        self.toolbar_actions.clear()
        self.widgets.clear()
