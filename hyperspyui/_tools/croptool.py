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
import numpy as np

from hyperspy.drawing.widgets import ResizebleDraggableRectangle, \
                                     ModifiableSpanSelector

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
        
        self.widget = ResizebleDraggableRectangle(None)
        self.widget.set_on(False)
        self.spanner = None
        self.axes = None
        
    @property
    def ndim(self):
        if self.axes is None:
            return 0
        return len(self.axes)
        
    def is_on(self):
        if self.ndim == 1:
            return self.spanner is not None
        elif self.ndim > 1:
            return self.widget.is_on()
        return False
        
    def in_ax(self, ax):
        if self.ndim == 1:
            return self.spanner is not None and ax == self.spanner.ax
        else:
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
            if self.ndim == 1:
                if self.spanner.rect.contains(event)[0] == True:
                    return
            else:
                if self.widget.patch.contains(event)[0] == True:
                    return
                for r in self.widget.resizers:
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
        ndim = len(am.signal_axes) if sig_ax == event.inaxes else \
                                                    len(am.navigation_axes)
        if ndim > 1:
            am = am.deepcopy()  # Widget should have copy to not navigate
            
        if sig_ax == event.inaxes:
            axes = am.signal_axes
        elif nav_ax == event.inaxes:
            axes = am.navigation_axes
        else:
            return
        self.axes = axes
        if self.ndim > 1:
            self.widget.axes_manager = am

        x, y = event.xdata, event.ydata
        if self.ndim == 1:
            axes[0].value = x
            self.spanner = ModifiableSpanSelector(event.inaxes)
            self.spanner.press(event)
        elif self.ndim > 1:
            self.widget.xaxis, self.widget.yaxis = axes
            axes[0].value = x
            axes[1].value = y
            self.widget.add_axes(event.inaxes)  # connects
            self.widget.set_on(True)
            self.widget.set_size(1)
            self.pick_on_frame = 3
            self.widget.picked = True
        
    def on_keyup(self, event):
        if event.key == 'enter':
            self.crop(event)
        elif event.key == 'escape':
            self.cancel(event)
            
    def crop(self, event):
        if self.in_ax(event.inaxes):
            f = event.inaxes.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            s = sw.signal
            sw.keep_on_close = True
            if self.ndim == 1:
                axis = self.axes[0]
                idx = axis.value2index(np.array(self.spanner.range))
                slices = slice(*idx)
                new_offset = self.spanner.range[0]
                idx = s.axes_manager._axes.index(axis)
                s.data = s.data[ (slice(None),) * idx + (slices, Ellipsis)]
                axis.offset = new_offset
            elif self.ndim > 1:
                new_offsets = [ax.value for ax in self.axes]
                slices = self.widget.axes_manager._getitem_tuple_nav_sliced
                s.data = s.data[slices]
                for i, ax in enumerate(self.axes):
                    idx = self.widget.axes_manager._axes.index(ax)
                    s.axes_manager._axes[idx].offset = new_offsets[i]
            s.get_dimensions_from_data()
            s.squeeze()
            sw.update_figures()
            sw.keep_on_close = False
            self.cancel()   # Turn off functionality as we are finished
    
    def cancel(self, event=None):
        if event is None or self.in_ax(event.inaxes):
            if self.widget.is_on():
                self.widget.set_on(False)
                self.widget.set_size(1) # Prevents flickering
            if self.spanner is not None:
                self.spanner.turn_off()
                self.spanner = None
            self.axes = None
            
    def disconnect(self, windows):
        super(CropTool, self).disconnect(windows)
        self.cancel(None)