# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 18:26:38 2015

@author: Vidar Tonaas Fauske
"""

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
    
#    def _on_setting_changed(self, key)
        
    def _create_group_widget(self, settings, group):
        wrap = QWidget(self)
        form = QFormLayout()
        settings.beginGroup(group)
        for k in settings.allKeys():
            v = settings.value(k)
            label = k.capitalize().replace('_', ' ')
            if isinstance(v, basestring):
                if v.lower() in ('true', 'false'):
                    w = QCheckBox()
                    w.setChecked(v.lower() == 'true')
#                    w.toggled.connect
                else:
                    w = QLineEdit(v)
            elif isinstance(v, int):
                w = QSpinBox()
                w.setValue(v)
            elif isinstance(v, float):
                w = QDoubleSpinBox()
                w.setValue(v)
            else:
                w = QLineEdit(str(v))
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
