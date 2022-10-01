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
Created on Tue Nov 04 16:25:54 2014

@author: Vidar Tonaas Fauske
"""


from qtpy import QtCore
#from hyperspy.model import Model
import hyperspy.models.eelsmodel
from .actionable import Actionable
from functools import partial

from hyperspyui.widgets.stringinput import StringInputDialog

# TODO: Add smartfit for EELSModel


def tr(text):
    return QtCore.QCoreApplication.translate("ModelWrapper", text)


class ModelWrapper(Actionable):
    added = QtCore.Signal((object, object), (object,))
    removed = QtCore.Signal((object, object), (object,))

    def __init__(self, model, signal_wrapper, name):
        super().__init__()
        self.model = model
        self.signal = signal_wrapper
        self.name = name
        if self.signal.signal is not self.model.signal:
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

    def record_code(self, code):
        self.signal.mainwindow.record_code("model = ui.get_selected_model()")
        self.signal.mainwindow.record_code(code)

    def _args_for_record(self, args, kwargs):
        argstr = str(args)[1:-1]
        kwargstr = str(kwargs)[1:-1]
        kwargstr = kwargstr.replace(": ", "=")
        if argstr and kwargstr:
            return ", ".join((argstr, kwargstr))
        else:
            return argstr + kwargstr

    def fit(self, *args, **kwargs):
        self.signal.keep_on_close = True
        self.model.fit(*args, **kwargs)
        self.signal.keep_on_close = False
        self.signal.update_figures()
        self.record_code(
            "model.fit(%s)" % self._args_for_record(args, kwargs)
            )

    def multifit(self, *args, **kwargs):
        self.signal.keep_on_close = True
        self.model.multifit(*args, **kwargs)
        self.signal.keep_on_close = False
        self.signal.update_figures()
        self.record_code(
            "model.multifit(%s)" % self._args_for_record(args, kwargs)
            )

    def smartfit(self, *args, **kwargs):
        if hasattr(self.model, 'smartfit'):
            self.signal.keep_on_close = True
            self.model.smartfit(*args, **kwargs)
            self.signal.keep_on_close = False
            self.signal.update_figures()
            self.record_code(
                "model.smartfit(%s)" % self._args_for_record(args, kwargs)
                )

    def fit_component(self, component):
        # This is a non-blocking call, which means the normal keep_on_close +
        # update_figures won't work. To make sure we keep our figures,
        # we force a plot first if it is not active already.
        if not self.model.signal._plot.is_active:
            self.plot()
        self.model.fit_component(component)
        self.record_code("model.fit_component(%s)" % component.name)

    def set_signal_range(self, *args, **kwargs):
        self.signal.keep_on_close = True
        self.model.set_signal_range(*args, **kwargs)
        self.signal.keep_on_close = False
        self.signal.update_figures()
        self.record_code(
            "model.set_signal_range(%s)" % self._args_for_record(args, kwargs)
            )

    def set_lowloss(self, signal=None):
        if signal is None:
            signal = self.signal.mainwindow.select_x_signals(
                1, ['Select low-loss'])
            if signal is None:
                return
        self.model.lowloss = signal.signal
        self.record_code("model.set_lowloss(low_loss_signal)")

    def toggle_fine_structure(self):
        if not isinstance(self.model, hyperspy.models.eelsmodel.EELSModel):
            raise TypeError(
                tr("Model is not EELS model. Can not toggle fine structure"))
        if self.fine_structure_enabled:
            self.model.disable_fine_structure()
            self.actions['fine_structure'].setText(
                tr("Enable fine &structure"))
            self.record_code("model.disable_fine_structure()")
        else:
            self.model.enable_fine_structure()
            self.actions['fine_structure'].setText(
                tr("Disable fine &structure"))
            self.record_code("model.enable_fine_structure()")
        self.fine_structure_enabled = not self.fine_structure_enabled

    def update_components(self):
        """
        Updates internal compoenent list to match model's list (called e.g.
        after console execute and in constructor)
        """

        # Add missing
        for c in self.model:
            if c.name not in list(self.components.keys()):
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
            elif component.__name__ == 'Expression':
                dlg = StringInputDialog(prompt="Enter expression:")
                expression = dlg.prompt_modal(rejection=None)
                if expression:
                    component = component(expression, 'Expression')
                else:
                    return
            else:
                component = component()

        added = False
        if component not in self.model:
            self.model.append(component)
            added = True
            self.record_code("model.append(%s)" % component.name)
        if component.name not in self.components:
            self.components[component.name] = component
            added = True
        if added:
            self.component_added(component)

    def remove_component(self, component):
        removed = False
        if component in self.model:
            self.model.remove(component)
            self.record_code("model.remove(%s)" % component.name)
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
