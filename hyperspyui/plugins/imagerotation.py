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
Created on Wed Jan 21 14:49:08 2015

@author: Vidar Tonaas Fauske
"""


from qtpy import QtCore
from qtpy.QtWidgets import (QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout,
                            QFormLayout, QDoubleSpinBox, QGroupBox, QSpinBox,
                            QRadioButton)

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.widgets.extendedqwidgets import ExToolWindow
from scipy.ndimage import rotate
import numpy as np
from hyperspyui.util import win2sig, dummy_context_manager
from hyperspyui.signalwrapper import SignalWrapper


def tr(text):
    return QtCore.QCoreApplication.translate("ImageRotation", text)


class ImageRotation_Plugin(Plugin):
    name = 'Image Rotation'

    def create_actions(self):
        self.settings.set_enum_hint('new_or_replace', ['new', 'replace'])
        self.add_action('rotate', "Rotate", self.show_rotate_dialog,
                        icon='rotate.svg',
                        tip="Rotate an image",
                        selection_callback=self.selection_rules)

    def create_menu(self):
        self.add_menuitem('Image', self.ui.actions['rotate'])

    def create_toolbars(self):
        self.add_toolbar_button("Image", self.ui.actions['rotate'])

    def selection_rules(self, win, action):
        """
        Callback to determine if rotation is valid for the passed window.
        """
        s = win2sig(win, self.ui.signals)
        ok = False
        if s is not None:
            if win == s.navigator_plot and \
                    s.signal.axes_manager.navigation_dimension >= 2:
                ok = True
            elif win == s.signal_plot and \
                    s.signal.axes_manager.signal_dimension == 2:
                ok = True
        if ok:
            action.setEnabled(True)
        else:
            action.setEnabled(False)

    def rotate_signal(self, angle, signal=None, reshape=False, out=None,
                      record=True, *args, **kwargs):
        if signal is None:
            signal, axes, _ = self.ui.get_selected_plot()
            if isinstance(axes, str):
                axm = signal.signal.axes_manager
                if axes.startswith("nav"):
                    axes = (axm._axes.index(axm.navigation_axes[0]),
                            axm._axes.index(axm.navigation_axes[1]))
                elif axes.startswith("sig"):
                    axes = (axm._axes.index(axm.signal_axes[0]),
                            axm._axes.index(axm.signal_axes[1]))
            kwargs['axes'] = axes
        if isinstance(signal, SignalWrapper):
            signal = signal.signal
        if record:
            self.record_code(
                r"<p>.rotate_signal({0}, reshape={1}, {2}, {3})".format(
                    angle, reshape, args, kwargs))
        # Reframe into 0-360 deg
        angle %= 360
        const_mode = 'mode' not in kwargs or kwargs['mode'] == 'constant'
        # Check if multiple of 90 deg -> Fast rotation
        if round(angle % 90, 2) == 0 and (reshape or const_mode):
            angle = 90 * (angle // 90)
            axes = kwargs.pop('axes', (1, 0))
            k = angle // 90
            if k > 0:
                if k == 1:  # 90 deg
                    # Invert axes[0]
                    s = (slice(None),)* axes[0] + (slice(None, None, -1),) + \
                        (Ellipsis,)
                elif k == 2:  # 180 deg
                    # Invert both axes
                    axisA = min(axes[0], axes[1])
                    axisB = max(axes[0], axes[1])
                    adiff = (axisB-axisA-1)
                    s = (slice(None),)* axisA + (slice(None, None, -1),) + \
                        (slice(None),)* adiff + (slice(None, None, -1),) + \
                        (Ellipsis,)
                else:  # 270 deg
                    # Invert axes[1]
                    s = (slice(None),)* axes[1] + (slice(None, None, -1),) + \
                        (Ellipsis,)
                data = signal.data[s]
            else:
                data = signal.data
            if k % 2 == 1:     # Rotating 90 or 270
                # TODO: Swap HyperSpy axes as well!
                data = np.swapaxes(data, axes[0], axes[1])
                if not reshape:
                    # By checking for constant mode before, padding is easy
                    cval = kwargs.pop('cval', 0.0)
                    bkgr = np.ones_like(signal.data) * cval
                    fa, la = min(axes), max(axes)
                    fd, ld = np.shape(data)[fa], np.shape(data)[la]
                    crop = abs(ld - fd) // 2
                    if fd < ld:  # Expand first, crop last
                        s = (slice(None),) * fa + (slice(0, fd),) + \
                            (slice(None),) * (la - fa - 1) + \
                            (slice(crop, crop + fd),) + (Ellipsis,)
                        t = (slice(None),) * fa + (slice(crop, crop + fd),) + \
                            (Ellipsis,)
                    else:       # Crop first, expand last
                        s = (slice(None),) * fa + (slice(crop, crop + ld),) + \
                            (slice(None),) * (la - fa - 1) + \
                            (slice(0, ld),) + (Ellipsis,)
                        t = (slice(None),) * la + (slice(crop, crop + ld),) + \
                            (Ellipsis,)
                    bkgr[t] = data[s]
                    data = bkgr
        else:
            data = rotate(signal.data, angle, reshape=reshape, *args, **kwargs)
        if out is None:
            sig = signal._deepcopy_with_new_data(None)
        else:
            sig = out
            old_shape = out.data.shape
        sig.data = data
        if out is None:
            if reshape:
                sig.get_dimensions_from_data()
                diff = np.array(sig.data.shape) - signal.data.shape
                for i, ax in enumerate(sig.axes_manager._axes):
                    dx = diff[i] * 0.5 * ax.scale
                    ax.offset -= dx
            return sig
        else:
            if sig.data.shape != old_shape:
                if hasattr(out.axes_manager, 'events') and hasattr(
                        out.axes_manager.events, 'any_axis_changed'):
                    cm = out.axes_manager.events.any_axis_changed.suppress
                else:
                    cm = dummy_context_manager
                with cm():
                    out.get_dimensions_from_data()
                    diff = np.array(out.data.shape) - old_shape
                    for i, ax in enumerate(out.axes_manager._axes):
                        dx = diff[i] * 0.5 * ax.scale
                        ax.offset -= dx
                if hasattr(out.axes_manager, 'events') and hasattr(
                        out.axes_manager.events, 'any_axis_changed'):
                    out.axes_manager.events.any_axis_changed.trigger(
                        out.axes_manager)
            if hasattr(out, 'events') and hasattr(out.events, 'data_changed'):
                out.events.data_changed.trigger(out)
            return None

    def on_dialog_accept(self):
        self.settings['angle'] = self.dialog.num_angle.value()
        if self.dialog.opt_new.isChecked():
            self.settings['new_or_replace'] = 'new'
        else:
            self.settings['new_or_replace'] = 'replace'
        self.settings['reshape'] = self.dialog.chk_reshape.isChecked()
        self.settings['preview'] = self.dialog.gbo_preview.isChecked()
        self.settings['grid'] = self.dialog.chk_grid.isChecked()
        self.settings['grid_spacing'] = self.dialog.num_grid.value()
        self.dialog.deleteLater()
        self.dialog = None

    def show_rotate_dialog(self):
        signal, space, _ = self.ui.get_selected_plot()
        if space not in ("navigation", "signal"):
            return None
        self.dialog = ImageRotationDialog(signal, space, self.ui, self)
        if 'angle' in self.settings:
            self.dialog.num_angle.setValue(self.settings['angle', float])
        if 'new_or_replace' in self.settings:
            v = self.settings['new_or_replace']
            if v == 'new':
                self.dialog.opt_new.setChecked(True)
            elif v == 'replace':
                self.dialog.opt_replace.setChecked(True)
        if 'reshape' in self.settings:
            self.dialog.chk_reshape.setChecked(self.settings['reshape', bool])
        if 'preview' in self.settings:
            self.dialog.gbo_preview.setChecked(self.settings['preview', bool])
        if 'grid' in self.settings:
            self.dialog.chk_grid.setChecked(self.settings['grid', bool])
        if 'grid_spacing' in self.settings:
            self.dialog.num_grid.setValue(self.settings['grid_spacing', int])
        self.dialog.accepted.connect(self.on_dialog_accept)
        self.dialog.show()


class ImageRotationDialog(ExToolWindow):

    def __init__(self, signal, axes, parent, plugin):
        super().__init__(parent)
        self.ui = parent
        self.create_controls()
        self.accepted.connect(self.ok)
        self.rejected.connect(self.close_new)
        self.signal = signal
        self.plugin = plugin
        self.new_out = None
        self._connected_updates = False
        if isinstance(axes, str):
            axm = signal.signal.axes_manager
            if axes.startswith("nav"):
                axes = (axm._axes.index(axm.navigation_axes[0]),
                        axm._axes.index(axm.navigation_axes[1]))
            elif axes.startswith("sig"):
                axes = (axm._axes.index(axm.signal_axes[0]),
                        axm._axes.index(axm.signal_axes[1]))
        self.axes = axes
        self.setWindowTitle(tr("Rotate"))

        # TODO: TAG: Functionality check
        if not hasattr(signal.signal, 'events'):
            self.gbo_preview.setVisible(False)

        # TODO: Add dynamic rotation, e.g. one that rotates when source
        # signal's data_changed event triggers

    def connect(self):
        # TODO: Don't have to con/dis those in gbo
        self.opt_new.toggled.connect(self.close_new)
        self.num_angle.valueChanged.connect(self.update)
        self.chk_grid.toggled.connect(self.update)
        self.num_grid.valueChanged.connect(self.update)
        self.chk_reshape.toggled.connect(self.update)
        self.opt_new.toggled.connect(self.update)
        self.opt_replace.toggled.connect(self.update)

    def disconnect(self):
        self.num_angle.valueChanged.disconnect(self.update)
        self.chk_grid.toggled.disconnect(self.update)
        self.num_grid.valueChanged.disconnect(self.update)
        self.chk_reshape.toggled.disconnect(self.update)
        self.opt_new.toggled.disconnect(self.update)
        self.opt_replace.toggled.disconnect(self.update)

    def ok(self):
        # Draw figure if not already done
        # TODO: TAG: Functionality check
        if not hasattr(self.signal.signal, 'events') or \
                not self.gbo_preview.isChecked():
            self.update()
        angle = self.num_angle.value()
        reshape = self.chk_reshape.isChecked()
        self.plugin.record_code(
            r"<p>.rotate_signal({0}, reshape={1}, axes={2})".format(
                angle, reshape, self.axes))
        # Clean up event connections
        if self.new_out is not None:
            self.connect_update_plot(self.new_out.signal, disconnect=True)

    def close_new(self, value=False):
        if self.new_out is not None and not value:
            self.new_out.close()
            self.new_out = None
            self._connected_updates = False

    def set_preview(self, value):
        if not hasattr(self.signal.signal, 'events'):
            return
        if value:
            self.connect()
            self.update()
        else:
            self.disconnect()
            self.close_new()

    def _axes_in_nav(self):
        axm = self.signal.signal.axes_manager
        navidx = [axm._axes.index(ax) for ax in axm.navigation_axes]
        if self.axes[0] in navidx:
            return True
        return False

    def connect_update_plot(self, signal, disconnect=False):
        if self._connected_updates != disconnect:
            return  # Nothing to do, prevent double connections
        if self._axes_in_nav():
            f = signal._plot.navigator_plot.update
        else:
            f = signal._plot.signal_plot.update

        # TODO: TAG: Functionality check
        if hasattr(signal, 'events') and hasattr(
                signal.events, 'data_changed'):
            if disconnect:
                signal.events.data_changed.disconnect(f)
            else:
                signal.events.data_changed.connect(f, [])
        self._connected_updates = not disconnect

    def update(self):
        angle = self.num_angle.value()
        reshape = self.chk_reshape.isChecked()
        if self.opt_new.isChecked():
            if self.new_out is None:
                out = None
            else:
                out = self.new_out.signal
        elif self.opt_replace.isChecked():
            out = self.signal.signal
        else:
            return  # Indeterminate state, do nothing

        s = self.plugin.rotate_signal(angle, self.signal.signal, record=False,
                                      reshape=reshape, out=out, axes=self.axes)

        if out is None:
            s.metadata.General.title = self.signal.name + "[Rotated]"
            s.plot()
            self.connect_update_plot(s)
            if (self.gbo_preview.isChecked() and self.opt_new.isChecked() and
                                                         self.new_out is None):
                self.new_out = self.ui.lut_signalwrapper[s]
        else:
            s = out

        if self.chk_grid.isChecked() is True:
            pass    # TODO: Draw grid

    def create_controls(self):
        """
        Create UI controls.
        """
        vbox = QVBoxLayout()

        form = QFormLayout()
        self.num_angle = QDoubleSpinBox()
        self.num_angle.setValue(0.0)
        self.num_angle.setMinimum(-360)
        self.num_angle.setMaximum(360)
        form.addRow(tr("Angle:"), self.num_angle)
        vbox.addLayout(form)

        self.gbo_preview = QGroupBox(tr("Preview"))
        self.gbo_preview.setCheckable(True)
        self.gbo_preview.setChecked(False)
        gbo_vbox = QVBoxLayout()
        self.chk_grid = QCheckBox(tr("Grid"))
        self.chk_grid.setChecked(False)
        self.num_grid = QSpinBox()
        self.num_grid.setValue(4)
        self.num_grid.setMinimum(1)
        self.num_grid.setEnabled(False)
        self.chk_grid.toggled[bool].connect(self.num_grid.setEnabled)
        gbo_vbox.addWidget(self.chk_grid)
        gbo_vbox.addWidget(self.num_grid)
        self.gbo_preview.setLayout(gbo_vbox)
        vbox.addWidget(self.gbo_preview)

        self.gbo_preview.toggled[bool].connect(self.set_preview)

        self.gbo_output = QGroupBox(tr("Output"))
        self.opt_new = QRadioButton(tr("New signal"))
        self.opt_replace = QRadioButton(tr("In place"))
        self.opt_new.setChecked(True)
        gbo_vbox2 = QVBoxLayout()
        gbo_vbox2.addWidget(self.opt_new)
        gbo_vbox2.addWidget(self.opt_replace)
        self.gbo_output.setLayout(gbo_vbox2)
        vbox.addWidget(self.gbo_output)

        self.chk_reshape = QCheckBox(tr("Resize to fit"))
        self.chk_reshape.setChecked(False)
        vbox.addWidget(self.chk_reshape)

        self.btn_ok = QPushButton(tr("&OK"))
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton(tr("&Cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_ok)
        hbox.addWidget(self.btn_cancel)
        vbox.addLayout(hbox)

        vbox.addStretch(1)
        self.setLayout(vbox)
