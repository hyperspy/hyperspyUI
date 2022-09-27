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
Created on Fri Dec 12 23:44:26 2014

@author: Vidar Tonaas Fauske
"""

from hyperspyui.settings import Settings
from functools import partial


class Plugin:
    name = None

    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window
        if self.name is None:
            set_group = 'plugins/' + str.lower(self.__class__.__name__)
            set_group = set_group.replace('.', '')
        else:
            set_group = 'plugins/' + self.name.replace('/', '-').replace(
                '\\', '-')
        self.settings = Settings(self.ui, group=set_group)

        self.actions = {}
        self.menu_actions = {}
        self.toolbar_actions = {}
        self.tools = []
        self.widgets = set()
        self.dialogs = []

    def add_action(self, key, *args, **kwargs):
        ac = self.ui.add_action(key, *args, **kwargs)
        self.actions[key] = ac

    def add_menuitem(self, category, action, *args, **kwargs):
        self.ui.add_menuitem(category, action, *args, **kwargs)
        if category in self.menu_actions:
            self.menu_actions[category].append(action)
        else:
            self.menu_actions[category] = [action]

    def add_tool(self, tool, selection_callback=None):
        self.ui.add_tool(tool, selection_callback)
        self.tools.append(tool)

    def add_toolbar_button(self, category, action, *args, **kwargs):
        self.ui.add_toolbar_button(category, action, *args, **kwargs)
        if category in self.toolbar_actions:
            self.toolbar_actions[category].append(action)
        else:
            self.toolbar_actions[category] = [action]

    def add_widget(self, widget, *args, **kwargs):
        dock = self.ui.add_widget(widget, *args, **kwargs)
        self.widgets.add(dock)

    def record_code(self, code):
        code = code.replace('<p>', "ui.plugins['{0}']".format(self.name))
        self.ui.record_code(code)

    def create_actions(self):
        pass

    def create_menu(self):
        pass

    def create_tools(self):
        pass

    def create_toolbars(self):
        pass

    def create_widgets(self):
        pass

    def unload(self):
        for category, actions in self.menu_actions.items():
            for action in actions:
                self.ui.menus[category].removeAction(action)
        for category, actions in self.toolbar_actions.items():
            for action in actions:
                self.ui.toolbars[category].removeAction(action)
        for key in self.actions.keys():
            self.ui.actions.pop(key, None)
        for tool in self.tools:
            self.ui.remove_tool(tool)
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

    def _on_dialog_close(self, diag):
        self.dialogs.remove(diag)
        diag.deleteLater()

    def open_dialog(self, dialog, modal=False, delete_on_close=True):
        self.dialogs.append(dialog)
        if delete_on_close:
            dialog.finished.connect(partial(self._on_dialog_close, dialog))
        if modal:
            dialog.exec_()
        else:
            dialog.show()
