# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:52:37 2014

@author: vidarton
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 02:03:23 2014

@author: Vidar Tonaas Fauske
"""

import os

from hyperspy.drawing.widgets import ResizebleDraggableRectangle

from figuretool import FigureTool
from util import load_cursor

class CropTool(FigureTool):
    def __init__(self, windows=None):
        super(CropTool, self).__init__(windows)
        
        self.widget = ResizebleDraggableRectangle(None)
        
    def get_name(self):
        return "Crop tool"
        
    def get_category(self):
        return 'Signal'
        
    def get_icon(self):
        return os.path.dirname(__file__) + '/../../images/crop.svg'
        
    def is_selectable(self):
        return True
            
    def make_cursor(self):
        return load_cursor(os.path.dirname(__file__) + \
                                  '/../../images/crop.svg', 8, 8)
        
    def on_mousedown(self, event):
        if event.inaxes is None:
            return
        f = event.inaxes.figure
        window = f.canvas.parent()
        sw = window.property('hyperspyUI.SignalWrapper')
        if sw is None:
            return
        if sw.signal._plot.signal_plot is not None:
            sig_ax = sw.signal._plot.signal_plot.ax
        else:
            sig_ax = None
        if sw.signal._plot.navigator_plot is not None:
            nav_ax = sw.signal._plot.navigator_plot.ax
        else:
            nav_ax = None
            
        if sig_ax == event.inaxes:
            axes = sw.signal.axes_manager.signal_axes
        elif nav_ax == event.inaxes:
            axes = sw.signal.axes_manager.navigator_axes
        else:
            return
        
        x, y = event.xdata, event.ydata
        self.widget.axes_manager = sw.signal.axes_manager
        self.widget.xaxis, self.widget.yaxis = axes
        self.widget.add_axes(event.inaxes)  # connects
        axes[0].value = x
        axes[1].value = y
        self.widget.set_size(1)
        self.widget.set_on(True)
        self.pick_on_frame = 3
        self.widget.picked = True
        
    def on_keyup(self, event):
        if event.key == 'enter':
            self.crop(event)
        elif event.key == 'escape':
            self.cancel(event)
            
    def crop(self, event):
        if event.inaxes == self.widget.ax:
            f = event.inaxes.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            s = sw.signal
            sw.keep_on_close = True
            for axis in self.widget.axes_manager.signal_axes:
                if isinstance(axis.slice, slice):
                    start = axis.slice[0]
                    end = axis.slice[1]
                else:
                    start = axis.index
                    end = axis.index + 1
                s.crop(axis, start=start, end=end)
    
    def cancel(self, event):
        if event is None or event.inaxes == self.widget.ax:
            self.widget.set_on(False)
            
    def disconnect(self, windows):
        super(CropTool, self).disconnect(windows)
        self.cancel(None)