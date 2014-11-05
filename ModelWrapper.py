# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:25:54 2014

@author: vidarton
"""


from python_qt_binding import QtCore
#from hyperspy.model import Model


class ModelWrapper(QtCore.QObject):
    added = QtCore.Signal(object, object)
    removed = QtCore.Signal(object, object)
#    changed = QtCore.Signal()
    
    def __init__(self, model, signal_wrapper, name):
        super(ModelWrapper, self).__init__()
        self.model = model
        self.signal = signal_wrapper
        self.name = name
        if self.signal.signal is not self.model.spectrum:
            print self.signal, self.signal.signal, self.model.spectrum
            raise ValueError("signal_wrapper doesn't match model.signal")
        self.components = {}
        self.update_components()
            
    def plot(self):
        self.model.plot()
        
    def update_plot(self):
        self.model.update_plot()
        
    def fit(self):
        self.model.fit()
            
    def multifit(self):
        self.model.multifit()
            
    def fit_component(self, component):
        self.model.fit_component(component)
        

    def update_components(self):
        """ 
        Updates internal list to match model's list (called e.g. after 
        console execute and in constructor)
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
        
    def component_added(self, component):
        self.added.emit(component, self)
    
    def component_removed(self, component):
        self.removed.emit(component, self)
