# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 13:48:22 2014

@author: vidarton
"""


import matplotlib.pyplot as plt

import FigureWrapper
from util import lstrip
from Singleton import Singleton

@Singleton
class FigureManager():
    def __init__(self):
        self._list = {}
        
    # A bit of a hack. Should integrate throught util.create_figure() instead?        
    def proc_new_figs(self):
        plt.draw()
        new = []
        nums = plt.get_fignums()
        for n in nums:
            f = plt.figure(n)
            key = lstrip(f.canvas.get_window_title(), "Figure ")
            if not self._list.has_key(key):
                f = FigureWrapper.FigureWrapper(f, on_close=self.remove_fig)
                self.add(f)
                new.append(f)
        return new
        
    def add(self, fig):
        self._list[fig.title] = fig
    
    def remove(self, fig):
        if isinstance(fig, str):
            if self._list.has_key(fig):
                self._list.pop(fig)
        elif isinstance(fig, FigureWrapper.FigureWrapper):
            for n, f in self._list.iteritems():
                if f == fig:
                    self._list.pop(n)
                    break
        
        