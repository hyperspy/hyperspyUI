# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 18:27:15 2014

@author: vidarton
"""

from util import fig2win

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
            navi.axes[0].set_title("")
            self.navigator_plot = fig2win(navi, ui_parent.figures)
            self.navigator_plot.closing.connect(self.nav_closed)
            self.add_figure(self.navigator_plot)
            
        if signal._plot.signal_plot is not None:
            sigp = signal._plot.signal_plot.figure
            sigp.axes[0].set_title("")
            self.signal_plot = fig2win(sigp, ui_parent.figures)
            self.signal_plot.closing.connect(self.sig_closed)
            self.add_figure(self.signal_plot)
            
    def update_figures(self):
        self.navigator_plot = self.signal._plot.navigator_plot
        self.signal_plot = self.signal._plot.signal_plot
        
    def add_figure(self, fig):
        self.figures.append(fig)
#        fig.signal = self
        
    def nav_closed(self):
        if self.signal_plot is None:
            self._closed()
    
    def sig_closed(self):
        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None
        self._closed()
    
    def close(self):
        if self.signal_plot is not None:
            self.signal_plot.close()
            self.signal_plot = None
            
        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None
        self._closed()
            
    def _closed(self):
        # TODO: Should probably be done by events for concistency
        if self in self.parent.signals:
            self.parent.signals.remove(self)