# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:25:54 2014

@author: vidarton
"""


from python_qt_binding import QtCore, QtGui
#from hyperspy.model import Model
from actionable import Actionable
from functools import partial

# TODO: Add smartfit for EELSModel
class ModelWrapper(Actionable):
    added = QtCore.Signal((object, object), (object,))
    removed = QtCore.Signal((object, object), (object,))
    
    def __init__(self, model, signal_wrapper, name):
        super(ModelWrapper, self).__init__()
        self.model = model
        self.signal = signal_wrapper
        self.name = name
        if self.signal.signal is not self.model.spectrum:
            raise ValueError("signal_wrapper doesn't match model.signal")
        self.components = {}
        self.update_components()
        
        # Default actions
        #TODO: tr()
        self.add_action('plot', "&Plot", self.plot)
        self.add_action('fit', "&Fit", self.fit)
        self.add_action('multifit', "&Multifit", self.multifit)
        self.add_action('set_signal_range', "Set signal &range",
                        self.set_signal_range)
        f = partial(self.signal.remove_model, self)
        self.add_action('delete', "&Delete", f)
        
            
    def plot(self):
        self.signal.keep_on_close = True
        self.model.plot()
        self.signal.keep_on_close = False
        self.signal.update_figures()
        
    def update_plot(self):
        self.model.update_plot()
        
    def fit(self):
        self.signal.keep_on_close = True
        self.model.fit()
        self.signal.keep_on_close = False
        self.signal.update_figures()
            
    def multifit(self):
        self.signal.keep_on_close = True
        self.model.multifit()
        self.signal.keep_on_close = False
        self.signal.update_figures()
            
    def fit_component(self, component):
        # This is a non-blocking call, which means the normal keep_on_close +
        # update_figures won't work. To make sure we keep our figures,
        # we force a plot first if it is not active already.
        if not self.model._plot.is_active():
            self.plot()
        self.model.fit_component(component)
        
    def set_signal_range(self, *args, **kwargs):
        self.signal.keep_on_close = True
        self.model.set_signal_range(*args, **kwargs)
        self.signal.keep_on_close = False
        self.signal.update_figures()
        

    def update_components(self):
        """ 
        Updates internal compoenent list to match model's list (called e.g. 
        after console execute and in constructor)
        """
        
        # Add missing
        for c in self.model:
            if c.name not in self.components.keys():
                self.components[c.name] = c
                self.component_added(c)
        
        # Remove lingering
        ml = [c.name for c in self.model]
        rm = [cn for cn in self.components.keys() if cn not in ml]
        for n in rm:
            c = self.components.pop(n)
            self.component_removed(c)
        
    def add_component(self, component):
        if isinstance(component, type):
            nec = ['EELSCLEdge', 'Spline', 'ScalableFixedPattern']
            if component.name in nec:
                raise TypeError("Component of type %s currently not supported"
                                % component)
            component = component()
        
        added = False
        if component not in self.model:
            self.model.append(component)
            added = True
        if not self.components.has_key(component.name):
            self.components[component.name] = component
            added = True
        if added:
            self.component_added(component)
            
    def remove_component(self, component):
        removed = False
        if component in self.model:
            self.model.remove(component)
            removed = True
        if self.components.has_key(component.name):
            self.components.pop(component.name)
            removed = True
        if removed:
            self.component_removed(component)
            
        
    def component_added(self, component):
        self.update_plot()
        self.added[object, object].emit(component, self)
        self.added[object].emit(component)
    
    def component_removed(self, component):
        self.update_plot()
        self.removed[object, object].emit(component, self)
        self.removed[object].emit(component)
