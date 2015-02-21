# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 17:55:01 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from pyqode.core import api
from pyqode.core import modes
from pyqode.core.widgets import TabWidget

from extendedqwidgets import ExToolWindow
import hyperspyui.plugin_creator as pc

class NameCategoryPrompt(QWidget):
    def __init__(self, parent=None):
        super(NameCategoryPrompt, self).__init__(parent)
        self.create_controls()
        
    def create_controls(self):
        

class EditorWidget(ExToolWindow):
    def __init__(self, main_window, parent=None):
        super(EditorWidget, self).__init__(parent)
        self.setWindowTitle("Code Editor") # TODO: tr
        self.filename = None
        self.ui = main_window
        
        self.create_controls()

    def append_code(self, code):
        self.editor.appendPlainText(code)
    
    def make_plugin(self):
        e = EditorWidget(self.ui, self.ui)
        pc.create_plugin_code(self.editor.toPlainText())
    
    def read(self, filename=None):
        self.filename = filename
    
    def create_controls(self):
        
        editor = api.CodeEdit()
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
        editor.modes.append(modes.AutoCompleteMode())
        self.editor = editor
        self.tab = TabWidget()
        self.tab.add_code_edit(editor)

        self.btn_save = QPushButton("Save") # TODO: tr()
        self.btn_open = QPushButton("Open") # TODO: tr()
        self.btn_plugin = QPushButton("Make Plugin")    # TODO: tr()
        
        self.btn_save.clicked.connect(self.tab.save_current)
        self.btn_open.clicked.connect(self.read)
        self.btn_plugin.clicked.connect(self.make_plugin)
        
        hbox = QHBoxLayout(self)
        for w in [self.btn_save, self.btn_open, self.btn_plugin]:
            hbox.addWidget(w)
        
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.tab)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
    