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
Created on Fri Nov 21 22:22:33 2014

@author: Vidar Tonaas Fauske
"""

from functools import partial

from qtpy import QtCore, QtWidgets

import hyperspy.signals
from hyperspy.misc.elements import elements as elements_db

from hyperspyui.widgets.extendedqwidgets import FigureWidget, ExClickLabel
from hyperspyui.widgets.periodictable import PeriodicTableWidget
from hyperspyui.util import win2sig, block_signals


def tr(text):
    return QtCore.QCoreApplication.translate("ElementPickerWidget", text)

edstypes = (hyperspy.signals.EDSSEMSpectrum, hyperspy.signals.EDSTEMSpectrum)


class ElementPickerWidget(FigureWidget):

    """
    Tool window for picking elements of an interactive periodic table.
    Takes a signal in the constructor, and a parent control.
    """
    element_toggled = QtCore.Signal(str)

    def __init__(self, main_window, parent):
        super().__init__(main_window, parent)
        self.signal = None
        self.create_controls()
        self.table.element_toggled.connect(self._toggle_element)
        self.set_signal(self.signal)
        self._only_lines = ['Ka', 'La', 'Ma',
                            'Kb', 'Lb1', 'Mb']

    def _on_figure_change(self, figure):
        super()._on_figure_change(figure)
        signal = win2sig(figure, plotting_signal=self.ui._plotting_signal)
        self.set_signal(signal)

    def set_signal(self, signal):
        self.signal = signal
        self.setWindowTitle(tr("Element picker"))

        if self.isEDS():
            self.map_btn.show()
        else:
            self.map_btn.hide()

        if signal is None or signal.signal is None:
            self.set_enabled(False)
            return
        else:
            self.set_enabled(True)

        # Enable markers if plot has any
        with block_signals(self.chk_markers):
            markers = (hasattr(signal.signal, '_xray_markers') and
                       bool(signal.signal._xray_markers))
            self.chk_markers.setChecked(markers)

        # Make sure we have the Sample node, and Sample.elements
        if not hasattr(signal.signal.metadata, 'Sample'):
            signal.signal.metadata.add_node('Sample')
        if not hasattr(signal.signal.metadata.Sample, 'elements'):
            signal.signal.metadata.Sample.elements = []

        self._set_elements(signal.signal.metadata.Sample.elements)

        # Disable elements which hyperspy does not accept
        hsyp_elem = list(elements_db.keys())
        for w in self.table.children():
            if isinstance(w, ExClickLabel):
                elem = w.text()
                if elem not in hsyp_elem:
                    self.table.disable_element(elem)
                else:
                    self.table.enable_element(elem)

    def set_enabled(self, value):
        self.setEnabled(value)

    @property
    def markers(self):
        return self.chk_markers.isChecked()

    def isEDS(self):
        if self.signal is None or self.signal.signal is None:
            return False
        return isinstance(self.signal.signal, edstypes)

    def isEELS(self):
        if self.signal is None or self.signal.signal is None:
            return False
        return isinstance(self.signal.signal, hyperspy.signals.EELSSpectrum)

    def _toggle_element(self, element):
        """
        Makes sure the element is toggled correctly for both EDS and EELS.
        Dependent on hyperspy implementation, as there are currently no
        remove_element functions.
        """
        if self.isEELS():
            self._toggle_element_eels(element)
        elif self.isEDS():
            self._toggle_element_eds(element)

    def _toggle_element_eds(self, element):
        s = self.signal.signal
        lines_added = []
        lines_removed = []
        self.ui.record_code("signal = ui.get_selected_signal()")
        if element in s.metadata.Sample.elements:
            # Element present, we're removing it
            s.metadata.Sample.elements.remove(element)
            self.ui.record_code(
                "signal.metadata.Sample.elements.remove('%s')" % element)
            if 'Sample.xray_lines' in s.metadata:
                for line in reversed(s.metadata.Sample.xray_lines):
                    if line.startswith(element):
                        s.metadata.Sample.xray_lines.remove(line)
                        lines_removed.append(line)
                if len(s.metadata.Sample.xray_lines) < 1:
                    del s.metadata.Sample.xray_lines
            else:
                lines_removed.extend(s._get_lines_from_elements(
                                     [element], only_one=False,
                                     only_lines=self._only_lines))
        else:
            lines_added = s._get_lines_from_elements(
                [element], only_one=False, only_lines=self._only_lines)
            if 'Sample.xray_lines' in s.metadata:
                s.add_lines(lines_added)  # Will also add element
                self.ui.record_code(
                    "signal.add_lines(%s)" % str(lines_added))
            else:
                s.add_elements((element,))
                self.ui.record_code(
                    "signal.add_elements(%s)" % str([element]))
        if self.markers:
            if lines_added:
                s.add_xray_lines_markers(lines_added)
            if lines_removed:
                s.remove_xray_lines_markers(lines_removed)

    def _toggle_element_eels(self, element):
        s = self.signal.signal
        self.ui.record_code("signal = ui.get_selected_signal()")
        if element in s.metadata.Sample.elements:
            s.elements.remove(element)
            s.subshells = set()
            s.add_elements([])  # Will set metadata.Sample.elements
            self.ui.record_code(
                "signal.elements.remove('%s')" % str(element))
            self.ui.record_code(
                "signal.subshells = set()")
            self.ui.record_code(
                "signal.add_elements([])")
        else:
            s.add_elements((element,))
            self.ui.record_code(
                "signal.add_elements(%s)" % str([element]))

    def _toggle_subshell(self, subshell, checked):
        if not self.isEDS():
            return
        s = self.signal.signal
        element, ss = subshell.split('_')

        # Figure out whether element should be toggled
        active, _ = self._get_element_subshells(element)
        if checked:
            any_left = True
        elif ss in active:
            active.remove(ss)
            any_left = len(active) > 0

        # If any(subshells toggled) != element toggled, we should toggle
        # element
        if self.table.toggled[element] != any_left:
            # Update table toggle
            self.table.toggle_element(element)
            # Update signal state
            if not any_left:
                # Remove element
                self._toggle_element(element)

        self.ui.record_code("signal = ui.get_selected_signal()")
        if 'Sample.xray_lines' not in s.metadata and len(active) > 0:
            lines = [element + '_' + a for a in active]
            s.add_lines(lines)
            self.ui.record_code(
                "signal.add_lines(%s)" % str(lines))
            if self.markers:
                if checked:
                    s.add_xray_lines_markers(lines)
                else:
                    s.remove_xray_lines_markers([subshell])
        else:
            if checked:
                s.add_lines([subshell])
                self.ui.record_code(
                    "signal.add_lines(%s)" % str([subshell]))
                if self.markers:
                    s.add_xray_lines_markers([subshell])
            elif 'Sample.xray_lines' in s.metadata:
                if subshell in s.metadata.Sample.xray_lines:
                    s.metadata.Sample.xray_lines.remove(subshell)
                    self.ui.record_code(
                        "signal.metadata.Sample.xray_lines.remove('%s')" %
                        str(subshell))
                    if self.markers:
                        s.remove_xray_lines_markers([subshell])
                # If all lines are disabled, fall back to element defined
                # (Not strictly needed)
                if len(s.metadata.Sample.xray_lines) < 1:
                    del s.metadata.Sample.xray_lines
                    self.ui.record_code(
                        "del signal.metadata.Sample.xray_lines")

    def _set_elements(self, elements):
        """
        Sets the table elements to passed parameter. Does not modify elements
        in signal! That is handled by the _toggle_element* functions
        """
        self.table.set_elements(elements)

    def set_element(self, element, value):
        """Sets the state of element in table and adds/removes in signal if
        necessary
        """
        self.table.set_element(element, value)
        s = self.signal.signal
        if (element in s.metadata.Sample.elements) != value:
            self._toggle_element(element)

    def _on_toggle_markers(self, value):
        """Toggles peak markers on the plot, i.e. adds/removes markers for all
        elements added on signal.
        """
        w = self.signal
        s = self.signal.signal
        if value:
            if self.isEDS():
                w.keep_on_close = True
                s._plot_xray_lines(xray_lines=True)
                w.update_figures()
                w.keep_on_close = False
        else:
            if self.isEDS():
                for m in reversed(s._plot.signal_plot.ax_markers):
                    m.close(render_figure=False)
                if hasattr(s, '_xray_markers'):
                    s._xray_markers.clear()

    def make_map(self):
        """
        Make integrated intensity maps for the defines elements. Currently
        only implemented for EDS signals.
        """
        if self.isEELS():
            pass    # TODO: EELS maps
        elif self.isEDS():
            imgs = self.signal.signal.get_lines_intensity(only_one=False)
            for im in imgs:
                im.plot()

    def _get_element_subshells(self, element, include_pre_edges=False):
        s = self.signal.signal
        subshells = []
        possible_subshells = []
        if self.isEELS():
            subshells[:] = [ss.split('_')[0] for ss in s.subshells]

            Eaxis = s.axes_manager.signal_axes[0].axis
            if not include_pre_edges:
                start_energy = Eaxis[0]
            else:
                start_energy = 0.
            end_energy = Eaxis[-1]
            for shell in elements_db[element][
                    'Atomic_properties']['Binding_energies']:
                if shell[-1] != 'a':
                    if start_energy <= \
                            elements_db[element]['Atomic_properties'][
                            'Binding_energies'][shell]['onset_energy (eV)'] \
                            <= end_energy:
                        possible_subshells.add(shell)
        elif self.isEDS():
            if 'Sample.xray_lines' in s.metadata:
                xray_lines = s.metadata.Sample.xray_lines
                for line in xray_lines:
                    c_element, subshell = line.split("_")
                    if c_element == element:
                        subshells.append(subshell)
            elif ('Sample.elements' in s.metadata and
                  element in s.metadata.Sample.elements):
                xray_lines = s._get_lines_from_elements(
                    [element], only_one=False, only_lines=self._only_lines)
                for line in xray_lines:
                    _, subshell = line.split("_")
                    subshells.append(subshell)
            possible_xray_lines = \
                s._get_lines_from_elements([element], only_one=False,
                                           only_lines=self._only_lines)
            for line in possible_xray_lines:
                _, subshell = line.split("_")
                possible_subshells.append(subshell)

        return (subshells, possible_subshells)

    def element_context(self, widget, point):
        if not self.isEDS():
            return
        cm = QtWidgets.QMenu()
        element = widget.text()
        active, possible = self._get_element_subshells(element)
        for ss in possible:
            key = element + '_' + ss
            ac = cm.addAction(ss)
            ac.setCheckable(True)
            ac.setChecked(ss in active)
            f = partial(self._toggle_subshell, key)
            ac.toggled[bool].connect(f)
        if possible:
            cm.exec_(widget.mapToGlobal(point))

    def create_controls(self):
        """
        Create UI controls.
        """
        self.table = PeriodicTableWidget(self)
        self.table.element_toggled.connect(self.element_toggled)    # Forward
        for w in self.table.children():
            if not isinstance(w, ExClickLabel):
                continue
            w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            f = partial(self.element_context, w)
            w.customContextMenuRequested[QtCore.QPoint].connect(f)

        self.chk_markers = QtWidgets.QCheckBox(tr("Markers"))
        self.chk_markers.toggled[bool].connect(self._on_toggle_markers)
        self.map_btn = QtWidgets.QPushButton(tr("Map"))
        self.map_btn.clicked.connect(self.make_map)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.chk_markers)
        hbox.addWidget(self.map_btn)
        vbox.addLayout(hbox)

        w = QtWidgets.QWidget()
        w.setLayout(vbox)
        self.setWidget(w)
