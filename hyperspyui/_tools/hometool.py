# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 03:49:54 2014

@author: Vidar Tonaas Fauske
"""

import os
from matplotlib.pylab import gca

from figuretool import FigureTool


class HomeTool(FigureTool):

    def __init__(self, windows=None):
        super(HomeTool, self).__init__(windows)

    def get_name(self):
        return "Home tool"

    def get_category(self):
        return 'Navigation'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/home.svg'

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
