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
Created on Sun Mar 01 15:20:55 2015

@author: Vidar Tonaas Fauske
"""

import sys

from hyperspyui.plugins.plugin import Plugin
from hyperspy.utils import stack as stack_signals

from qtpy import QtCore, QtWidgets

from hyperspyui.widgets.axespicker import AxesPickerDialog


def tr(text):
    return QtCore.QCoreApplication.translate("BasicSignalPlugin", text)


class BasicSignalPlugin(Plugin):
    name = "Basic signal tools"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings.set_default('histogram_bins_method', 'freedman')
        self.settings.set_enum_hint(
            'histogram_bins_method',
            ('knuth', 'scotts', 'freedman', 'blocks', '<integer>'))

    def create_actions(self):
        self.add_action(self.name + '.stack', "Stack", self.stack,
                        tip="Stack selected signals along a new navigation "
                        "axis")

        self.add_action(self.name + '.split', "Split", self.split,
                        tip="Split selected signal along an axis")

        self.add_action(self.name + '.copy', "Copy", self.copy,
                        tip="Make a copy of all selected signals")

        self.add_action(self.name + '.switch', "Switch spaces", self.switch,
                        tip="Switch navigation and signal spaces")

        self.add_action('stats', tr("Statistics"),
                        self.statistics,
                        icon=None,
                        tip=tr("Print the signal statistics to the console."),
                        selection_callback=self.ui.select_signal)

        self.add_action('histogram', tr("Histogram"),
                        self.histogram,
                        icon=None,
                        tip=tr("Plot a histogram of the signal."),
                        selection_callback=self.ui.select_signal)

        self.add_action('add', tr("Add"),
                        self.add,
                        icon='add.svg',
                        tip=tr("Add the currently selected signals"),
                        selection_callback=self.ui.select_signal)

        self.add_action('subtract', tr("Subtract"),
                        self.subtract,
                        icon='subtract.svg',
                        tip=tr("Subtract two signals"),
                        selection_callback=self.ui.select_signal)

        self.add_action('multiply', tr("Multiply"),
                        self.multiply,
                        icon='multiply.svg',
                        tip=tr("Multiply the currently selected signals"),
                        selection_callback=self.ui.select_signal)

        self.add_action('divide', tr("Divide"),
                        self.divide,
                        icon='divide.svg',
                        tip=tr("Divide two signals"),
                        selection_callback=self.ui.select_signal)

        self.add_action('mean', tr("Mean"),
                        self.mean,
                        icon='mean.svg',
                        tip=tr("Take the mean of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('sum', tr("Sum"),
                        self.sum,
                        icon='sum.svg',
                        tip=tr("Take the sum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('max', tr("Maximum"),
                        self.max,
                        icon='max.svg',
                        tip=tr("Take the maximum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('min', tr("Minimum"),
                        self.min,
                        icon='min.svg',
                        tip=tr("Take the sum of the current signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('std', tr("Std.dev."),
                        self.std,
                        icon='stddev.svg',
                        tip=tr("Take the standard deviation of the current "
                               "signal"),
                        selection_callback=self.ui.select_signal)

        self.add_action('var', tr("Variance"),
                        self.var,
                        icon='variance.svg',
                        tip=tr("Take the variances of the current signal"),
                        selection_callback=self.ui.select_signal)

#        max, min, std, var, diff?, derivate?, integrate_simpson, integrate1D,
#        indexmax, valuemax

    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions[self.name + '.stack'])
        self.add_menuitem('Signal', self.ui.actions[self.name + '.split'])
        self.add_menuitem('Signal', self.ui.actions[self.name + '.copy'])
        self.add_menuitem('Signal', self.ui.actions[self.name + '.switch'])
        self.add_menuitem("Signal", self.ui.actions['stats'])
        self.add_menuitem("Signal", self.ui.actions['histogram'])
        self.add_menuitem("Math", self.ui.actions['add'])
        self.add_menuitem("Math", self.ui.actions['subtract'])
        self.add_menuitem("Math", self.ui.actions['multiply'])
        self.add_menuitem("Math", self.ui.actions['divide'])
        self.add_menuitem("Math", self.ui.actions['mean'])
        self.add_menuitem('Math', self.ui.actions['sum'])
        self.add_menuitem('Math', self.ui.actions['max'])
        self.add_menuitem('Math', self.ui.actions['min'])
        self.add_menuitem('Math', self.ui.actions['std'])
        self.add_menuitem('Math', self.ui.actions['var'])

    def create_toolbars(self):
        self.add_toolbar_button("Math", self.ui.actions['add'])
        self.add_toolbar_button("Math", self.ui.actions['subtract'])
        self.add_toolbar_button("Math", self.ui.actions['multiply'])
        self.add_toolbar_button("Math", self.ui.actions['divide'])
        self.add_toolbar_button("Math", self.ui.actions['mean'])
        self.add_toolbar_button('Math', self.ui.actions['sum'])
        self.add_toolbar_button('Math', self.ui.actions['max'])
        self.add_toolbar_button('Math', self.ui.actions['min'])
        self.add_toolbar_button('Math', self.ui.actions['std'])
        self.add_toolbar_button('Math', self.ui.actions['var'])

    def stack(self, signals=None, advanced=False):
        if signals is None:
            signals = self.ui.get_selected_signals()
        if signals is None:
            raise ValueError("No signals to stack")
        self.record_code('signals = self.ui.get_selected_signals()')
        if advanced:
            # Advanced mode: Pop up a dialog to prompt for axes to sum over=
            axis = self._prompt_axes(signals[0], single=True)
            if not axis:
                return
            stack = stack_signals(signals, axis=axis.name)
            self.record_code('s_stack = hs.stack(signals, axis="%s")' %
                             axis.name)
        else:
            stack = stack_signals(signals)
            self.record_code('s_stack = hs.stack(signals)')
        stack.plot()

    def split(self, signal=None, advanced=False):
        if signal is None:
            signal = self.ui.get_selected_signal()
        if signal is None:
            raise ValueError('No signal to split')
        axis = 'auto'
        if advanced:
            axis = self._prompt_axes(signal, single=True)
            if not axis:
                return
            axis = axis.name
        signals = signal.split(axis=axis)
        for s in signals:
            s.plot()

    def copy(self, signals=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        for s in signals:
            s.deepcopy().plot()
        self.record_code('signals = self.ui.get_selected_signals()')
        self.record_code('for s in signals:\n\ts.deepcopy().plot()')

    def switch(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        # Switch the nav and sig spaces:
        switched = signal.transpose(signal.axes_manager.navigation_axes,
                                    signal.axes_manager.signal_axes)
        switched.plot()
        self.record_code("signal = ui.get_selected_signal()")
        self.record_code(
            "switched = signal.transpose(" +
            "signal.axes_manager.navigation_axes, " +
            "signal.axes_manager.signal_axes)")

    def statistics(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        # If we're using an external console for errors, we need to temporarily
        # redirect stdout
        _old_stdout = None
        if self.ui.settings['output_to_console', bool]:
            _old_stdout = sys.stdout
            sys.stdout = self.ui.console.kernel.stdout
        try:
            signal.print_summary_statistics()
            self.record_code("signal = ui.get_selected_signal()")
            self.record_code("signal.print_summary_statistics()")
        finally:
            if self.ui.settings['output_to_console', bool]:
                sys.stdout = _old_stdout

    def histogram(self, signal=None):
        signal = signal or self.ui.get_selected_signal()
        if signal is not None:
            method = self.settings['histogram_bins_method']
            signal.get_histogram(bins=method).plot()
            self.record_code("signal = ui.get_selected_signal()")
            self.record_code("histogram = signal.get_histogram(bins=%s)" %
                             method)

    def _prompt_axes(self, signal, single=False):
        diag = AxesPickerDialog(self.ui, signal, single)
        diag.setWindowTitle("Select axes to operate on")
        dr = diag.exec_()
        if dr == QtWidgets.QDialog.Accepted:
            return diag.selected_axes
        return None

    def _np_method(self, name, signal, advanced):
        if signal is None:
            signal = self.ui.get_selected_signal()
        f = getattr(signal, name)
        if advanced:
            # Advanced mode: Pop up a dialog to prompt for axes to sum over=
            axes = self._prompt_axes(signal)
            if not axes:
                return
            f(axis=axes).plot()
        else:
            f().plot()
        self.record_code("signal = ui.get_selected_signal()")
        self.record_code("result = signal.%s()" % name)

    def mean(self, signal=None, advanced=False):
        self._np_method('mean', signal, advanced)

    def sum(self, signal=None, advanced=False):
        self._np_method('sum', signal, advanced)

    def max(self, signal=None, advanced=False):
        self._np_method('max', signal, advanced)

    def min(self, signal=None, advanced=False):
        self._np_method('min', signal, advanced)

    def std(self, signal=None, advanced=False):
        self._np_method('std', signal, advanced)

    def var(self, signal=None, advanced=False):
        self._np_method('var', signal, advanced)

    def add(self, signals=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        if len(signals) < 2:
            raise ValueError(
                "Two or more signals should be selected for addition!")
        s = signals[0] + signals[1]
        for sb in signals[2:]:
            s += sb
        s.plot()
        self.record_code("signals = ui.get_selected_signals()")
        self.record_code("result = signals[0] + signals[1]")
        if len(signals) == 2:
            self.record_code("for other in signals[2:]:")
            self.record_code("    result += other")

    def subtract(self, signals=None):
        if signals is None:
            signals = self.ui.select_x_signals(2, ["a", " - b"])
            signals = [s.signal for s in signals]
            self.record_code(
                "signals = [s.signal for s in "
                "ui.select_x_signals(2, [\"a\", \" - b\"])")
        elif len(signals != 2):
            raise ValueError(
                "Subtraction can only be performed with two signals")
        result = signals[0] - signals[1]
        result.plot()
        self.record_code("result = signals[0] - signals[1]")

    def multiply(self, signals=None):
        if signals is None:
            signals = self.ui.get_selected_signals()
        if len(signals) < 2:
            raise ValueError(
                "Two or more signals should be selected for multiplication!")
        s = signals[0] * signals[1]
        for sb in signals[2:]:
            s *= sb
        s.plot()
        self.record_code("signals = ui.get_selected_signals()")
        self.record_code("result = signals[0] * signals[1]")
        if len(signals) == 2:
            self.record_code("for other in signals[2:]:")
            self.record_code("    result *= other")

    def divide(self, signals=None):
        if signals is None:
            signals = self.ui.select_x_signals(2, ["a", " - b"])
            signals = [s.signal for s in signals]
            self.record_code(
                "signals = [s.signal for s in "
                "ui.select_x_signals(2, [\"a\", \" - b\"])")
        elif len(signals != 2):
            raise ValueError(
                "Division can only be performed with two signals")
        result = signals[0] / signals[1]
        result.plot()
        self.record_code("result = signals[0] / signals[1]")
