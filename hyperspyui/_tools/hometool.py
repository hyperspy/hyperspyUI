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
Created on Sun Dec 07 03:49:54 2014

@author: Vidar Tonaas Fauske
"""

import os
from matplotlib.pylab import gca

from .figuretool import FigureTool


class HomeTool(FigureTool):

    def __init__(self, windows=None):
        super().__init__(windows)

    def get_name(self):
        return "Home tool"

    def get_category(self):
        return 'Plot'

    def get_icon(self):
        return os.path.join(os.path.dirname(__file__), '..', 'images', 'home.svg')

    def single_action(self):
        return self.home

    def home(self, axes=None):
        if axes is None:
            axes = gca()
            if axes is None:
                return
        oldx = axes.get_autoscalex_on()
        oldy = axes.get_autoscaley_on()
        axes.set_xlim(auto=True)
        axes.set_ylim(auto=True)
        axes.autoscale_view(tight=True, scalex=True, scaley=False)
        axes.autoscale_view(tight=None, scalex=False, scaley=True)
        axes.figure.canvas.draw_idle()
        axes.set_xlim(auto=oldx)
        axes.set_ylim(auto=oldy)

    def on_keyup(self, event):
        if event.key == '5':
            self.home()
