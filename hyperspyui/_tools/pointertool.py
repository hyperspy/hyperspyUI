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
Created on Sun Dec 07 05:23:12 2014

@author: Vidar Tonaas Fauske
"""

import os

from .figuretool import FigureTool


class PointerTool(FigureTool):

    def __init__(self, windows=None):
        super().__init__()

    def get_name(self):
        return "Pointer tool"

    def get_category(self):
        return 'Plot'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/pointer.svg'

    def is_selectable(self):
        return True
