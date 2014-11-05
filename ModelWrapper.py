# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:25:54 2014

@author: vidarton
"""


#from hyperspy.model import Model

class ModelWrapper():
    def __init__(self, model, signal_wrapper):
        self.model = model
        self.signal = signal_wrapper
        if self.signal.signal != self.model.spectrum:
            raise ValueError("signal_wrapper doesn't match model.signal")
            
    def plot(self):
        self.model.plot()
        
    def update_plot(self):
        self.model.update_plot()
        
        
import hyperspy.hspy

import traitsui

        
def add_model(self, model_wrap):
    
form = None
create_model = form.create_model