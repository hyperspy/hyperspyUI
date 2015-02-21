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

header = """
import plugin
import numpy as np
from hyperspy.hspy import *

class {0}(plugin.Plugin):
    name = "{0}"
    
    def create_actions(self):
        self.add_action('{0}.default', "{0}", self.default,
                        tip="")
"""

menu_def = """
    def create_menu(self):
        self.add_menuitem({0}, self.ui.actions[{1}.default])
"""

toolbar_def = """
    def create_toolbars(self):
        self.add_toolbar_button({0}, self.ui.actions[{1}.default])
"""

default = """
    def default(self):
{0}
"""

def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))

def create_plugin(code, name, category=None, menu=False, toolbar=False):
    """Create a plugin with an action that will execute 'code' when triggered.
    If 'menu' and/or 'toolbar' is True, the corresponding items will be added
    for the action.
    """
    
    if category is None:
        category = name
    
    filename = name.lower() + '.py'
    dirname = os.path.dirname(hyperspyui.plugins.plugin.__file__)
    path = dirname + os.path.sep + filename
    
    with open(path, 'w') as f:
        f.write(header.format(name))
        if menu:
            f.write(menu_def.format(category, name))
        if toolbar:
            f.write(toolbar_def.format(category, name))
            
        # Indent code by two levels
        code = indent(code, 2*4)
        f.write(default.format(code))
    return filename
    