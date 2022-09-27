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
Created on Sat Feb 21 12:04:06 2015

@author: Vidar Tonaas Fauske
"""


"""
Utility to make it easier to create plugins directly through the UI.
"""

import os
import string

import hyperspyui.plugins.plugin

header = """from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs

class {0}(Plugin):
    name = "{1}"

    def create_actions(self):"""

action_noicon = """
        self.add_action(self.name + '.default', self.name, self.default,
                        tip="")
"""

action_icon = """
        self.add_action(self.name + '.default', self.name, self.default,
                        icon="{0}",
                        tip="")
"""

menu_def = """
    def create_menu(self):
        self.add_menuitem('{0}', self.ui.actions[self.name + '.default'])
"""

toolbar_def = """
    def create_toolbars(self):
        self.add_toolbar_button('{0}', self.ui.actions[self.name + '.default'])
"""

default = """
    def default(self):
{0}
"""


def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n' + padding).join(lines.split('\n'))


def suggest_plugin_filename(name):
    filename = name.lower() + '.py'
    dirname = os.path.dirname(hyperspyui.plugins.plugin.__file__)
    path = dirname + os.path.sep + filename
    return path


def create_plugin_code(code, name, category=None, menu=False, toolbar=False,
                       icon=None):
    """Create a plugin with an action that will execute 'code' when triggered.
    If 'menu' and/or 'toolbar' is True, the corresponding items will be added
    for the action.
    """

    if category is None:
        category = name

    safe_name = string.capwords(name).replace(" ", "")
    plugin_code = header.format(safe_name, name)
    if icon is None:
        plugin_code += action_noicon.format()
    else:
        plugin_code += action_icon.format(icon)
    if menu:
        plugin_code += menu_def.format(category)
    if toolbar:
        plugin_code += toolbar_def.format(category)

    # Indent code by two levels
    code = indent(code, 2 * 4)
    plugin_code += default.format(code)
    try:
        import autopep8
        plugin_code = autopep8.fix_code(plugin_code,
                                        options=autopep8.parse_args(
                                         ['--aggressive', '--aggressive', '']))
    except ImportError:
        # in case autopep8 is not installed
        pass
    return plugin_code


def create_plugin_file(code, name, category=None, menu=False, toolbar=False,
                       filename=None):
    """Create a plugin with an action that will execute 'code' when triggered.
    If 'menu' and/or 'toolbar' is True, the corresponding items will be added
    for the action.
    """
    if filename is None:
        path = suggest_plugin_filename(name)
    elif os.path.isabs(filename):
        path = filename
    else:
        dirname = os.path.dirname(hyperspyui.plugins.plugin.__file__)
        path = dirname + os.path.sep + filename

    with open(path, 'w') as f:
        f.write(create_plugin_code(code, name, category, menu, toolbar))
    return path
