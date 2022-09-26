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
Created on Fri Oct 24 18:27:15 2014

@author: Vidar Tonaas Fauske
"""

from .util import fig2win
from qtpy import QtCore

from .modelwrapper import ModelWrapper
from .actionable import Actionable


class SignalWrapper(Actionable):
    closing = QtCore.Signal()
    model_added = QtCore.Signal(object)
    model_removed = QtCore.Signal(object)

    _untitled_counter = 0

    def __init__(self, signal, mainwindow, name=None):
        super().__init__()
        self.signal = signal
        # Override replot on Signal instance
        self._old_replot = signal._replot
        signal._replot = self._replot
        if name is None:
            if signal.metadata.General.title:
                name = signal.metadata.General.title
            elif signal.tmp_parameters.has_item('filename'):
                name = signal.tmp_parameters.filename
            else:
                name = "Untitled %d" % SignalWrapper._untitled_counter
                SignalWrapper._untitled_counter += 1
        self.name = name
        self.figures = []
        self.mainwindow = mainwindow
        self.models = []

        self._keep_on_close = 0
        self._magic_jump = (8, 30)

        self.navigator_plot = None
        self.signal_plot = None

        self._nav_geom = None
        self._sig_geom = None
        self._replotargs = ((), {})

        self._model_id = 1

        self.add_action('plot', "&Plot", self.replot)
        self.add_action('add_model', "Add &model", self.make_model)
        self.add_separator()
        self.add_action('close', "&Close", self.close)

    @property
    def keep_on_close(self):
        return self._keep_on_close > 0

    @keep_on_close.setter
    def keep_on_close(self, value):
        if value:
            self._keep_on_close += 1
        else:
            if self._keep_on_close > 0:
                self._keep_on_close -= 1

    def plot(self, *args, **kwargs):
        self.keep_on_close = True
        self.signal.plot(*args, **kwargs)
        self.keep_on_close = False
        self.update_figures()
        self._replotargs = (args, kwargs)
        self.mainwindow.main_frame.subWindowActivated.emit(
            self.mainwindow.main_frame.activeSubWindow())
        # Redraw plot needed for pyqt5
        if self.signal._plot and self.signal._plot.signal_plot:
            self.signal._plot.signal_plot.figure.canvas.draw_idle()

    def _replot(self):
        if self.signal._plot is not None:
            if self.signal._plot.is_active:
                self.replot()

    def replot(self):
        old = self.mainwindow.updatesEnabled()
        self.mainwindow.setUpdatesEnabled(False)
        try:
            self.plot(*self._replotargs[0], **self._replotargs[1])
        finally:
            self.mainwindow.setUpdatesEnabled(old)

    def switch_signal(self, new_signal):
        """
        Switch the signal wrapped by this wrapper. To complete the switch, the
        signal should also be replotted if previously plotted. For performance
        reasons this is left as the responsibility of the caller.
        """
        old_signal = self.signal
        self.signal = new_signal
        idx = -1
        for i, s in enumerate(self.mainwindow.hspy_signals):
            if s is old_signal:
                idx = i
                break
        self.mainwindow.lut_signalwrapper[new_signal] = self
        del self.mainwindow.lut_signalwrapper[old_signal]
        if idx >= 0:
            self.mainwindow.hspy_signals[idx] = new_signal

    def update(self):
        if self.navigator_plot is not None:
            self.navigator_plot.update()
        if self.signal_plot is not None:
            self.signal_plot.update()

    def update_figures(self):
        old_nav = self.navigator_plot
        old_sig = self.signal_plot
        self.remove_figure(old_nav)
        self.remove_figure(old_sig)
        self.navigator_plot = None
        self.signal_plot = None

        atleast_one_changed = False

        # If we have a navigator plot
        if self.signal._plot and self.signal._plot.navigator_plot:
            # Set internal `navigator_plot` to window containing it
            navi = self.signal._plot.navigator_plot.figure
            self.navigator_plot = fig2win(navi, self.mainwindow.figures)
            # Did the window change?
            if old_nav is not self.navigator_plot:
                # Process the plot
                title = navi.axes[0].set_title("")  # remove title
                title.set_visible(False)
                # Wire closing event
                self.navigator_plot.closing.connect(self.nav_closing)
                # Set a reference on window to self
                self.navigator_plot.setProperty('hyperspyUI.SignalWrapper',
                                                self)
                # Add to figures list
                self.add_figure(self.navigator_plot)

                # Did we have a previous window?
                if old_nav is not None:
                    navi.tight_layout()
                    # Save geometry of old, and make sure it is closed
                    self._nav_geom = old_nav.saveGeometry()
                    old_nav.closing.disconnect(self.nav_closing)
                    old_nav.close()
                    atleast_one_changed = True
                # If we have stored geometry, and a valid plot, restore
                if self._nav_geom is not None and self.navigator_plot is not None:
                    self.navigator_plot.restoreGeometry(self._nav_geom)
                self._nav_geom = None

        if self.signal._plot and self.signal._plot.signal_plot is not None:
            sigp = self.signal._plot.signal_plot.figure
            self.signal_plot = fig2win(sigp, self.mainwindow.figures)
            if old_sig is not self.signal_plot:
                title = sigp.axes[0].set_title("")
                title.set_visible(False)
                self.signal_plot.closing.connect(self.sig_closing)
                self.signal_plot.setProperty('hyperspyUI.SignalWrapper', self)
                self.add_figure(self.signal_plot)
                if old_sig is not None:
                    sigp.tight_layout()
                    self._sig_geom = old_sig.saveGeometry()
                    old_sig.closing.disconnect(self.sig_closing)
                    old_sig.close()
                    atleast_one_changed = True
                if self._sig_geom is not None and self.signal_plot is not None:
                    self.signal_plot.restoreGeometry(self._sig_geom)
                self._sig_geom = None

        if atleast_one_changed:
            self.mainwindow.check_action_selections()

    def add_figure(self, fig):
        self.figures.append(fig)

    def remove_figure(self, fig):
        if fig in self.figures:
            self.figures.remove(fig)

    def as_signal2D(self, axis=(0, 1)):
        signal = self.signal
        self.close()  # Store geomtery and close
        # Swap geometries
        tmp = self._sig_geom
        self._sig_geom = self._nav_geom
        self._nav_geom = tmp
        self.signal = signal.as_signal2D(axis)

    def as_signal1D(self, axis=0):
        signal = self.signal
        self.close()  # Store geomtery and close
        # Swap geometries
        tmp = self._sig_geom
        self._sig_geom = self._nav_geom
        self._nav_geom = tmp
        self.signal = signal.as_signal1D(axis)

    def make_model(self, *args, **kwargs):
        m = self.signal.create_model(*args, **kwargs)
        self.mainwindow.record_code("signal = ui.get_selected_signal()")
        self.mainwindow.record_code("model = signal.create_model()")
#        modelname = self.signal.metadata.General.title
        modelname = "Model %d" % self._model_id
        self._model_id += 1
        mw = ModelWrapper(m, self, modelname)
        self.add_model(mw)
        mw.plot()
        return mw

    def add_model(self, model):
        self.models.append(model)
        self.model_added.emit(model)

    def remove_model(self, model):
        self.models.remove(model)
        self.model_removed.emit(model)
        self.plot()

    def nav_closing(self):
        if self.navigator_plot:
            p = self.navigator_plot.pos()
            self.navigator_plot.move(p.x() + self._magic_jump[0],
                                     p.y() + self._magic_jump[1])
            self._nav_geom = self.navigator_plot.saveGeometry()
            self.navigator_plot = None
        if self.signal_plot is None:
            self._closed()

    def sig_closing(self):
        if self.signal_plot:
            p = self.signal_plot.pos()
            # For some reason the position changes -8,-30 on closing, at least
            # it does on windows 7, Qt4.
            self.signal_plot.move(p.x() + self._magic_jump[0],
                                  p.y() + self._magic_jump[1])
            self._sig_geom = self.signal_plot.saveGeometry()
        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None
        self.signal_plot = None
        self._closed()

    def close(self):
        if self.signal_plot is not None:
            self.signal_plot.close()
            self.signal_plot = None

        if self.navigator_plot is not None:
            self.navigator_plot.close()
            self.navigator_plot = None
        self._closed()

    def _closed(self):
        if not self.keep_on_close:
            self.closing.emit()
        # TODO: Should probably be with by events for concistency
        if self in self.mainwindow.signals and not self.keep_on_close:
            self.mainwindow.signals.remove(self)
            self.signal._replot = self._old_replot
            self._old_replot = None
            self.signal = None
