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
from skimage.filters import gaussian
from hyperspyui.util import win2sig
from hyperspyui.widgets.extendedqwidgets import ExToolWindow

from qtpy import QtGui, QtCore


def tr(text):
    return QtCore.QCoreApplication.translate("GaussianFilter", text)


class GaussianFilter(Plugin):
    name = "Gaussian Filter"

    def __init__(self, ui):
        super().__init__(ui)
        self.settings.set_default('sigma', 1.0)

    def create_actions(self):
        self.add_action(
            self.name + '.show_dialog', self.name, self.show_dialog,
            icon="gaussian_bare.svg",
            tip="Apply a gaussian filter",
            selection_callback=self.selection_rules)

    def create_menu(self):
        self.add_menuitem('Image', self.ui.actions[self.name + '.show_dialog'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'Image', self.ui.actions[
                self.name + '.show_dialog'])

    def selection_rules(self, win, action):
        """
        Callback to determine if filter is valid for the passed window.
        """
        s = win2sig(win, self.ui.signals)
        ok = False
        if s is not None:
            if win == s.signal_plot and \
                    s.signal.axes_manager.signal_dimension == 2:
                ok = True
        if ok:
            action.setEnabled(True)
        else:
            action.setEnabled(False)

    def gaussian(self, sigma, signal=None, out=None, record=True,
                 *args, **kwargs):
        """
        Apply a gaussian smoothing filter to an image signal.
        Uses py:func:`skimage.filters.gaussian` for the actual processing.

        Parameters
        ----------
        sigma : {float}
            Smoothing factor in units of pixels, i.e a value around 1 is
            a slight smoothing.
        signal : {Signal | None}
            Signal to operate on. If not, it will use the currently
            selected one
        out : {Signal | None}
            Output signal
        record : {bool}
            Whether the operation should be recorded or not.
        **kwargs : dict
            Other keyword arguments are passed to
            py:func:`skimage.filters.gaussian`.
        """
        if signal is None:
            signal, axes, _ = self.ui.get_selected_plot()
            signal = signal.signal
            if isinstance(axes, str):
                axm = signal.axes_manager
                if axes.startswith("nav"):
                    axes = (axm._axes.index(axm.navigation_axes[0]),
                            axm._axes.index(axm.navigation_axes[1]))
                elif axes.startswith("sig"):
                    axes = (axm._axes.index(axm.signal_axes[0]),
                            axm._axes.index(axm.signal_axes[1]))

        s_out = out or signal.deepcopy()
        if out is None and not np.issubdtype(s_out.data.dtype, float):
            s_out.change_dtype(float)
        if np.issubdtype(signal.data.dtype, float):
            vmin, vmax = np.nanmin(signal.data), np.nanmax(signal.data)
        else:
            vmin, vmax = (None, None)
        for im_o, im_i in zip(s_out._iterate_signal(),
                              signal._iterate_signal()):
            if vmin is None:
                im_o[:] = gaussian(im_i, sigma, *args, **kwargs)
            else:
                im_o[:] = gaussian((im_i-vmin)/(vmax-vmin), sigma, *args, **kwargs)
        if vmin is not None:
            s_out.data[:] = (vmax-vmin)*s_out.data + vmin

        if out is None:
            if record:
                self.record_code(r"<p>.gaussian({0}, {1}, {2})".format(
                        sigma, args, kwargs))
            return s_out
        else:
            if record:
                self.record_code(
                    r"<p>.gaussian({0}, out={1}, {2}, {3})".format(
                        sigma, out, args, kwargs))
            if hasattr(out, 'events') and hasattr(out.events, 'data_changed'):
                out.events.data_changed.trigger(out)
            return None

    def on_dialog_accept(self, dialog):
        self.settings['sigma'] = dialog.num_sigma.value()

    def show_dialog(self):
        signal, space, _ = self.ui.get_selected_plot()
        if space != "signal":
            return None
        dialog = GaussianFilterDialog(signal, self.ui, self)
        if 'sigma' in self.settings:
            dialog.num_sigma.setValue(float(self.settings['sigma']))
        dialog.accepted.connect(lambda: self.on_dialog_accept(dialog))
        self.open_dialog(dialog)


class GaussianFilterDialog(ExToolWindow):

    def __init__(self, signal, parent, plugin):
        super().__init__(parent)
        self.ui = parent
        self.create_controls()
        self.accepted.connect(self.ok)
        self.rejected.connect(self.undo)
        self.signal = signal
        self.plugin = plugin
        self.new_out = None
        self._connected_updates = False
        self.setWindowTitle(tr("Gaussian Filter"))

        # TODO: TAG: Functionality check
        if not hasattr(signal.signal, 'events'):
            self.chk_preview.setVisible(False)

    def connect(self):
        self.opt_new.toggled.connect(self.close_new)
        self.num_sigma.valueChanged.connect(self.update)
        self.opt_new.toggled.connect(self.update)
        self.opt_replace.toggled.connect(self.update)

    def disconnect(self):
        self.opt_new.toggled.disconnect(self.close_new)
        self.num_sigma.valueChanged.disconnect(self.update)
        self.opt_new.toggled.disconnect(self.update)
        self.opt_replace.toggled.disconnect(self.update)

    def ok(self):
        # Draw figure if not already done
        # TODO: TAG: Functionality check
        if not hasattr(self.signal.signal, 'events') or \
                not self.chk_preview.isChecked():
            self.update()
        sigma = self.num_sigma.value()
        self.plugin.record_code(r"<p>.gaussian({0})".format(sigma))

    def undo(self):
        self.close_new()
        self.set_preview

    def close_new(self, value=False):
        if self.new_out is not None and not value:
            self.new_out.close()
            self.new_out = None

    def set_preview(self, value):
        if not hasattr(self.signal.signal, 'events'):
            return
        if value:
            self.connect()
            self.update()
        else:
            self.disconnect()
            self.close_new()

    def update(self):
        sigma = self.num_sigma.value()
        if self.opt_new.isChecked():
            if self.new_out is None:
                out = None
            else:
                out = self.new_out.signal
        elif self.opt_replace.isChecked():
            out = self.signal.signal
        else:
            return  # Indeterminate state, do nothing

        s = self.plugin.gaussian(sigma, self.signal.signal,
                                 record=False, out=out)

        if out is None:
            s.metadata.General.title = self.signal.name + "[GaussianFilter]"
            s.plot()
            if (self.chk_preview.isChecked() and self.opt_new.isChecked() and
                    self.new_out is None):
                self.new_out = self.ui.lut_signalwrapper[s]

    def create_controls(self):
        """
        Create UI controls.
        """
        vbox = QtGui.QVBoxLayout()

        form = QtGui.QFormLayout()
        self.num_sigma = QtGui.QDoubleSpinBox()
        self.num_sigma.setValue(1.0)
        self.num_sigma.setMinimum(0.0)
        self.num_sigma.setSingleStep(0.1)
        self.num_sigma.setMaximum(1e3)
        self.num_sigma.setDecimals(2)
        form.addRow(tr("Sigma:"), self.num_sigma)
        vbox.addLayout(form)

        self.chk_preview = QtGui.QCheckBox(tr("Preview"))
        self.chk_preview.setCheckable(True)
        self.chk_preview.setChecked(False)
        vbox.addWidget(self.chk_preview)

        self.chk_preview.toggled[bool].connect(self.set_preview)

        self.gbo_output = QtGui.QGroupBox(tr("Output"))
        self.opt_new = QtGui.QRadioButton(tr("New signal"))
        self.opt_replace = QtGui.QRadioButton(tr("In place"))
        self.opt_new.setChecked(True)
        gbo_vbox2 = QtGui.QVBoxLayout()
        gbo_vbox2.addWidget(self.opt_new)
        gbo_vbox2.addWidget(self.opt_replace)
        self.gbo_output.setLayout(gbo_vbox2)
        vbox.addWidget(self.gbo_output)

        self.btn_ok = QtGui.QPushButton(tr("&OK"))
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QtGui.QPushButton(tr("&Cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_ok)
        hbox.addWidget(self.btn_cancel)
        vbox.addLayout(hbox)

        vbox.addStretch(1)
        self.setLayout(vbox)
