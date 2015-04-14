# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:25:54 2014

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtCore, QtGui
#from hyperspy.model import Model
import hyperspy.models
from actionable import Actionable
from functools import partial

# TODO: Add smartfit for EELSModel


def tr(text):
    return QtCore.QCoreApplication.translate("ModelWrapper", text)


class ModelWrapper(Actionable):
    added = QtCore.Signal((object, object), (object,))
    removed = QtCore.Signal((object, object), (object,))

    def __init__(self, model, signal_wrapper, name):
        super(ModelWrapper, self).__init__()
        self.model = model
        self.signal = signal_wrapper
        self.name = name
        if self.signal.signal is not self.model.spectrum:
            raise ValueError("SignalWrapper doesn't match model.signal")
        self.components = {}
        self.update_components()

        self.fine_structure_enabled = False

        # Default actions
        self.add_action('plot', tr("&Plot"), self.plot)
        self.add_action('fit', tr("&Fit"), self.fit)
        self.add_action('multifit', tr("&Multifit"), self.multifit)
        self.add_action('set_signal_range', tr("Set signal &range"),
                        self.set_signal_range)
        if isinstance(self.model, hyperspy.models.eelsmodel.EELSModel):
            self.add_action('lowloss', tr("Set low-loss"), self.set_lowloss)
            self.add_action('fine_structure', tr("Enable fine &structure"),
                            self.toggle_fine_structure)
        f = partial(self.signal.remove_model, self)
        self.add_action('delete', tr("&Delete"), f)

    def plot(self):
        self.signal.keep_on_close = True
        self.model.plot()
        self.signal.keep_on_close = False
        self.signal.update_figures()
        self.signal.signal_plot.setProperty('hyperspyUI.ModelWrapper', self)

    def update_plot(self):
        self.model.update_plot()

    def fit(self):
        self.signal.keep_on_close = True
        self.model.fit()
        self.signal.keep_on_close = False
        self.signal.update_figures()

    def multifit(self):
        self.signal.keep_on_close = True
        self.model.multifit()
        self.signal.keep_on_close = False
        self.signal.update_figures()

    def fit_component(self, component):
        # This is a non-blocking call, which means the normal keep_on_close +
        # update_figures won't work. To make sure we keep our figures,
        # we force a plot first if it is not active already.
        if not self.model._plot.is_active():
            self.plot()
        self.model.fit_component(component)

    def set_signal_range(self, *args, **kwargs):
        self.signal.keep_on_close = True
        self.model.set_signal_range(*args, **kwargs)
        self.signal.keep_on_close = False
        self.signal.update_figures()

    def set_lowloss(self, signal=None):
        if signal is None:
            signal = self.signal.mainwindow.select_x_signals(
                1, ['Select low-loss'])
            if signal is None:
                return
        self.model.lowloss = signal.signal

    def toggle_fine_structure(self):
        if not isinstance(self.model, hyperspy.models.eelsmodel.EELSModel):
            raise TypeError(
                tr("Model is not EELS model. Can not toggle fine structure"))
        if self.fine_structure_enabled:
            self.model.disable_fine_structure()
            self.actions['fine_structure'].setText(
                tr("Enable fine &structure"))
        else:
            self.model.enable_fine_structure()
            self.actions['fine_structure'].setText(
                tr("Disable fine &structure"))
        self.fine_structure_enabled = not self.fine_structure_enabled

    def update_components(self):
        """
        Updates internal compoenent list to match model's list (called e.g.
        after console execute and in constructor)
        """

        # Add missing
        for c in self.model:
            if c.name not in self.components.keys():
                self.components[c.name] = c
                self.component_added(c)

        # Remove lingering
        ml = [c.name for c in self.model]
        rm = [cn for cn in self.components.keys() if cn not in ml]
        for n in rm:
            c = self.components.pop(n)
            self.component_removed(c)

    def add_component(self, component):
        if isinstance(component, type):
            nec = ['EELSCLEdge', 'Spline', 'ScalableFixedPattern']
            if component.__name__ in nec:
                raise TypeError(
                    tr("Component of type %s currently not supported")
                    % component)
            component = component()

        added = False
        if component not in self.model:
            self.model.append(component)
            added = True
        if component.name not in self.components:
            self.components[component.name] = component
            added = True
        if added:
            self.component_added(component)

    def remove_component(self, component):
        removed = False
        if component in self.model:
            self.model.remove(component)
            removed = True
        if component.name in self.components:
            self.components.pop(component.name)
            removed = True
        if removed:
            self.component_removed(component)

    def component_added(self, component):
        self.update_plot()
        self.added[object, object].emit(component, self)
        self.added[object].emit(component)

    def component_removed(self, component):
        self.update_plot()
        self.removed[object, object].emit(component, self)
        self.removed[object].emit(component)
