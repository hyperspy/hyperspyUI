# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 02:03:23 2014

@author: vroot
"""

import os
import collections

from figuretool import FigureTool
from util import load_cursor

class ZoomPanTool(FigureTool):
    def __init__(self, windows=None):
        super(ZoomPanTool, self).__init__(windows)
        self.panning = False
        self.pan_data = None
        self.cursor = load_cursor(os.path.dirname(__file__) + \
                                  '/../../images/panzoom2.svg', 16, 16)
        
    def get_name(self):
        return "Pan/Zoom tool"
        
    def get_category(self):
        return 'Navigation'
        
    def get_icon(self):
        return os.path.dirname(__file__) + '/../../images/panzoom2.svg'
        
    def is_selectable(self):
        return True
        
    def on_mousedown(self, event):
        if event.inaxes is None:
            return
        f = event.inaxes.figure
        x, y = event.x, event.y
        axes = []
        for a in f.get_axes():
            if (x is not None and y is not None and a.in_axes(event) and
                    a.can_pan()):
                a.start_pan(x, y, event.button)
                axes.append(a)
        if len(axes) > 0:
            self.panning = True
            self.pan_data = [x, y, event.button, axes]
    
    def on_mouseup(self, event):
        if not self.panning:
            return
        self.panning = False
        if self.pan_data is None:
            return
        for a in self.pan_data[3]:
            a.end_pan()
            a.figure.canvas.draw_idle()
        self.pan_data = None
    
    def on_mousemove(self, event):
        if not self.panning or self.pan_data is None:
            return
            
        x0, y0 = self.pan_data[0:2]
        x1, y1 = self.pan_data[0:2] = (event.x, event.y)
        dx, dy = x1-x0, y1-y0
        
        cs = set()
        for a in self.pan_data[3]:
            #safer to use the recorded button at the press than current button:
            #multiple button can get pressed during motion...
            a.drag_pan(self.pan_data[2], event.key, event.x, event.y)
            cs.add(a.figure.canvas)
        for canvas in cs:
            canvas.draw()
            
    def connect(self, windows):
        super(ZoomPanTool, self).connect(windows)
        if windows is None:
            return
        if not isinstance(windows, collections.Iterable):
            windows = (windows,)
        canvases = set()
        for w in windows:
            canvases.add(w.widget())
        for c in canvases:
            print c.widgetlock._owner
            c.widgetlock(self)
            print c.widgetlock._owner
            
    def disconnect(self, windows):
        super(ZoomPanTool, self).disconnect(windows)
        if windows is None:
            return
        if not isinstance(windows, collections.Iterable):
            windows = (windows,)
        canvases = set()
        for w in windows:
            canvases.add(w.widget())
        for c in canvases:
            print c.widgetlock._owner
            c.widgetlock.release(self)
            print c.widgetlock._owner
            
    def on_scroll(self, event):
        pass
            
    def get_cursor(self):
        return self.cursor