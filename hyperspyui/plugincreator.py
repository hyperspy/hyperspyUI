# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 12:04:06 2015

@author: Vidar Tonaas Fauske
"""


"""
Utility to make it easier to create plugins directly through the UI.
"""

import os
import hyperspyui.plugins.plugin

header = """from hyperspyui.plugins.plugin import Plugin
import numpy as np
from hyperspy.hspy import *

class {0}(Plugin):
    name = "{0}"
    
    def create_actions(self):"""

action_noicon = """
        self.add_action('{0}.default', "{0}", self.default,
                        tip="")
"""

action_icon = """
        self.add_action('{0}.default', "{0}", self.default,
                        icon="{1}",
                        tip="")
"""

menu_def = """
    def create_menu(self):
        self.add_menuitem('{0}', self.ui.actions['{1}.default'])
"""

toolbar_def = """
    def create_toolbars(self):
        self.add_toolbar_button('{0}', self.ui.actions['{1}.default'])
"""

default = """
    def default(self):
{0}
"""

def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))
    
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
    
    plugin_code = header.format(name)
    if icon is None:
        plugin_code += action_noicon.format(name)
    else:
        plugin_code += action_icon.format(name, icon)
    if menu:
        plugin_code += menu_def.format(category, name)
    if toolbar:
        plugin_code += toolbar_def.format(category, name)
        
    # Indent code by two levels
    code = indent(code, 2*4)
    plugin_code += default.format(code)
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
    