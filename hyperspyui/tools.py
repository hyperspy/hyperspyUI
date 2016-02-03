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
Created on Sun Dec 07 03:06:55 2014

@author: Vidar Tonaas Fauske
"""


from _tools.tool import Tool
from _tools.figuretool import FigureTool
try:
    from _tools.signalfiguretool import SignalFigureTool
    from _tools.selectiontool import SelectionTool
    from _tools.multiselectiontool import MultiSelectionTool
    from _tools.linetool import LineTool
except ImportError:
    pass
from _tools.pointertool import PointerTool
from _tools.hometool import HomeTool
from _tools.zoompan import ZoomPanTool
from _tools.gaussiantool import GaussianTool

default_tools = [PointerTool, HomeTool, ZoomPanTool, GaussianTool]
