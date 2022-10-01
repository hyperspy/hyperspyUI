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

from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs
from hyperspy.drawing import utils
from functools import partial


class VirtualBfDf(Plugin):
    name = "Virtual BF/DF"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rois = []

    def create_actions(self):
        self.add_action(self.name + '.virtual_navigator',
                        "Virtual navigator",
                        self.virtual_navigator,
                        tip="Set the navigator inesity by a virtual aperture")
        self.add_action(self.name + '.virtual_aperture',
                        "Virtual aperture",
                        self.virtual_aperture,
                        tip="Add a virtual aperture to the diffraction image")
        self.add_action(self.name + '.virtual_annulus',
                        "Virtual annulus",
                        self.virtual_annulus,
                        tip="Add a virtual annulus to the diffraction image")

    def create_menu(self):
        self.add_menuitem(
            'Diffraction', self.ui.actions[self.name + '.virtual_navigator'])
        self.add_menuitem(
            'Diffraction', self.ui.actions[self.name + '.virtual_aperture'])
        self.add_menuitem(
            'Diffraction', self.ui.actions[self.name + '.virtual_annulus'])

    def _on_close(self, roi):
        for w in roi.widgets:
            w.close()
        roi.signal_map.clear()
        if roi in self._rois:
            self._rois.remove(roi)

    def virtual_navigator(self, signal=None):
        return self.virtual_aperture(signal=signal, navigate=True)

    def virtual_annulus(self, signal=None):
        return self.virtual_aperture(signal=signal, annulus=True)

    def virtual_aperture(self, signal=None, annulus=False, navigate=False):
        ui = self.ui
        if signal is None:
            signal = ui.get_selected_signal()
        dd = np.array([a.high_value + a.low_value for a in
                       signal.axes_manager.signal_axes]) / 2.0
        r = hs.roi.CircleROI(dd[0], dd[1],
                             signal.axes_manager.signal_axes[0].scale*3)
        if annulus:
            r.r_inner = signal.axes_manager.signal_axes[0].scale*2
        s_virtual = r.interactive(signal, None,
                                  axes=signal.axes_manager.signal_axes)
        s_nav = hs.interactive(
            s_virtual.mean,
            s_virtual.events.data_changed,
            axis=s_virtual.axes_manager.signal_axes)
        s_nav.axes_manager.set_signal_dimension(2)
        if navigate:
            signal.plot(navigator=s_nav)
            signal._plot.navigator_plot.update()
            s_nav.events.data_changed.connect(
                signal._plot.navigator_plot.update, [])
            utils.on_figure_window_close(
                signal._plot.navigator_plot.figure,
                partial(self._on_close, r))
        else:
            s_nav.plot()
            utils.on_figure_window_close(
                s_nav._plot.signal_plot.figure,
                partial(self._on_close, r))

        if navigate:
            r.add_widget(signal, axes=signal.axes_manager.signal_axes,
                         color='darkorange')
        else:
            r.add_widget(signal, axes=signal.axes_manager.signal_axes)
        self._rois.append(r)
        self.record_code("<p>.virtual_aperture(navigate=%s)" % navigate)
