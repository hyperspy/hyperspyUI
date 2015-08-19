# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 00:03:50 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtCore
import os

from hyperspy.drawing.widgets import ResizableDraggableRectangle, \
    DraggableResizableRange, DraggableSquare, DraggableVerticalLine
from hyperspy.roi import BaseInteractiveROI, RectangularROI, SpanROI, \
    Point1DROI, Point2DROI

from hyperspyui.tools import SignalFigureTool
from hyperspyui.util import load_cursor


class SelectionTool(SignalFigureTool):

    """
    Tool to select a ROI on a  signal interactively. Simply click and drag in a
    figure to create an ROI, and then press enter to indicate that the
    selection is complete, or ESC to cancel. The selection can also be aborted
    by simply selecting a different tool.
    """

    accepted = QtCore.Signal([BaseInteractiveROI],
                             [BaseInteractiveROI, SignalFigureTool])
    updated = QtCore.Signal([BaseInteractiveROI],
                            [BaseInteractiveROI, SignalFigureTool]) # TODO: Use
    cancelled = QtCore.Signal()

    def __init__(self, windows=None, name=None, category=None, icon=None,
                 description=None):
        super(SelectionTool, self).__init__(windows)
        self.widget2d_r = ResizableDraggableRectangle(None)
        self.widget2d_r.set_on(False)
        self.widget1d_r = DraggableResizableRange(None)
        self.widget1d_r.set_on(False)
        self.widget2d = DraggableSquare(None)
        self.widget2d.set_on(False)
        self.widget1d = DraggableVerticalLine(None)
        self.widget1d.set_on(False)
        self._widgets = [self.widget2d_r, self.widget1d_r, self.widget2d,
                         self.widget1d]
        self.valid_dimensions = [1, 2]
        self.ranged = True

        self.name = name or "Selection tool"
        self.category = category or 'Signal'
        self.description = description
        self.icon = icon
        self.cancel_on_accept = False

    @property
    def widget(self):
        if self.ndim == 1:
            if self.ranged:
                return self.widget1d_r
            else:
                return self.widget1d
        else:
            if self.ranged:
                return self.widget2d_r
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
        return self.name

    def get_category(self):
        return self.category

    def get_icon(self):
        return self.icon

    def make_cursor(self):
        return load_cursor(os.path.dirname(__file__) +
                           '/../images/picker.svg', 8, 8)

    def is_selectable(self):
        return True

    def on_mousedown(self, event):
        # Only accept mouse down inside axes
        if event.inaxes is None:
            return

        axes = self._get_axes(event)
        # Make sure we have a figure with valid dimensions
        if len(axes) not in self.valid_dimensions:
            return
        self.axes = axes
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

        # Find out which axes of Signal are plotted in figure
        s = self._get_signal(event.inaxes.figure)
        if s is None:
            return
        am = s.axes_manager

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
            if self.ranged:
                span = self.widget.span
                span.buttonDown = True
                span.on_move_cid = \
                    span.canvas.mpl_connect('motion_notify_event',
                                            span.move_right)
            else:
                self.widget.picked = True
        else:
            self.widget.coordinates = (x, y)
            self.widget.size = (1, 1)
            if self.ranged:
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
                if self.ranged:
                    roi = SpanROI(0, 1)
                else:
                    roi = Point1DROI(0)
            elif self.ndim > 1:
                if self.ranged:
                    roi = RectangularROI(0, 0, 1, 1)
                else:
                    roi = Point2DROI(0, 0)
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.accepted[BaseInteractiveROI].emit(roi)
            self.accepted[BaseInteractiveROI, SignalFigureTool].emit(roi, self)
        if self.cancel_on_accept:
            self.cancel()

    def cancel(self):
        for w in self._widgets:
            if w.is_on():
                w.set_on(False)
                w.size = 1    # Prevents flickering
        self.axes = None
        self.cancelled.emit()

    def disconnect_windows(self, windows):
        super(SelectionTool, self).disconnect_windows(windows)
        self.cancel()
