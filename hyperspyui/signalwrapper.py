# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 18:27:15 2014

@author: Vidar Tonaas Fauske
"""

from util import fig2win
from python_qt_binding import QtCore, QtGui

from modelwrapper import ModelWrapper
from actionable import Actionable
import hyperspy.hspy


class SignalWrapper(Actionable):
    closing = QtCore.Signal()
    model_added = QtCore.Signal(object)
    model_removed = QtCore.Signal(object)

    def __init__(self, signal, mainwindow, name):
        super(SignalWrapper, self).__init__()
        self.signal = signal
        self._old_replot = signal._replot
        signal._replot = self._replot
        if name is None:
            name = signal.metadata.General.title
        self.name = name
        self.figures = []
        self.mainwindow = mainwindow
        self.models = []

        self._keep_on_close = 0

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

    def _replot(self):
        if self.signal._plot is not None:
            if self.signal._plot.is_active() is True:
                self.replot()

    def replot(self):
        old = self.mainwindow.updatesEnabled()
        self.mainwindow.setUpdatesEnabled(False)
        try:
            self.plot(*self._replotargs[0], **self._replotargs[1])
        finally:
            self.mainwindow.setUpdatesEnabled(old)

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
                navi.axes[0].set_title("")  # remove title
                navi.tight_layout()
                # Wire closing event
                self.navigator_plot.closing.connect(self.nav_closing)
                # Set a reference on window to self
                self.navigator_plot.setProperty('hyperspyUI.SignalWrapper',
                                                self)
                # Add to figures list
                self.add_figure(self.navigator_plot)

                # Did we have a previous window?
                if old_nav is not None:
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
                sigp.axes[0].set_title("")
                sigp.tight_layout()
                self.signal_plot.closing.connect(self.sig_closing)
                self.signal_plot.setProperty('hyperspyUI.SignalWrapper', self)
                self.add_figure(self.signal_plot)
                if old_sig is not None:
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

    def as_image(self, axis=(0, 1)):
        self.close()  # Store geomtery and close
        tmp = self._sig_geom
        self._sig_geom = self._nav_geom
        self._nav_geom = tmp
        self.signal = self.signal.as_image(axis)

    def as_spectrum(self, axis=0):
        self.close()  # Store geomtery and close
        tmp = self._sig_geom
        self._sig_geom = self._nav_geom
        self._nav_geom = tmp
        self.signal = self.signal.as_spectrum(axis)

    def run_nonblock(self, function, windowtitle):
        self.keep_on_close = True

        def on_close():
            self.keep_on_close = False
            self.update_figures()

        def on_capture(dialog):
            dialog.destroyed.connect(on_close)
            dialog.setParent(self.mainwindow, QtCore.Qt.Tool)
            dialog.show()
            dialog.activateWindow()

        # Setup capture
        self.mainwindow.capture_traits_dialog(on_capture)

        # Call actual function that triggers dialog
        function()

    def make_model(self, *args, **kwargs):
        m = hyperspy.hspy.create_model(self.signal, *args, **kwargs)
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
            self.navigator_plot.move(p.x() + 8, p.y() + 30)
            self._nav_geom = self.navigator_plot.saveGeometry()
            self.navigator_plot = None
        if self.signal_plot is None:
            self._closed()

    def sig_closing(self):
        if self.signal_plot:
            p = self.signal_plot.pos()
            # For some reason the position changes -8,-30 on closing, at least
            # it does on windows 7, Qt4.
            self.signal_plot.move(p.x() + 8, p.y() + 30)
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
