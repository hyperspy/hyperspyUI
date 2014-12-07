# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 10:30:08 2014

@author: vroot
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 02:03:23 2014

@author: vroot
"""

import os
import copy
from matplotlib.widgets import SpanSelector

from hyperspy.components import Gaussian2

from figuretool import FigureTool
from util import load_cursor

class GaussianTool(FigureTool):
    def __init__(self, windows=None):
        super(GaussianTool, self).__init__(windows)
        self.dragging = False
        self.drag_data = None
        self.span = None
        self.cursor = load_cursor(os.path.dirname(__file__) + \
                                  '/../../images/picker.svg', 8, 8)
        
    def get_name(self):
        return "Gaussian tool"
        
    def get_category(self):
        return 'Components'
        
    def get_icon(self):
        return os.path.dirname(__file__) + '/../../images/gaussian.svg'
        
    def is_selectable(self):
        return True
        
    def on_mousedown(self, event):
        if event.inaxes is None:
            return
        ax = event.inaxes
        f = ax.figure
        x, y = event.xdata, event.ydata
        
        if event.dblclick:
            # Add Gaussian here!
            window = f.canvas.parent()
            mw = window.property('hyperspyUI.ModelWrapper')
            if mw is None:
                sw = window.property('hyperspyUI.SignalWrapper')
                mw = sw.make_model()
            m = mw.model
            i = m.axis.value2index(x)
            h = m.spectrum()[i] - m()[i]
            if m.spectrum.metadata.Signal.binned:
                h /= m.axis.scale
            g = Gaussian2(height = h, centre = x)
            g.height.free = False
            g.centre.free = False
            mw.add_component(g)
            m.fit_component(g, signal_range=None, estimate_parameters=False)
            g.height.free = True
            g.centre.free = True
        else:
            self.dragging = True
            self.drag_data = [x, y, event.button, ax, event]
        
    def on_spanselect(self, x0, x1):
        self.span.disconnect_events()
        self.span = None
        ax = self.drag_data[3]
        window = ax.figure.canvas.parent()
        mw = window.property('hyperspyUI.ModelWrapper')
        if mw is None:
            sw = window.property('hyperspyUI.SignalWrapper')
            mw = sw.make_model()
        m = mw.model
        
        g = Gaussian2()
        mw.add_component(g)
        m.fit_component(g, signal_range=(x0, x1))
        i = m.axis.value2index(g.centre.value)
        g.active = False
        h = m.spectrum()[i] - m(onlyactive=True)[i]
        g.active = True
        if m.spectrum.metadata.Signal.binned:
            h /= m.axis.scale
        g.height.value = h
        g.height.free = False
        g.centre.free = False
        m.fit_component(g, signal_range=(x0, x1), estimate_parameters=False)
        g.height.free = True
        g.centre.free = True
        
        if self.drag_data is None:
            return
        self.drag_data = None
    
    def on_mousemove(self, event):
        if not self.dragging or self.drag_data is None:
            return
        
        ax = self.drag_data[3]
        if self.span is None:
            self.dragging = False
            self.span = SpanSelector(ax, self.on_spanselect, 'horizontal')
            event2 = self.drag_data[4]
            self.span.press(event2)
            self.span.onmove(event)
            
    def get_cursor(self):
        return self.cursor