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
Created on Sat Dec 27 14:21:00 2014

@author: Vidar Tonaas Fauske
"""

from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QMessageBox

from hyperspyui.widgets.extendedqwidgets import ExRememberPrompt


class Settings:

    def __init__(self, parent=None, group=None):
        self._sep = '/'
        self.group = group
        self.parent = parent

    def _get_groups(self, key):
        if self.group is None:
            return key.split(self._sep)
        else:
            return (self.group + self._sep + key).split(self._sep)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key, t = key
        else:
            t = None
        groupings = self._get_groups(key)
        if key not in self:
            groupings.insert(0, 'defaults')
        key = groupings.pop()
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        ret = settings.value(key)
        if t and isinstance(t, type) and not isinstance(ret, t):
            if t is bool:
                ret = ("true" == ret.lower())
            else:
                ret = t(ret)
        for _ in groupings:
            settings.endGroup()
        return ret

    def __setitem__(self, key, value):
        groupings = self._get_groups(key)
        key = groupings.pop()
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        settings.setValue(key, value)
        for _ in groupings:
            settings.endGroup()

    def __contains__(self, key):
        groupings = self._get_groups(key)
        key = groupings.pop()
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        r = settings.contains(key)
        for _ in groupings:
            settings.endGroup()
        return r

    def __iter__(self):
        settings = QSettings(parent=self.parent)
        settings.beginGroup(self.group)
        keys = settings.allKeys()
        for k in keys:
            yield k, settings.value(k)

    @staticmethod
    def clear_defaults():
        """
        Clear all settings in defaults group. Should only be run once during
        application start, as it will undo any defaults that have been set.
        """
        settings = QSettings()
        settings.beginGroup('defaults')
        settings.remove("")
        settings.endGroup()

    @staticmethod
    def restore_from_defaults():
        """
        Clears all settings (except "defaults" group) and restores all settings
        from the defaults group.
        """
        settings = QSettings()
        for g in settings.childGroups():
            if g != "defaults":
                settings.remove(g)
        for k in settings.childKeys():
            settings.remove(k)
        defaults = QSettings()
        defaults.beginGroup("defaults")
        for k in defaults.allKeys():
            settings.setValue(k, defaults.value(k))

    def restore_key_default(self, key):
        """
        Restore a given setting to its default value.
        """
        groupings = self._get_groups(key)
        groupings.insert(0, 'defaults')
        inner_key = groupings.pop()
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        default_value = settings.value(inner_key)
        for _ in groupings:
            settings.endGroup()
        self[key] = default_value

    def set_default(self, key, value):
        """
        Sets default value by writing into defaults group.
        """
        # If not in normal settings, set it:
        if key not in self:
            self[key] = value

        # Either way, write to defaults group
        groupings = self._get_groups(key)
        groupings.insert(0, 'defaults')
        key = groupings.pop()
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        settings.setValue(key, value)
        for _ in groupings:
            settings.endGroup()

    def set_enum_hint(self, key, options):
        """
        Indicate possible values for a setting.

        The `options` are not strictly enforced, but can be used to indicate
        valid values to the user. A typical usecase is to allow the use of a
        combobox in a dialog to pick a value.
        """
        groupings = self._get_groups(key)
        groupings.insert(0, 'defaults')
        key = groupings.pop()
        key = '_' + key + '_options'    # Change key to avoid conflicts
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        if not isinstance(options, list):
            options = list(options)
        settings.setValue(key, options)
        for _ in groupings:
            settings.endGroup()

    def get_enum_hint(self, key):
        """
        Returns the possible enum hint values if set, otherwise None.
        """
        groupings = self._get_groups(key)
        groupings.insert(0, 'defaults')
        key = groupings.pop()
        key = '_' + key + '_options'    # Change key to avoid conflicts
        settings = QSettings(parent=self.parent)
        for g in groupings:
            settings.beginGroup(g)
        value = settings.value(key)
        for _ in groupings:
            settings.endGroup()
        return value

    def get_or_prompt(self, key, options, title="Prompt", descr=""):
        """
        Gets the setting specified by key. If it is not set, prompts the user
        to select one option out of several. The prompt includes a checkbox to
        remember the answer ("Remember this setting").

        The option parameter should be a list of two-tuples, specifying an
        ordered list of option values, and labels.
        """

        # First check if we have a remembered setting.
        val = self[key]
        if val is not None:
            return val

        # Setup the dialog
        mb = ExRememberPrompt(QMessageBox.Question, title, descr)
        if len(options) < 5:
            buttons = []
            opt = options[0]
            buttons.append(mb.addButton(opt[1], QMessageBox.AcceptRole))
            for opt in options[1:]:
                buttons.append(mb.addButton(opt[1], QMessageBox.RejectRole))
        else:
            pass  # TODO: Make list selection
        mb.addButton(QMessageBox.Cancel)

        # Show the dialog modal/blocking
        mb.exec_()
        btn = mb.clickedButton()
        if btn not in buttons:
            # The user did not make a valid selection = cancelled
            return None
        sel = btn.text()
        idx = [o[1] for o in options].index(sel)
        ret = options[idx][0]
        if mb.isChecked():
            self[key] = ret
        return ret

    def write(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)

        for k, v in d.items():
            settings.setValue(k, v)

        if group is not None:
            settings.endGroup()

    def read(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)

        for k, v in d.items():
            if isinstance(v, tuple):
                settings.value(k, v)

        if group is not None:
            settings.endGroup()
