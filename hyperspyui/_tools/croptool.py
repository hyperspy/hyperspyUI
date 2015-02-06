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

from hyperspy.drawing.widgets import ResizableDraggableRectangle, \
                                     DraggableResizableRange
from hyperspy.roi import RectangularROI, SpanROI

from figuretool import FigureTool
from util import load_cursor

class CropTool(FigureTool):
    """
    Tool to crop signal interactively. Simply click and drag in a figure to
    create an ROI, and then press enter to apply cropping operation, or ESC to
    abort cropping. The cropping can also be aborted simply by selecting a 
    different tool.
    """
    
    def __init__(self, windows=None):
        super(CropTool, self).__init__(windows)
        self.widget2d = ResizableDraggableRectangle(None)
        self.widget2d.set_on(False)
        self.widget1d = DraggableResizableRange(None)
        self.widget1d.set_on(False)
        self.axes = None
    
    @property
    def widget(self):
        if self.ndim == 1:
            return self.widget1d
        else:
            return self.widget2d
        
    @property
    def ndim(self):
        if self.axes is None:
            return 0
        return len(self.axes)

    def is_on(self):
        return self.widget.is_on()
        
    def in_ax(self, ax):
        return ax == self.widget.ax
        
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
        if self.is_on():
            if self.widget.patch.contains(event)[0] == True:
                return
            if self.ndim > 1 and self.widget.resizers:
                for r in self.widget._resizer_handles:
                    if r.contains(event)[0] == True:
                        return      # Leave the event to resizer pick
            self.cancel()   # Cancel previous and start new
        
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
        
        am = sw.signal.axes_manager
        if sig_ax == event.inaxes:
            axes = am.signal_axes
        elif nav_ax == event.inaxes:
            axes = am.navigation_axes
        else:
            return
        self.axes = axes
        self.widget.axes = axes
        if self.ndim > 1:
            self.widget.axes_manager = am

        x, y = event.xdata, event.ydata
        self.widget.axes = axes
        self.widget.set_mpl_ax(event.inaxes)  # connects
        self.widget.set_on(True)
        if self.ndim == 1:
            self.widget.coordinates = (x,)
            self.widget.size = 1
            span = self.widget.span
            span.buttonDown = True
            span.on_move_cid = \
                span.canvas.mpl_connect('motion_notify_event', span.move_right)
        else:
            self.widget.coordinates = (x,y)
            self.widget.size = (1,1)
            self.widget.pick_on_frame = 3
            self.widget.picked = True
        
    def on_keyup(self, event):
        if event.key == 'enter':
            self.crop(event)
        elif event.key == 'escape':
            self.cancel(event)
            
    def crop(self, event):
        if self.is_on() and self.in_ax(event.inaxes):
            f = event.inaxes.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            s = sw.signal
            if self.ndim == 1:
                roi = SpanROI(0,1)
            elif self.ndim > 1:
                roi = RectangularROI(0,0,1,1)
            roi._on_widget_change(self.widget)
            axes = s.axes_manager._axes
            slices = roi._make_slices(axes, self.axes)
            new_offsets = self.widget.coordinates
            s.data = s.data[slices]
            for i, ax in enumerate(self.axes):
                s.axes_manager[ax.name].offset = new_offsets[i]
            s.get_dimensions_from_data()
            s.squeeze()
            self.cancel()   # Turn off functionality as we are finished
    
    def cancel(self, event=None):
        if event is None or self.in_ax(event.inaxes):
            if self.widget.is_on():
                self.widget.set_on(False)
                self.widget.size = 1    # Prevents flickering
            self.axes = None
            
    def disconnect(self, windows):
        super(CropTool, self).disconnect(windows)
        self.cancel(None)