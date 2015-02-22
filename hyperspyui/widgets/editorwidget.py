# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 17:55:01 2015

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import os

from pyqode.core import api
from pyqode.core import modes
from pyqode.core.widgets import TabWidget

from extendedqwidgets import ExToolWindow
import hyperspyui.plugincreator as pc

class NameCategoryPrompt(ExToolWindow):
    def __init__(self, main_window, parent=None):
        super(NameCategoryPrompt, self).__init__(parent)
        self.setWindowTitle("Plugin properties") # TODO: tr
        self.ui = main_window
        self.create_controls()


    def checks_changed(self):
        menu = self.chk_menu.isChecked()
        toolbar = self.chk_toolbar.isChecked()
        icon = self.chk_icon.isChecked()
        
        if menu or toolbar:
            self.txt_category.setEnabled(True)
        else:
            self.txt_category.setEnabled(False)
        
        self.txt_iconpath.setEnabled(icon)
        self.btn_browse_icon.setEnabled(icon)

    def browse_icon(self):
        formats = QImageReader.supportedImageFormats()
        formats = [str(f) for f in formats]
        type_filter = 'Supported formats (*.{0})'.format(' *.'.join(formats))
        type_filter += ';;All files (*.*) ;;*.' + ';;*.'.join(formats)
        path = QFileDialog.getOpenFileName(self,
                    'Pick icon', os.path.dirname(self.ui.cur_dir),  # TODO: tr
                    type_filter)
        if isinstance(path, tuple):    # Pyside returns tuple, PyQt not
            path = path[0]
        if path is None:
            return
        self.txt_iconpath.setText(path)

    def create_controls(self):
        self.txt_name = QLineEdit()
        self.chk_menu = QCheckBox("Menu entry") # TODO: tr
        self.chk_menu.setChecked(True)
        self.chk_toolbar = QCheckBox("Toolbar button") # TODO: tr
        self.chk_toolbar.setChecked(True)
        self.txt_category = QLineEdit()
        self.chk_icon = QCheckBox()
        self.chk_toolbar.setChecked(False)
        self.txt_iconpath = QLineEdit()
        self.btn_browse_icon = QPushButton("...")
        self.txt_iconpath.setEnabled(False)
        self.btn_browse_icon.setEnabled(False)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                Qt.Horizontal)
        
        self.chk_menu.toggled.connect(self.checks_changed)
        self.chk_toolbar.toggled.connect(self.checks_changed)
        self.chk_icon.toggled.connect(self.checks_changed)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        
        hbox = QHBoxLayout()
        for w in [self.chk_icon, self.txt_iconpath, self.btn_browse_icon]:
            hbox.addWidget(w)
        
        form = QFormLayout()
        form.addRow("Name", self.txt_name)
        form.addRow(self.chk_menu, self.chk_toolbar)
        form.addRow("Category", self.txt_category)
        form.addRow("Icon", hbox)
        
        vbox = QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(btns)
        
        self.setLayout(vbox)
        
        

class EditorWidget(ExToolWindow):
    code_title = "Code Editor" # TODO: tr
    plugin_title = "Plugin Editor" # TODO: tr
    
    def __init__(self, main_window, parent=None, path=None):
        super(EditorWidget, self).__init__(parent)
        self.setWindowTitle(self.code_title)
        self.ui = main_window
        self._is_plugin = False
        
        self.create_controls(path)
        
    @property
    def is_plugin(self):
        return self._is_plugin
    
    @is_plugin.setter
    def is_plugin(self, value):
        if self._is_plugin != value:
            self._is_plugin = value
            self.btn_make_plugin.setVisible(not value)
            self.btn_run.setVisible(not value)
            self.btn_reg_plugin.setVisible(value)
            if value:
                self.setWindowTitle(self.plugin_title)
            else:
                self.setWindowTitle(self.code_title)

    def append_code(self, code):
        text = self.editor.toPlainText()
        if len(text) > 0 and text[-1] == '\n':
            prev_cursor = self.editor.textCursor()
            self.editor.moveCursor(QTextCursor.End)
            self.editor.insertPlainText(code)
            self.editor.setTextCursor(prev_cursor)
        else:
            self.editor.appendPlainText(code)
    
    def make_plugin(self):
        diag = NameCategoryPrompt(self.ui, self)
        dr = diag.exec_()
        if dr == QDialog.Accepted:
            if diag.chk_icon.isChecked():
                icon = diag.txt_iconpath.text()
            else:
                icon = None
            code = "ui = self.ui\n"
            code += "siglist = ui.signals\n"
            code += self.editor.toPlainText().rstrip()
            
            name = diag.txt_name.text()
            code = pc.create_plugin_code(code, 
                                  name,
                                  diag.txt_category.text(),
                                  diag.chk_menu.isChecked(),
                                  diag.chk_toolbar.isChecked(),
                                  icon)
            path = os.path.normpath(os.path.dirname(__file__) + 
                                        '/../plugins/' + name.lower() + '.py')
            e = EditorWidget(self.ui, self.ui, path)
            e.append_code(code)
            self.ui.editors.append(e)   # We have to keep an instance!
            e.finished.connect(lambda: self.ui.editors.remove(e))
            e.is_plugin = True
            e.show()
    
    def register_plugin(self):
        dr = self.save()
        path = self.editor.file.path
        if dr and os.path.exists(path):
            self.ui.plugin_manager.load_from_file(path)
    
    def save(self):
        if not os.path.exists(self.editor.file.path):
            path = QFileDialog.getSaveFileName(self, 'Choose destination path',
                                        self.editor.file.path)[0]
            if not path:
                return False
            self.editor.file._path = path
            open(path, 'w').close() # Touch file so save_current works
        return self.tab.save_current()
    
    def read(self, filename=None):
        pass
    
    def run(self):
        code = self.editor.toPlainText()
        self.ui.console.ex(code)
    
    def create_controls(self, path):
        editor = api.CodeEdit()
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
        editor.modes.append(modes.AutoCompleteMode())
        if path is not None:
            editor.file._path = path
        self.editor = editor
        self.tab = TabWidget(self)
        if path is None:
            self.tab.add_code_edit(editor, "untitled%d.py")
        else:
            self.tab.add_code_edit(editor)

        self.btn_save = QPushButton("Save") # TODO: tr()
        self.btn_open = QPushButton("Open") # TODO: tr()
        self.btn_run = QPushButton("Run") # TODO: tr()
        self.btn_make_plugin = QPushButton("Make Plugin")    # TODO: tr()
        self.btn_reg_plugin = QPushButton("Register Plugin")    # TODO: tr()
        self.btn_reg_plugin.setVisible(False)
        
        self.btn_save.clicked.connect(self.save)
        self.btn_open.clicked.connect(self.read)
        self.btn_run.clicked.connect(self.run)
        self.btn_make_plugin.clicked.connect(self.make_plugin)
        self.btn_reg_plugin.clicked.connect(self.register_plugin)
        
        self.hbox = QHBoxLayout()
        for w in [self.btn_save, self.btn_open, self.btn_run, 
                  self.btn_make_plugin, self.btn_reg_plugin]:
            self.hbox.addWidget(w)
        
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.tab)
        vbox.addLayout(self.hbox)
        
        self.setLayout(vbox)
    