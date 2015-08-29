# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 11:42:05 2015

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtCore
import os
import numpy as np

from hyperspy.drawing.widgets import DraggableResizable2DLine, \
                                     DraggableResizableRange
from hyperspy.roi import BaseInteractiveROI, SpanROI, Line2DROI

from hyperspyui.tools import SignalFigureTool
from hyperspyui.util import crosshair_cursor


class LineTool(SignalFigureTool):

    """
    Tool to select a ROI on a  signal interactively. Simply click and drag in a
    figure to create an ROI, and then press enter to indicate that the
    selection is complete, or ESC to cancel. The selection can also be aborted
    by simply selecting a different tool.
    """

    accepted = QtCore.Signal([BaseInteractiveROI],
                             [BaseInteractiveROI, SignalFigureTool])
    updated = QtCore.Signal([BaseInteractiveROI],
                            [BaseInteractiveROI, SignalFigureTool])
    cancelled = QtCore.Signal()

    def __init__(self, windows=None):
        super(LineTool, self).__init__(windows)
        self.widget2d = DraggableResizable2DLine(None)
        self.widget2d.set_on(False)
        self.widget1d = DraggableResizableRange(None)
        self.widget1d.set_on(False)
        self.valid_dimensions = [1, 2]
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
        return "Line tool"

    def get_category(self):
        return 'Signal'

    def make_cursor(self):
        return crosshair_cursor()

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
#            # Clicked outside existing widget, check for resize handles
#            if self.ndim > 1 and self.widget.resizers:
#                for r in self.widget._resizer_handles:
#                    if r.contains(event)[0] == True:
#                        return      # Leave the event to widget
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
        new_widget = not self.is_on()
        if self.ndim == 1:
            self.widget.coordinates = (x,)
            self.widget.size = 0
            self.widget.set_on(True)
            if self.ranged:
                span = self.widget.span
                span.buttonDown = True
                span.on_move_cid = \
                    span.canvas.mpl_connect('motion_notify_event',
                                            span.move_right)
            else:
                self.widget.picked = True
        else:
            self.widget.coordinates = np.array(((x, y), (x, y)))
            self.widget.size = 1
            self.widget.set_on(True)
            self.widget.picked = True
            self.widget.func = self.widget._get_func_from_pos(event.x, event.y)
            self.widget._prev_pos = [x, y]
            if self.widget.func & self.widget.FUNC_ROTATE:
                self.widget._rotate_orig = self.widget.coordinates
        if new_widget:
            self.widget.events.changed.connect(self._on_change, 1)

    def on_keyup(self, event):
        if event.key == 'enter':
            self.accept()
        elif event.key == 'escape':
            self.cancel()

    def _on_change(self, widget):
        if self.is_on():
            if self.ndim == 1:
                roi = SpanROI(0, 1)
            elif self.ndim > 1:
                roi = Line2DROI(0, 0, 1, 1, 1)
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.updated[BaseInteractiveROI].emit(roi)
            self.updated[BaseInteractiveROI, SignalFigureTool].emit(roi, self)

    def accept(self):
        if self.is_on():
            if self.ndim == 1:
                roi = SpanROI(0, 1)
            elif self.ndim > 1:
                roi = Line2DROI(0, 0, 1, 1, 1)
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.accepted[BaseInteractiveROI].emit(roi)
            self.accepted[BaseInteractiveROI, SignalFigureTool].emit(roi, self)

    def cancel(self):
        if self.widget.is_on():
            self.widget.set_on(False)
            self.widget.size = 1    # Prevents flickering
        self.widget.events.changed.disconnect(self._on_change)
        self.axes = None
        self.cancelled.emit()

    def disconnect_windows(self, windows):
        super(LineTool, self).disconnect_windows(windows)
        self.cancel()
