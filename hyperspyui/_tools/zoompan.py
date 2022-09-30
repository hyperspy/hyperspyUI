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
Created on Sun Dec 07 02:03:23 2014

@author: Vidar Tonaas Fauske
"""

import os

from .figuretool import FigureTool
from hyperspyui.util import load_cursor


class ZoomPanTool(FigureTool):

    def __init__(self, windows=None):
        super().__init__(windows)
        self.panning = False
        self.pan_data = None
        self.base_scale = 1.5     # Mouse wheel zoom factor

    def get_name(self):
        return "Pan/Zoom tool"

    def get_category(self):
        return 'Plot'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/panzoom2.svg'

    def is_selectable(self):
        return True

    def make_cursor(self):
        return load_cursor(os.path.dirname(__file__) +
                           '/../images/panzoom2.svg', 8, 8)

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

        self.pan_data[0:2] = (event.x, event.y)

        cs = set()
        for a in self.pan_data[3]:
            # safer to use the recorded button at the press than current button
            # as multiple buttons can get pressed during motion...
            a.drag_pan(self.pan_data[2], event.key, event.x, event.y)
            cs.add(a.figure.canvas)
        for canvas in cs:
            canvas.draw()

    def connect_windows(self, windows):
        super().connect_windows(windows)
        windows = self._iter_windows(windows)
        canvases = set()
        for w in windows:
            canvases.add(w.widget())
        for c in canvases:
            c.widgetlock(self)

    def disconnect_windows(self, windows):
        super().disconnect_windows(windows)
        windows = self._iter_windows(windows)
        canvases = set()
        for w in windows:
            canvases.add(w.widget())
        for c in canvases:
            c.widgetlock.release(self)

    def on_scroll(self, event):
        if event.inaxes is None:
            return
        ax = event.inaxes
        # get the current x and y limits
        cxlim = ax.get_xlim()
        cylim = ax.get_ylim()
        cx = (cxlim[1] - cxlim[0]) * .5
        cy = (cylim[1] - cylim[0]) * .5
        x = event.xdata  # get event x location
        y = event.ydata  # get event y location
        center = ((cxlim[1] + cxlim[0]) * .5, (cylim[1] + cylim[0]) * .5)
        zoom_vector = (
            (x - center[0]) / self.base_scale,
            (y - center[1]) / self.base_scale)
        if event.button == 'up':
            # deal with zoom in
            scale = 1.0 / self.base_scale
            new_centre = (
                center[0] + zoom_vector[0], center[1] + zoom_vector[1])
            new_xlim = [new_centre[0] - cx * scale,
                        new_centre[0] + cx * scale]
            new_ylim = [new_centre[1] - cy * scale,
                        new_centre[1] + cy * scale]
        elif event.button == 'down':
            # deal with zoom out
            scale = self.base_scale
            new_centre = (
                center[0] - zoom_vector[0], center[1] - zoom_vector[1])
            new_xlim = [new_centre[0] - cx * scale,
                        new_centre[0] + cx * scale]
            new_ylim = [new_centre[1] - cy * scale,
                        new_centre[1] + cy * scale]
        else:
            return
        # set new limits
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        ax.figure.canvas.draw_idle()
