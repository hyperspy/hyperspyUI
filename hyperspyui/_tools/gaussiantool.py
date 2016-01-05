# -*- coding: utf-8 -*-
"""
Created on Sun Dec 07 10:30:08 2014

@author: Vidar Tonaas Fauske
"""

import os
import numpy as np
from matplotlib.widgets import SpanSelector

from hyperspy.components import Gaussian
try:
    from hyperspy.components import Gaussian2
    GaussTypes = (Gaussian, Gaussian2)
    has_gauss_v2 = True
except ImportError:
    GaussTypes = (Gaussian, )
    has_gauss_v2 = False

from .figuretool import FigureTool
from hyperspyui.util import crosshair_cursor


class GaussianTool(FigureTool):

    def __init__(self, windows=None):
        super(GaussianTool, self).__init__(windows)
        self.dragging = False
        self.drag_data = None
        self.span = None
        self._old_plot_comp = {}

    def get_name(self):
        return "Gaussian tool"

    def get_category(self):
        return 'Components'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/gaussian.svg'

    def is_selectable(self):
        return True

    def make_cursor(self):
        return crosshair_cursor()

    def _wire_wrapper(self, wrapper):
        if wrapper is None:
            return
        m = wrapper.model
        if m._plot.is_active():
            self._old_plot_comp[wrapper] = m._plot_components
            m.enable_plot_components()
            for c in m:
                if isinstance(c, GaussTypes):
                    c._model_plot_line.line.set_picker(True)

    def _unwire_wrapper(self, wrapper):
        if wrapper is None:
            return
        m = wrapper.model
        if wrapper in self._old_plot_comp:
            for c in m:
                if isinstance(c, GaussTypes):
                    c._model_plot_line.line.set_picker(False)
            if not self._old_plot_comp[wrapper]:
                m.disable_plot_components()

    def on_pick(self, event):
        if event.mouseevent.inaxes is None:
            return
        ax = event.mouseevent.inaxes
        if event.mouseevent.button == 3:
            window = ax.figure.canvas.parent()
            mw = window.property('hyperspyUI.ModelWrapper')
            if mw is not None:
                for c in mw.model:
                    line = c._model_plot_line.line
                    if event.artist == line and \
                            isinstance(c, GaussTypes):
                        mw.remove_component(c)

    def connect_windows(self, windows):
        super(GaussianTool, self).connect_windows(windows)
        windows = self._iter_windows(windows)
        for w in windows:
            mw = w.property('hyperspyUI.ModelWrapper')
            self._wire_wrapper(mw)

    def disconnect_windows(self, windows):
        super(GaussianTool, self).disconnect_windows(windows)
        windows = self._iter_windows(windows)
        for w in windows:
            mw = w.property('hyperspyUI.ModelWrapper')
            self._unwire_wrapper(mw)

    def on_mousedown(self, event):
        if event.inaxes is None:
            return
        ax = event.inaxes
        f = ax.figure
        x, y = event.xdata, event.ydata

        if event.button == 1 and event.dblclick:
            # Add Gaussian here!
            window = f.canvas.parent()
            mw = window.property('hyperspyUI.ModelWrapper')
            if mw is None:
                sw = window.property('hyperspyUI.SignalWrapper')
                mw = sw.make_model()
                self._wire_wrapper(mw)
            m = mw.model
            i = m.axis.value2index(x)
            h = m.spectrum()[i] - m()[i]
            if m.spectrum.metadata.Signal.binned:
                h /= m.axis.scale
            if has_gauss_v2:
                g = Gaussian2(height=h * np.sqrt(2 * np.pi), centre=x)
                g.height.free = False
            else:
                g = Gaussian(A=h, centre=x)
            g.centre.free = False
            mw.add_component(g)
            g._model_plot_line.line.set_picker(True)
            m.fit_component(g, signal_range=None, estimate_parameters=False)
            if has_gauss_v2:
                g.height.free = True
            g.centre.free = True
        else:
            self.dragging = True
            self.drag_data = [x, y, event.button, ax, event]

    def on_spanselect(self, x0, x1):
        self.span.disconnect_events()
        self.span = None
        ax = self.drag_data[3]
        window = ax.figure.canvas.parent()
        mw = window.property('hyperspyUI.ModelWrapper')
        if mw is None:
            sw = window.property('hyperspyUI.SignalWrapper')
            mw = sw.make_model()
            self._wire_wrapper(mw)
        m = mw.model

        if has_gauss_v2:
            g = Gaussian2()
        else:
            g = Gaussian()
        mw.add_component(g)
        g._model_plot_line.line.set_picker(True)
        m.fit_component(g, signal_range=(x0, x1))
        i = m.axis.value2index(g.centre.value)
        g.active = False
        h = m.spectrum()[i] - m(onlyactive=True)[i]
        g.active = True
        if m.spectrum.metadata.Signal.binned:
            h /= m.axis.scale
        if has_gauss_v2:
            g.height.value = h
            g.height.free = False
        else:
            g.A.value = h * np.sqrt(2 * np.pi)
        g.centre.free = False
        m.fit_component(g, signal_range=(x0, x1), estimate_parameters=False)
        if has_gauss_v2:
            g.height.free = True
        g.centre.free = True

        if self.drag_data is None:
            return
        self.drag_data = None

    def on_mousemove(self, event):
        if not self.dragging or self.drag_data is None:
            return

        ax = self.drag_data[3]
        if self.span is None:
            self.dragging = False
            invtrans = ax.transData.inverted()
            minspan = 3 * np.abs(invtrans.transform((1, 0)) -
                                 invtrans.transform((0, 0)))[0]
            self.span = SpanSelector(ax, self.on_spanselect, 'horizontal',
                                     minspan=minspan)
            event2 = self.drag_data[4]
            self.span.press(event2)
            self.span.onmove(event)
