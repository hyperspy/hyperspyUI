# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 18:46:40 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.recorder import Recorder
from hyperspyui.widgets.editorwidget import EditorWidget

class RecorderWidget(QDockWidget):
    def __init__(self, main_window, parent=None):
        super(RecorderWidget, self).__init__(parent)
        self.setWindowTitle("Recorder") # TODO: tr
        self.ui = main_window
        self.create_controls()
    
    def start_recording(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        r = Recorder()
        self.recorder = r
        self.update_filter()
        self.ui.recorders.append(r)
        e = EditorWidget(self.ui, self.ui)
        e.setWindowTitle("Recorded Code")   # TODO: tr
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
        self.btn_start = QPushButton("Start") # TODO: tr
        self.btn_stop = QPushButton("Stop") # TODO: tr
        self.btn_stop.setEnabled(False)
        
        self.btn_start.clicked.connect(self.start_recording)
        self.btn_stop.clicked.connect(self.stop_recording)
        
        self.chk_actions = QCheckBox("Actions") # TODO: tr
        self.chk_code = QCheckBox("Code")       # TODO: tr
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
        self.add_widget( RecorderWidget(self.ui, self.ui) )