# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Thu Jul 30 11:42:05 2015

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore
import numpy as np

from hyperspy.drawing.widgets import Line2DWidget, RangeWidget
from hyperspy.roi import BaseInteractiveROI, SpanROI, Line2DROI

from hyperspyui.log import logger
from hyperspyui._tools.signalfiguretool import SignalFigureTool
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
        super().__init__(windows)
        self.widget2d = Line2DWidget(None)
        self.widget2d.set_on(False)
        self.widget1d = RangeWidget(None)
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
        if not axes:
            logger.warning('Line tool only works on HyperSpy signal plots!')
            return
        # Make sure we have a figure with valid dimensions
        if len(axes) not in self.valid_dimensions:
            return
        self.axes = axes
        # If we already have a widget, make sure dragging is passed through
        if self.is_on():
            if any([p.contains(event)[0] is True for p in self.widget.patch]):
                return              # Interacting, handle in widget
            # Cancel previous and start new
            self.cancel()
            # Cancel reset axes, so set again
            self.axes = axes

        # Find out which axes of Signal are plotted in figure
        s = self._get_signal(event.inaxes.figure)
        if s is None:
            logger.warning('Line tool only works on HyperSpy signal plots!')
            return
        am = s.axes_manager

        self.widget.axes = axes
        if self.ndim > 1:
            self.widget.axes_manager = am

        # Have what we need, create widget
        x, y = event.xdata, event.ydata
        self.widget.set_mpl_ax(event.inaxes)  # connects
        new_widget = not self.is_on()
        if self.ndim == 1:
            self.widget.position = (x,)
            self.widget.size = np.array([0])
            self.widget.set_on(True)
            span = self.widget.span
            span.buttonDown = True
            span.on_move_cid = \
                span.canvas.mpl_connect('motion_notify_event',
                                        span.move_right)
        else:
            self.widget.position = np.array(((x, y), (x, y)))
            self.widget.size = np.array([0])
            self.widget.picked = True
            self.widget.func = Line2DWidget.FUNC_B | Line2DWidget.FUNC_RESIZE
            self.widget._drag_start = [x, y]
            self.widget._drag_store = (self.widget.position, self.widget.size)
            self.widget.set_on(True)
        if new_widget:
            self.widget.events.changed.connect(self._on_change,
                                               {'obj': 'widget'})

    def on_keyup(self, event):
        if event.key == 'enter':
            self.accept()
        elif event.key == 'escape':
            self.cancel()

    def _on_change(self, widget):
        if self.is_on():
            if self.ndim == 1:
                roi = SpanROI(0, 1)
            elif self.ndim == 1:
                roi = Line2DROI(0, 0, 1, 1, 1)
            else:
                raise RuntimeError(
                    f"Line tool doesn't support dimension dimension {self.ndim}."
                    )
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.updated[BaseInteractiveROI].emit(roi)
            self.updated[BaseInteractiveROI, SignalFigureTool].emit(roi, self)

    def accept(self):
        if self.is_on():
            if self.ndim == 1:
                roi = SpanROI(0, 1)
            elif self.ndim > 1:
                roi = Line2DROI(0, 0, 1, 1, 1)
            else:
                raise RuntimeError(
                    f"Line tool doesn't support dimension dimension {self.ndim}."
                    )
            roi._on_widget_change(self.widget)  # ROI gets coords from widget
            self.accepted[BaseInteractiveROI].emit(roi)
            self.accepted[BaseInteractiveROI, SignalFigureTool].emit(roi, self)

    def cancel(self):
        if self.widget.is_on():
            self.widget.set_on(False)
            self.widget.size = np.array([0])    # Prevents flickering
        if self._on_change in self.widget.events.changed.connected:
            self.widget.events.changed.disconnect(self._on_change)
        self.axes = None
        self.cancelled.emit()

    def disconnect_windows(self, windows):
        super().disconnect_windows(windows)
        self.cancel()
