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


def settings_to_controls(settings):


class PluginManagerWidget(ExToolWindow):

    def __init__(self, main_window, parent=None):
        super(PluginManagerWidget, self).__init__(parent)

        self.setWindowTitle(tr("Settings"))
        self.ui = main_window
        self.create_controls()

    def create_controls(self):
        self.tabs = QTabWidget(self)

        self.general_tab = QWidget(self)
        form = QFormLayout()
