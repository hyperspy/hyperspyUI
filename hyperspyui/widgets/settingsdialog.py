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
Created on Sun Mar 01 18:26:38 2015

@author: Vidar Tonaas Fauske
"""

from functools import partial

from qtpy import QtCore
from qtpy.QtCore import QSettings
from qtpy.QtWidgets import (QDialogButtonBox, QVBoxLayout, QLineEdit, QWidget,
                            QCheckBox, QDoubleSpinBox, QSpinBox, QComboBox,
                            QMessageBox, QAbstractButton,
                            QTabWidget, QFormLayout)

from .extendedqwidgets import ExToolWindow
from hyperspyui.settings import Settings

import numpy as np


def tr(text):
    return QtCore.QCoreApplication.translate("PluginManagerWidget", text)


class SettingsDialog(ExToolWindow):
    settings_changed = QtCore.Signal(dict)

    def __init__(self, main_window, parent=None):
        """
        Create a dialog for editing the application settings, including the
        settings for plugins.
        """
        super().__init__(parent)

        self.setWindowTitle(tr("Settings"))
        self.ui = main_window
        self._initial_values = {}
        self._changes = {}
        self._lut = {}
        self.create_controls()

    @property
    def apply_btn(self):
        """
        The apply button.
        """
        return self._btns.button(QDialogButtonBox.Apply)

    def _on_setting_changed(self, key, widget, *pysideargs):
        """
        Callback when the value of a settings editor widget has changed.
        """
        # First, extract value from widget (depends on widget type)
        if isinstance(widget, QLineEdit):
            v = widget.text()
        elif isinstance(widget, QCheckBox):
            if widget.isTristate() and \
                    widget.checkState() == QtCore.Qt.PartiallyChecked:
                v = None
            else:
                v = "true" if widget.isChecked() else "false"
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            v = widget.value()
        elif isinstance(widget, QComboBox):
            v = widget.currentText()

        # Compare to initial value:
        if v == self._initial_values[key]:
            # If the same, remove from self._changes
            del self._changes[key]
            if len(self._changes) < 1:
                # If no changes, disable apply button (nothing to apply)
                self.apply_btn.setEnabled(False)
        else:
            # If different, store in self._changes and enable apply button
            self._changes[key] = v
            self.apply_btn.setEnabled(True)

    def apply_changes(self):
        """
        Applies changes performed since dialog creation or last apply,
        whichever is most recent. Fires settings_changed Signal as long as
        there has been any changes.
        """
        if len(self._changes) < 1:
            return
        s = QSettings(self.ui)
        for k, v in self._changes.items():
            if k in self._initial_values:   # Avoid readding removed settings
                s.setValue(k, v)
                self._initial_values[k] = v
        self.settings_changed.emit(self._changes)
        self._changes.clear()
        self.apply_btn.setEnabled(False)

    def _create_settings_widgets(self, settings):
        """
        Create a widget for a settings instance, containing label/editor pairs
        for each setting in the current level of the passed QSettings instance.
        The key of the setting is used as the label, but it's capitalized and
        underscores are replaced by spaces.
        """
        wrap = QWidget(self)
        form = QFormLayout()
        hint_lookup = Settings()
        for k in settings.allKeys():
            if k.startswith("_"):
                continue                                # Ignore hidden keys
            v = settings.value(k)                       # Read value
            label = k.capitalize().replace('_', ' ')
            abs_key = settings.group() + '/' + k
            self._initial_values[abs_key] = v           # Store initial value
            hints = hint_lookup.get_enum_hint(abs_key)  # Check for enum hints
            # Create a fitting editor widget based on value type:
            if hints is not None:
                w = QComboBox()
                w.addItems(hints)
                w.setEditable(True)
                w.setEditText(v)
                w.editTextChanged.connect(partial(self._on_setting_changed,
                                                  abs_key, w))
            elif isinstance(v, str):
                if v.lower() in ('true', 'false'):
                    w = QCheckBox()
                    w.setChecked(v.lower() == 'true')
                    w.toggled.connect(partial(self._on_setting_changed,
                                              abs_key, w))
                else:
                    w = QLineEdit(v)
                    w.textChanged.connect(partial(self._on_setting_changed,
                                                  abs_key, w))
            elif isinstance(v, int):
                w = QSpinBox()
                w.setRange(np.iinfo(np.int32).min, np.iinfo(np.int32).max)
                w.setValue(v)
                w.valueChanged.connect(partial(self._on_setting_changed,
                                               abs_key, w))
            elif isinstance(v, float):
                w = QDoubleSpinBox()
                w.setRange(np.finfo(np.float32).min, np.finfo(np.float32).max)
                w.setValue(v)
                w.valueChanged.connect(partial(self._on_setting_changed,
                                               abs_key, w))
            else:
                w = QLineEdit(str(v))
                w.textChanged.connect(partial(self._on_setting_changed,
                                              abs_key, w))
            self._lut[abs_key] = w
            form.addRow(label, w)
        wrap.setLayout(form)
        return wrap

    def _add_groups(self, settings):
        """
        Add all child groups in settings as a separate tab, with editor widgets
        to change the values of each setting within those groups.

        Treats the groups 'PluginManager' and 'plugins' specially: The former
        is ignored in its entirety, the latter is called recursively so that
        each plugin gets its own tab.
        """
        for group in settings.childGroups():
            if group in ('defaults', 'PluginManager'):
                continue
            elif group == 'plugins':
                settings.beginGroup(group)
                self._add_groups(settings)
                settings.endGroup()
                continue
            settings.beginGroup(group)
            tab = self._create_settings_widgets(settings)
            settings.endGroup()
            if group.lower() == 'general':
                self.general_tab = tab
                self.tabs.insertTab(0, tab, tr("General"))
            else:
                self.tabs.addTab(tab, group)

    def _on_accept(self):
        """
        Callback when dialog is closed by OK-button.
        """
        self.apply_changes()
        self.accept()

    def _on_reset(self):
        """
        Callback for reset button. Prompts user for confirmation, then proceeds
        to reset settings to default values if confirmed, before updating
        controls and applying any changes (emits change signal if any changes).
        """
        mb = QMessageBox(QMessageBox.Warning,
                         tr("Reset all settings"),
                         tr("This will reset all settings to their default " +
                            "values. Are you sure you want to continue?"),
                         QMessageBox.Yes | QMessageBox.No)
        mb.setDefaultButton(QMessageBox.No)
        dr = mb.exec_()
        if dr == QMessageBox.Yes:
            # This clears all settings, and recreates only those values
            # initialized with set_default this session.
            Settings.restore_from_defaults()

            # Now we update controls:
            s = QSettings(self.ui)
            keys = list(self._initial_values.keys())  # Use copy, as we may modify
            for k in keys:
                # Check if setting is still present
                if s.contains(k):
                    # Present, update to new value (triggers _on_change)
                    v = s.value(k)
                    w = self._lut[k]
                    if isinstance(w, QLineEdit):
                        w.setText(v)
                    elif isinstance(w, QCheckBox):
                        w.setChecked(v.lower() == "true")
                    elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                        w.setValue(v)
                else:
                    # Setting was removed, remove editor
                    w = self._lut[k]
                    layout = w.parent().layout()
                    label = layout.labelForField(w)
                    layout.removeWidget(w)
                    w.close()
                    if label is not None:
                        layout.removeWidget(label)
                        label.close()
                    del self._lut[k]
                    del self._initial_values[k]
                    self._changes[k] = None
                    # Check whether all editors for tab was removed
                    if layout.count() == 0:
                        wrap = w.parent()
                        self.tabs.removeTab(self.tabs.indexOf(wrap))
            # Finally apply changes (update _initial_values, and emit signal)
            self.apply_changes()

    def _on_click(self, button):
        """
        Route button clicks to appropriate handler.
        """
        if button == self.apply_btn:
            self.apply_changes()
        elif button == self._btns.button(QDialogButtonBox.Reset):
            self._on_reset()

    def create_controls(self):
        """
        Create UI controls.
        """
        self.tabs = QTabWidget(self)

        # Fill in tabs by setting groups
        s = QSettings(self.ui)
        self._add_groups(s)

        # Add button bar at end
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Apply |
                                QDialogButtonBox.Cancel |
                                QDialogButtonBox.Reset,
                                QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        btns.clicked[QAbstractButton].connect(self._on_click)
        self._btns = btns
        self.apply_btn.setEnabled(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addWidget(btns)

        self.setLayout(vbox)
