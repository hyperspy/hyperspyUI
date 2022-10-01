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
Created on Mon Aug 03 19:43:52 2015

@author: Vidar Tonaas Fauske
"""
import copy

from qtpy import QtCore

import hyperspy.api as hs
from hyperspy.drawing.widgets import (
    RectangleWidget,
    RangeWidget,
    SquareWidget,
    VerticalLineWidget
    )
from hyperspy.roi import RectangularROI, SpanROI, Point1DROI, Point2DROI

from hyperspyui._tools.signalfiguretool import SignalFigureTool
from hyperspyui.util import crosshair_cursor


class MultiSelectionTool(SignalFigureTool):

    """
    Tool to select multiple ROIs on a  signal interactively. Simply click and
    drag in a figure to create an ROI. This can be done multiple times. Right-
    click the ROI to remove it. Press enter to indicate that the selection is
    complete, or ESC to cancel. The selection can also be aborted by simply
    selecting a different tool.
    """

    accepted = QtCore.Signal([hs.signals.BaseSignal, list],
                             [hs.signals.BaseSignal, list, SignalFigureTool])
    updated = QtCore.Signal([hs.signals.BaseSignal, list],
                            [hs.signals.BaseSignal, list, SignalFigureTool])
    cancelled = QtCore.Signal([hs.signals.BaseSignal])

    def __init__(self, windows=None):
        super().__init__(windows)
        self.widgets = {}
        self.axes = {}
        self.valid_dimensions = [1, 2]
        self.ranged = True
        self.name = "Multi-selection tool"
        self.category = 'Signal'
        self.icon = None
        self.validator = self._default_validator

    def ndim(self, signal):
        if self.axes is None or signal is None or signal not in self.axes:
            return 0
        return len(self.axes[signal])

    def get_name(self):
        return self.name

    def get_category(self):
        return self.category

    def make_cursor(self):
        return crosshair_cursor()

    def get_icon(self):
        return self.icon

    def is_selectable(self):
        return True

    def _add_widget(self, signal):
        if signal is None:
            return None
        if self.ndim(signal) == 1:
            if self.ranged:
                w = RangeWidget(None)
            else:
                w = VerticalLineWidget(None)
        else:
            if self.ranged:
                w = RectangleWidget(None)
            else:
                w = SquareWidget(None)
        if signal in self.widgets:
            self.widgets[signal].append(w)
        else:
            self.widgets[signal] = [w]
        w.set_on(False)
        return w

    def _remove_widget(self, widget, signal=None):
        if widget.is_on():
            widget.set_on(False)
        if signal is None:
            for widgets in self.widgets.values():
                if widget in widgets:
                    widgets.remove(widget)
        else:
            self.widgets[signal].remove(widget)

    def have_selection(self, signal):
        if signal is None:
            return False
        if signal not in self.widgets:
            return False
        for w in self.widgets[signal]:
            if w.is_on():
                return True
        return False

    def on_keyup(self, event):
        if event.inaxes is None:
            s = None
        else:
            s = self._get_signal(event.inaxes.figure)
        if event.key == 'enter':
            self.accept(s)
        elif event.key == 'escape':
            self.cancel(s)

    def on_mouseup(self, event):
        # Only accept mouse up inside axes
        if event.inaxes is None:
            return

        if event.button != 3:
            # Don't handle anything except right click up events.
            return

        s = self._get_signal(event.inaxes.figure)
        for w in self.widgets[s]:
            if any([p.contains(event)[0] == True for p in w.patch]):
                self._remove_widget(w, s)
                self._on_change(w, s)

    def _default_validator(self, signal, axes):
        # Validate signal
        if signal is None:
            return False

        # Make sure we have a figure with valid dimensions
        return len(axes) in self.valid_dimensions

    def on_mousedown(self, event):
        # Only accept mouse down inside axes
        if event.inaxes is None:
            return

        if event.button == 3:
            # Don't handle right click down events.
            return

        # Find out which axes of Signal are plotted in figure
        s = self._get_signal(event.inaxes.figure)
        axes = self._get_axes(event)
        if not self.validator(s, axes):
            return

        self.axes[s] = axes

        # If we already have widgets, make sure editing is passed through
        if self.have_selection(s):
            for w in self.widgets[s]:
                if any([p.contains(event)[0] == True for p in w.patch]):
                    return              # Moving, handle in widget
            # Clicked outside existing widget, check for resize handles
            if self.ndim(s) > 1:
                for w in self.widgets[s]:
                    if w.resizers:
                        for r in w._resizer_handles:
                            if r.contains(event)[0] == True:
                                return      # Leave the event to widget
        am = s.axes_manager

        # Start a new widget
        widget = self._add_widget(s)
        widget.axes = axes
        if self.ndim(s) > 1:
            widget.axes_manager = am

        # Have what we need, create widget
        x, y = event.xdata, event.ydata
        widget.axes = axes
        widget.set_mpl_ax(event.inaxes)  # connects
        if self.ndim(s) == 1:
            widget.position = (x,)
            widget.size = axes[0].scale
            widget.set_on(True)
            if self.ranged:
                span = widget.span
                span.buttonDown = True
                span.on_move_cid = \
                    span.canvas.mpl_connect('motion_notify_event',
                                            span.move_right)
            else:
                widget.picked = True
        else:
            widget.position = (x, y)
            widget.size = [ax.scale for ax in axes]
            widget.set_on(True)
            if self.ranged:
                widget.resizer_picked = 3
            widget.picked = True
        widget.events.changed.connect(self._on_change, {'obj': 'widget'})

    def _get_rois(self, signal):
        rois = []
        if self.have_selection(signal):
            if self.ndim(signal) == 1:
                if self.ranged:
                    roi_template = SpanROI(0, 1)
                else:
                    roi_template = Point1DROI(0)
            elif self.ndim(signal) > 1:
                if self.ranged:
                    roi_template = RectangularROI(0, 0, 1, 1)
                else:
                    roi_template = Point2DROI(0, 0)
            for w in self.widgets[signal]:
                roi = copy.deepcopy(roi_template)
                # ROI gets coords from widget:
                roi._on_widget_change(w)
                rois.append(roi)
        return rois

    def _on_change(self, widget, signal=None):
        if signal is None:
            for s, widgets in self.widgets.items():
                if widget in widgets:
                    signal = s
                    break
        if signal is None:
            return

        rois = self._get_rois(signal)
        self.updated[hs.signals.BaseSignal, list].emit(signal, rois)
        self.updated[hs.signals.BaseSignal, list, SignalFigureTool].emit(
            signal, rois, self)

    def _cancel(self, signal):
        for w in self.widgets[signal]:
            if w.is_on():
                w.set_on(False)
        self.widgets.pop(signal)
        self.axes.pop(signal)

    def accept(self, signal):
        if self.have_selection(signal):
            rois = self._get_rois(signal)
            self.accepted[hs.signals.BaseSignal, list].emit(signal, rois)
            self.accepted[hs.signals.BaseSignal, list, SignalFigureTool].emit(
                signal, rois, self)
        if signal is not None:
            self.cancel(signal)

    def cancel(self, signal=None):
        if signal is None:
            signals = list(self.widgets.keys())
        else:
            signals = [signal]
        for s in signals:
            if s in self.widgets:
                self._cancel(s)
                self.cancelled[hs.signals.BaseSignal].emit(s)

    def disconnect_windows(self, windows):
        super().disconnect_windows(windows)
        self.cancel()
