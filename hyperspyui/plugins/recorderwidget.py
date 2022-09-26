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
Created on Sun Feb 22 18:46:40 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                            QCheckBox)

from hyperspyui.recorder import Recorder
from hyperspyui.widgets.editorwidget import EditorWidget


def tr(text):
    return QtCore.QCoreApplication.translate("RecorderWidget", text)


class RecorderWidget(QtWidgets.QDockWidget):

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Recorder"))
        self.ui = main_window
        self.create_controls()
        self.recorder = None

    def start_recording(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        r = Recorder()
        self.recorder = r
        self.update_filter()
        self.ui.recorders.append(r)
        e = EditorWidget(self.ui, self.ui)
        e.setWindowTitle(tr("Recorded Code"))
        self.editor = e
        self.ui.editors.append(e)
        r.record.connect(e.append_code)
        self.editor.finished.connect(lambda: self.ui.editors.remove(e))
        self.editor.finished.connect(lambda: self.disconnect_editor(e))
        e.show()

    def stop_recording(self, disconnect=True):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.ui.recorders.remove(self.recorder)
        if disconnect:
            self.disconnect_editor()
        self.recorder = None
        self.editor = None

    def update_filter(self):
        if self.recorder is None:
            return
        self.recorder.filter['actions'] = self.chk_actions.isChecked()
        self.recorder.filter['code'] = self.chk_code.isChecked()

    def disconnect_editor(self, editor=None):
        if editor is None:
            editor = self.editor
        else:
            if self.editor != editor:
                return
            self.stop_recording(disconnect=False)
        if self.recorder is not None:
            self.recorder.record.disconnect(editor.append_code)

    def create_controls(self):
        self.btn_start = QPushButton(tr("Start"))
        self.btn_stop = QPushButton(tr("Stop"))
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(self.start_recording)
        self.btn_stop.clicked.connect(self.stop_recording)

        self.chk_actions = QCheckBox(tr("Actions"))
        self.chk_code = QCheckBox(tr("Code"))
        for c in [self.chk_actions, self.chk_code]:
            c.setChecked(True)
            c.toggled.connect(self.update_filter)

        hbox = QHBoxLayout()
        for w in [self.btn_start, self.btn_stop]:
            hbox.addWidget(w)
        hbox2 = QHBoxLayout()
        for w in [self.chk_actions, self.chk_code]:
            hbox2.addWidget(w)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        wrap = QWidget()
        wrap.setLayout(vbox)
        height = vbox.sizeHint().height()
        wrap.setFixedHeight(height)
        self.setWidget(wrap)


class RecorderWidgetPlugin(Plugin):
    name = "Recorder Widget"

    def create_widgets(self):
        self.add_widget(RecorderWidget(self.ui, self.ui))
