# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 15:20:55 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.widgets.elementpicker import ElementPickerWidget
from hyperspyui.threaded import Threaded
from hyperspyui.util import SignalTypeFilter
from hyperspyui.tools import SignalFigureTool

import hyperspy.signals
from hyperspy.misc.eds.utils import _get_element_and_line
import numpy as np

import os
from functools import partial


def tr(text):
    return QCoreApplication.translate("BasicSpectrumPlugin", text)


class Namespace:
    pass


QWIDGETSIZE_MAX = 16777215


class BasicSpectrumPlugin(Plugin):
    name = "Basic spectrum tools"

    def create_actions(self):
        self.add_action('plot_components', tr("Plot components"),
                        self.plot_components,
                        icon=None,
                        tip=tr(""),
                        selection_callback=self._plot_components_state_update)
        self.actions['plot_components'].setCheckable(True)

        self.add_action('remove_background', tr("Remove Background"),
                        self.remove_background,
                        icon='power_law.svg',
                        tip=tr("Interactively define the background, and "
                               "remove it"),
                        selection_callback=SignalTypeFilter(
                            hyperspy.signals.Spectrum, self.ui))

        self.add_action('fourier_ratio', tr("Fourier Ratio Deconvoloution"),
                        self.fourier_ratio,
                        icon='fourier_ratio.svg',
                        tip=tr("Use the Fourier-Ratio method to deconvolve "
                               "one signal from another"),
                        selection_callback=SignalTypeFilter(
                            hyperspy.signals.EELSSpectrum, self.ui))

        self.add_action('estimate_thickness', tr("Estimate thickness"),
                        self.estimate_thickness,
                        icon="t_over_lambda.svg",
                        tip=tr("Estimates the thickness (relative to the "
                               "mean free path) of a sample using the "
                               "log-ratio method."),
                        selection_callback=SignalTypeFilter(
                            hyperspy.signals.EELSSpectrum, self.ui))

    def create_menu(self):
        self.add_menuitem("Model", self.ui.actions['plot_components'])
        self.add_menuitem("EELS", self.ui.actions['remove_background'])
        self.add_menuitem('EELS', self.ui.actions['fourier_ratio'])
        self.add_menuitem('EELS', self.ui.actions['estimate_thickness'])

    def create_toolbars(self):
        self.add_toolbar_button("EELS", self.ui.actions['remove_background'])
        self.add_toolbar_button("EELS", self.ui.actions['fourier_ratio'])
        self.add_toolbar_button("EELS", self.ui.actions['estimate_thickness'])

    def create_tools(self):
        try:
            from hyperspy.misc.eds.utils import get_xray_lines_near_energy as _
            self.picker_tool = ElementPickerTool()
            self.picker_tool.picked[basestring].connect(self.pick_element)
            self.add_tool(self.picker_tool,
                          SignalTypeFilter(
                              (  # hyperspy.signals.EELSSpectrum,
                               hyperspy.signals.EDSSEMSpectrum,
                               hyperspy.signals.EDSTEMSpectrum),
                              self.ui))
        except ImportError:
            pass

    def _toggle_fixed_height(self, floating):
        w = self.picker_widget
        if floating:
            w.setFixedHeight(QWIDGETSIZE_MAX)
        else:
            w.setFixedHeight(w.minimumSize().height())

    def create_widgets(self):
        self.picker_widget = ElementPickerWidget(self.ui, self.ui)
        self.picker_widget.topLevelChanged[bool].connect(
            self._toggle_fixed_height)
        self.add_widget(self.picker_widget)
        self._toggle_fixed_height(False)

    def pick_element(self, element, signal=None):
        wp = self.picker_widget
        if signal:
            wp.set_signal(signal)
        wp.set_element(element, True)
        if not wp.chk_markers.isChecked():
            wp.chk_markers.setChecked(True)

    def _plot_components_state_update(self, win, action):
        model = self.ui.get_selected_model()
        action.setEnabled(model is not None)
        if model is not None:
            action.setChecked(model._plot_components)

    def plot_components(self, model=None):
        if model is None:
            model = self.ui.get_selected_model()
        if model is None:
            return
        current = model._plot_components
        if current:
            model.enable_plot_components()
        else:
            model.disable_plot_components()

    def fourier_ratio(self):
        signals = self.ui.select_x_signals(2, [tr("Core loss"),
                                               tr("Low loss")])
        if signals is not None:
            s_core, s_lowloss = signals

            # Variable to store return value in
            ns = Namespace()
            ns.s_return = None

#            s_core.signal.remove_background()
            def run_fr():
                ns.s_return = s_core.signal.fourier_ratio_deconvolution(
                    s_lowloss.signal)
                ns.s_return.data = np.ma.masked_array(
                    ns.s_return.data,
                    mask=(np.isnan(ns.s_return.data) |
                          np.isinf(ns.s_return.data)))

            def fr_complete():
                ns.s_return.metadata.General.title = \
                    s_core.name + "[Fourier-ratio]"
                ns.s_return.plot()

            t = Threaded(self.ui, run_fr, fr_complete)
            t.run()

    def remove_background(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_wrapper()
        signal.signal.remove_background()

    def estimate_thickness(self):
        ui = self.ui
        s = ui.get_selected_signal()
        s_t = s.estimate_thickness(3.0)
        s_t.plot()


class ElementPickerTool(SignalFigureTool):
    picked = Signal(basestring)

    def __init__(self, windows=None):
        super(ElementPickerTool, self).__init__(windows)
        self.ranged = False
        self.valid_dimensions = [1]

    def get_name(self):
        return "Element picker tool"

    def get_category(self):
        return 'EDS'

    def get_icon(self):
        return os.path.dirname(__file__) + '/../images/periodic_table.svg'

    def on_pick_line(self, line):
        el, _ = _get_element_and_line(line)
        self.picked.emit(el)

    def is_selectable(self):
        return True

    def on_mouseup(self, event):
        if event.inaxes is None:
            return
        energy = event.xdata
        axes = self._get_axes(event)
        if len(axes) not in self.valid_dimensions:
            return
        a = axes[0]
        if a.units.lower() == 'ev':
            energy /= 1000.0
        from hyperspy.misc.eds.utils import get_xray_lines_near_energy
        lines = get_xray_lines_near_energy(energy)
        if lines:
            m = QMenu()
            for line in lines:
                m.addAction(line, partial(self.on_pick_line, line))
            m.exec_(QCursor.pos())
