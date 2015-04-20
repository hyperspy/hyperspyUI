# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 00:03:50 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtCore
import os

from hyperspy.drawing.widgets import ResizableDraggableRectangle, \
    DraggableResizableRange
from hyperspy.roi import BaseInteractiveROI, RectangularROI, SpanROI

from hyperspyui.tools import FigureTool
from hyperspyui.util import load_cursor


class SelectionTool(FigureTool):

    """
    Tool to select a ROI on a  signal interactively. Simply click and drag in a
    figure to create an ROI, and then press enter to indicate that the
    selection is complete, or ESC to cancel. The selection can also be aborted
    by simply selecting a different tool.
    """

    accepted = QtCore.Signal([BaseInteractiveROI],
                             [BaseInteractiveROI, FigureTool])
    updated = QtCore.Signal([BaseInteractiveROI],
                            [BaseInteractiveROI, FigureTool])    # TODO: Use
    cancelled = QtCore.Signal()

    def __init__(self, windows=None):
        super(SelectionTool, self).__init__(windows)
        self.widget2d = ResizableDraggableRectangle(None)
        self.widget2d.set_on(False)
        self.widget1d = DraggableResizableRange(None)
        self.widget1d.set_on(False)
        self.axes = None
        self.valid_dimensions = [1, 2]

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
        return "Selection tool"

    def get_category(self):
        return 'Signal'

    def make_cursor(self):
        return load_cursor(os.path.dirname(__file__) +
                           '/../images/picker.svg', 8, 8)

    def is_selectable(self):
        return True

    def on_mousedown(self, event):
        # Only accept mouse down inside axes
        if event.inaxes is None:
            return
        # If we already have a widget, make sure dragging is passed through
        if self.is_on():
            if self.widget.patch.contains(event)[0] == True:
                return              # Moving, handle in widget
            # Clicked outside existing widget, check for resize handles
            if self.ndim > 1 and self.widget.resizers:
                for r in self.widget._resizer_handles:
                    if r.contains(event)[0] == True:
                        return      # Leave the event to widget
            # Cancel previous and start new
            self.cancel()

        # We need to map figure to a hyperspy Signal:
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

        # Find out which axes of Signal are plotted in figure
        am = sw.signal.axes_manager
        if sig_ax == event.inaxes:
            axes = am.signal_axes
        elif nav_ax == event.inaxes:
            axes = am.navigation_axes
        else:
            return
        # Make sure we have a figure with valid dimensions
        if len(axes) not in self.valid_dimensions:
            return
        self.axes = axes
        self.widget.axes = axes
        if self.ndim > 1:
            self.widget.axes_manager = am

        # Have what we need, create widget
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
            self.widget.coordinates = (x, y)
            self.widget.size = (1, 1)
            self.widget.pick_on_frame = 3
            self.widget.picked = True

    def on_keyup(self, event):
        if event.key == 'enter':
            self.accept()
        elif event.key == 'escape':
            self.cancel()

    def accept(self):
        if self.is_on():
            if self.ndim == 1:
                roi = SpanROI(0, 1)
            elif self.ndim > 1:
                roi = RectangularROI(0, 0, 1, 1)
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.accepted[BaseInteractiveROI].emit(roi)
            self.accepted[BaseInteractiveROI, FigureTool].emit(roi, self)

    def cancel(self):
        if self.widget.is_on():
            self.widget.set_on(False)
            self.widget.size = 1    # Prevents flickering
        self.axes = None
        self.cancelled.emit()

    def disconnect(self, windows):
        super(SelectionTool, self).disconnect(windows)
        self.cancel()
