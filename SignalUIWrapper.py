# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 18:27:15 2014

@author: vidarton
"""

from FigureWrapper import FigureWrapper
from FigureManager import FigureManager

class SignalUIWrapper():
    def __init__(self, signal, ui_parent, name):
#        super(SignalUIWrapper, self).__init__(parent)
        self.signal = signal
        self.name = name
        self.figures = []
        self.parent = ui_parent
        
        self.navigator_plot = None
        self.signal_plot = None
        
        signal = self.signal
        signal.plot()
        if signal._plot.navigator_plot:
            navi = signal._plot.navigator_plot.figure
            self.navigator_plot = FigureWrapper(navi, self.parent, self.nav_closed)
            self.add_figure(self.navigator_plot)
        if signal._plot.signal_plot is not None:
            sigp = signal._plot.signal_plot.figure
            self.signal_plot = FigureWrapper(sigp, self.parent, self.sig_closed)
            self.add_figure(self.signal_plot)
            
    def update_figures(self):
        oldnav = self.navigator_plot
        oldsig = self.signal_plot
        
        signal = self.signal
        if oldnav is None and oldsig is None:
            signal.plot()
        if signal._plot.navigator_plot is not None:
            navi = signal._plot.navigator_plot.figure
            self.navigator_plot.change_fig(navi)
        elif oldnav is not None:
            oldnav.close()
            
        if signal._plot.signal_plot is not None:
            sigp = signal._plot.signal_plot.figure
            self.signal_plot.change_fig(sigp)
        elif oldsig is not None:
            oldsig.close()
        
    def claim_new_figures(self):
        fm = FigureManager.Instance()
        new = fm.proc_new_figs()
        for f in new:
            self.add_figure(f)
        return new
        
    def add_figure(self, fig):
        self.figures.append(fig)
        fig.signal = self
        
    def nav_closed(self):
        pass
    
    def sig_closed(self):
        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None
    
    def close(self):
        if self.signal_plot is not None:
            self.signal_plot.close()
            self.signal_plot = None
            
        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None