# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 18:27:15 2014

@author: vidarton
"""

from util import fig2win
from python_qt_binding import QtCore

from ModelWrapper import ModelWrapper
import hyperspy.hspy

class SignalUIWrapper(QtCore.QObject):
    
    model_added = QtCore.Signal(object)
    model_removed = QtCore.Signal(object)
    
    def __init__(self, signal, ui_parent, name):
        super(SignalUIWrapper, self).__init__()
        self.signal = signal
        self.name = name
        self.figures = []
        self.parent = ui_parent
        self.models = []
        
        self._keep_on_close = False
        
        self.navigator_plot = None
        self.signal_plot = None
        
        self._nav_geom = None
        self._sig_geom = None
        
        self._model_id = 1
        
        self.plot()

    @property
    def keep_on_close(self):
        return self._keep_on_close
    
    @keep_on_close.setter
    def keep_on_close(self, value):
        self._keep_on_close = value

    def plot(self):
        self.signal.plot()
        self.update_figures()
            
    def update_figures(self):  
        self.remove_figure(self.navigator_plot)
        self.remove_figure(self.signal_plot)
        self.navigator_plot = None
        self.signal_plot = None
        
        if self.signal._plot.navigator_plot:
            navi = self.signal._plot.navigator_plot.figure
            navi.axes[0].set_title("")
            self.navigator_plot = fig2win(navi, self.parent.figures)
            self.navigator_plot.closing.connect(self.nav_closing)
            self.add_figure(self.navigator_plot)
            if self._nav_geom is not None:
                self.navigator_plot.restoreGeometry(self._nav_geom)
            
        if self.signal._plot.signal_plot is not None:
            sigp = self.signal._plot.signal_plot.figure
            sigp.axes[0].set_title("")
            self.signal_plot = fig2win(sigp, self.parent.figures)
            self.signal_plot.closing.connect(self.sig_closing)
            self.add_figure(self.signal_plot)
            if self._sig_geom is not None:
                self.signal_plot.restoreGeometry(self._sig_geom)
        
    def add_figure(self, fig):
        self.figures.append(fig)
        
    def remove_figure(self, fig):
        if fig in self.figures:
            self.figures.remove(fig)
            
    def make_model(self, *args, **kwargs):   
        m = hyperspy.hspy.create_model(self.signal, *args, **kwargs)
#        modelname = self.signal.metadata.General.title
        modelname = "Model%d" % self._model_id
        self._model_id += 1
        mw = ModelWrapper(m, self, modelname)
        self.add_model(mw)
        return mw
        
    def add_model(self, model):
        self.models.append(model)
        self.model_added.emit(model)
        
    def remove_model(self, model):
        self.models.remove(model)
        self.model_removed.emit(model)
        
    def nav_closing(self):
        self._nav_geom = self.navigator_plot.saveGeometry()
        if self.signal_plot is None:
            self._closed()
    
    def sig_closing(self):
        self._sig_geom = self.signal_plot.saveGeometry()
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
        # TODO: Should probably be with by events for concistency
        if self in self.parent.signals and not self.keep_on_close:
            self.parent.signals.remove(self)