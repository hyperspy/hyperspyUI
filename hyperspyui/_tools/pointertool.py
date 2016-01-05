# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 05:23:12 2014

@author: Vidar Tonaas Fauske
"""

import os

from .figuretool import FigureTool


class PointerTool(FigureTool):

    def __init__(self, windows=None):
        super(PointerTool, self).__init__()

    def get_name(self):
        return "Pointer tool"

    def get_category(self):
        return 'Navigation'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/pointer.svg'

    def is_selectable(self):
        return True
