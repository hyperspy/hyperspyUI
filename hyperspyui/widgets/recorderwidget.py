# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 15:42:09 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.recorder import Recorder
from editorwidget import EditorWidget

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
        self.ui.recorders.append(r)
        e = EditorWidget(self.ui, self.ui)
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
        
        hbox = QHBoxLayout()
        for w in [self.btn_start, self.btn_stop]:
            hbox.addWidget(w)
            
        wrap = QWidget()
        wrap.setLayout(hbox)
        height = hbox.sizeHint().height()
        wrap.setFixedHeight(height)
        self.setWidget(wrap)