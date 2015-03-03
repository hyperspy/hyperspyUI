# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 18:26:38 2015

@author: Vidar Tonaas Fauske
"""

from functools import partial

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from extendedqwidgets import ExToolWindow


def tr(text):
    return QCoreApplication.translate("PluginManagerWidget", text)


class SettingsDialog(ExToolWindow):

    def __init__(self, main_window, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.setWindowTitle(tr("Settings"))
        self.ui = main_window
        self.create_controls()

    def _on_setting_changed(self, key, widget):
        # TODO: Maybe drop on_change and use OK/Apply/Cancel instead?
        s = QSettings(self.ui)
        if isinstance(widget, QLineEdit):
            v = widget.text()
        elif isinstance(widget, QCheckBox):
            if widget.isTristate() and \
                    widget.checkState() == Qt.PartiallyChecked:
                v = None
            else:
                v = widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            v = widget.value()

        # TODO: Ugly hack, use signals for changes instead!
        if key == 'mainwindow/toolbar_button_size':
            self.ui.toolbar_button_size = v
        else:
            s.setValue(key, v)

    def _create_group_widget(self, settings, group):
        wrap = QWidget(self)
        form = QFormLayout()
        settings.beginGroup(group)
        for k in settings.allKeys():
            v = settings.value(k)
            label = k.capitalize().replace('_', ' ')
            abs_key = settings.group() + '/' + k
            if isinstance(v, basestring):
                if v.lower() in ('true', 'false'):
                    w = QCheckBox()
                    w.setChecked(v.lower() == 'true')
                    w.clicked.connect(partial(self._on_setting_changed,
                                              abs_key, w))
                else:
                    w = QLineEdit(v)
                    w.textChanged.connect(partial(self._on_setting_changed,
                                                  abs_key, w))
            elif isinstance(v, int):
                w = QSpinBox()
                w.setValue(v)
                w.valueChanged.connect(partial(self._on_setting_changed,
                                               abs_key, w))
            elif isinstance(v, float):
                w = QDoubleSpinBox()
                w.setValue(v)
                w.valueChanged.connect(partial(self._on_setting_changed,
                                               abs_key, w))
            else:
                w = QLineEdit(str(v))
                w.textChanged.connect(partial(self._on_setting_changed,
                                              abs_key, w))
            form.addRow(label, w)
        settings.endGroup()
        wrap.setLayout(form)
        return wrap

    def _add_groups(self, settings):
        for group in settings.childGroups():
            if group == 'PluginManager':
                continue
            elif group == 'plugins':
                settings.beginGroup(group)
                self._add_groups(settings)
                settings.endGroup()
                continue
            tab = self._create_group_widget(settings, group)
            if group == 'mainwindow':
                self.general_tab = tab
                self.tabs.insertTab(0, tab, tr("General"))
            else:
                self.tabs.addTab(tab, group)

    def create_controls(self):
        self.tabs = QTabWidget(self)

        s = QSettings(self.ui)
        self._add_groups(s)
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)
