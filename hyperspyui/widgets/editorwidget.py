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
Created on Sat Feb 21 17:55:01 2015

@author: Vidar Tonaas Fauske
"""

from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtWidgets import (QDialogButtonBox, QCheckBox, QLineEdit,
                            QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout,
                            )

import os

from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.widgets import TabWidget
from . import _editor_server as server
from pyqode.python import modes as pymodes
from pyqode.python.backend.workers import run_pyflakes, calltips

from .extendedqwidgets import ExToolWindow
import hyperspyui.plugincreator as pc


def tr(text):
    return QtCore.QCoreApplication.translate("EditorWidget", text)


class NameCategoryPrompt(ExToolWindow):

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Plugin properties"))
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
        formats = QtGui.QImageReader.supportedImageFormats()
        formats = [str(f, encoding='ascii') for f in formats]
        # Add one filter that takes all supported:
        type_filter = tr("Supported formats")
        type_filter += ' (*.{0})'.format(' *.'.join(formats))
        # Add all as individual options
        type_filter += ';;' + tr("All files") + \
            ' (*.*) ;;*.' + ';;*.'.join(formats)
        path = QtWidgets.QFileDialog.getOpenFileName(self,
            tr("Pick icon"),
            os.path.dirname(self.ui.cur_dir),
            type_filter)
        if isinstance(path, tuple):    # Pyside returns tuple, PyQt not
            path = path[0]
        if path is None:
            return
        self.txt_iconpath.setText(path)

    def create_controls(self):
        self.txt_name = QLineEdit()
        self.chk_menu = QCheckBox(tr("Menu entry"))
        self.chk_menu.setChecked(True)
        self.chk_toolbar = QCheckBox(tr("Toolbar button"))
        self.chk_toolbar.setChecked(True)
        self.txt_category = QLineEdit()
        self.chk_icon = QCheckBox()
        self.chk_toolbar.setChecked(False)
        self.txt_iconpath = QLineEdit()
        self.btn_browse_icon = QPushButton("...")
        self.txt_iconpath.setEnabled(False)
        self.btn_browse_icon.setEnabled(False)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                QtCore.Qt.Horizontal)

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
        form.addRow(tr("Name"), self.txt_name)
        form.addRow(self.chk_menu, self.chk_toolbar)
        form.addRow(tr("Category"), self.txt_category)
        form.addRow(tr("Icon"), hbox)

        vbox = QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(btns)

        self.setLayout(vbox)


class ConsoleCodeCheckerMode(modes.CheckerMode):
    """ Runs pyflakes on you code while you're typing

    This checker mode runs pyflakes on the fly to check your python syntax.

    Works the same as FrostedCheckerMode, except it is aware of
    HyperspyUI's "globals".
    """

    def _request(self):
        """ Requests a checking of the editor content. """
        if not self.editor:
            return
        code = self.editor.toPlainText()
        if not self.myeditor.is_plugin:
            code = server._console_mode_header + code
        request_data = {
            'code': code,
            'path': self.editor.file.path,
            'encoding': self.editor.file.encoding
        }
        try:
            self.editor.backend.send_request(
                self._worker, request_data, on_receive=self._on_work_finished)
            self._finished = False
        except Exception:
            # retry later
            QtCore.QTimer.singleShot(100, self._request)

    def _on_work_finished(self, results):
        """
        Display results.

        :param status: Response status
        :param results: Response data, messages.
        """
        messages = []
        for msg in results:
            msg = modes.CheckerMessage(*msg)
            msg.line -= server._header_num_lines
            if msg.line < 0:
                continue
            block = self.editor.document().findBlockByNumber(msg.line)
            msg.block = block
            messages.append(msg)
        self.add_messages(messages)

    def __init__(self, editor):
        self.myeditor = editor
        super().__init__(run_pyflakes, delay=1200)


class ConsoleCodeCalltipsMode(pymodes.CalltipsMode):

    def __init__(self, editor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.myeditor = editor

    def _request_calltip(self, source, line, col, fn, encoding):
        if self._CalltipsMode__requestCnt == 0:
            self._CalltipsMode__requestCnt += 1
            if not self.myeditor.is_plugin:
                source = server._console_mode_header + source
                line += server._header_num_lines
            self.editor.backend.send_request(
                calltips,
                {'code': source, 'line': line, 'column': col, 'path': None,
                 'encoding': encoding}, on_receive=self._on_results_available)


class EditorWidget(ExToolWindow):
    code_title = tr("Code Editor")
    plugin_title = tr("Plugin Editor")

    def __init__(self, main_window, parent=None, path=None):
        super().__init__(parent)
        self.setWindowTitle(self.code_title)
        self.ui = main_window
        self._is_plugin = False
        self._suppress_append = False

        self.create_controls(path)

        self.save_action = QtWidgets.QAction(self)
        self.save_action.setShortcut(QtGui.QKeySequence.Save)
        self.save_action.triggered.connect(self.save)
        self.addAction(self.save_action)

        self.run_action = QtWidgets.QAction(self)
        self.run_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))
        self.run_action.triggered.connect(self.run)
        self.addAction(self.run_action)

        if path is not None and os.path.isfile(path):
            self.load(path)

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
        if self._suppress_append:
            return
        text = self.editor.toPlainText()
        if len(text) > 0 and text[-1] == '\n':
            prev_cursor = self.editor.textCursor()
            self.editor.moveCursor(QtGui.QTextCursor.End)
            self.editor.insertPlainText(code)
            self.editor.setTextCursor(prev_cursor)
        else:
            self.editor.appendPlainText(code)

    def make_plugin(self):
        diag = NameCategoryPrompt(self.ui, self)
        dr = diag.exec_()
        if dr == QtWidgets.QDialog.Accepted:
            if diag.chk_icon.isChecked():
                icon = diag.txt_iconpath.text()
            else:
                icon = None
            code = "ui = self.ui\n"
            code += "siglist = ui.hspy_signals\n"
            code += self.editor.toPlainText().rstrip()

            name = diag.txt_name.text()
            code = pc.create_plugin_code(code,
                                         name,
                                         diag.txt_category.text(),
                                         diag.chk_menu.isChecked(),
                                         diag.chk_toolbar.isChecked(),
                                         icon)
            path = os.path.normpath(os.path.dirname(__file__) +
                                    '/../plugins/' +
                                    name.lower().replace(' ', '').replace(
                                        '_', '') +
                                    '.py')
            e = EditorWidget(self.ui, self.ui, path)
            e.append_code(code)
            e.editor.moveCursor(QtGui.QTextCursor.Start)
            e.editor.ensureCursorVisible()
            self.ui.editors.append(e)   # We have to keep an instance!
            e.finished.connect(lambda: self.ui.editors.remove(e))
            e.is_plugin = True
            e.show()

    def register_plugin(self):
        dr = self.save()
        path = self.editor.file.path
        if dr and os.path.isfile(path):
            self.ui.plugin_manager.load_from_file(path)

    def save(self):
        if not os.path.isfile(self.editor.file.path):
            path = QtWidgets.QFileDialog.getSaveFileName(self,
                tr("Choose destination path"),
                self.editor.file.path)[0]
            if not path:
                return False
            self.editor.file._path = path
            open(path, 'w').close()  # Touch file so save_current works
        return self.tab.save_current()

    def load(self, filename):
        if filename is not None and os.path.exists(filename):
            self.editor.file.open(filename)

    def run(self):
        code = self.editor.toPlainText()
        old = self._suppress_append
        self._suppress_append = True
        self.ui.console.ex(code)
        self._suppress_append = old

    def sizeHint(self):
        # Default size to fit right margin
        def_sz = super().sizeHint()
        if hasattr(self, 'editor'):
            font = QtGui.QFont(self.editor.font_name, self.editor.font_size +
                               self.editor.zoom_level)
            metrics = QtGui.QFontMetricsF(font)
            pos = 80
            cm = self.layout().contentsMargins()
            # TODO: Currently uses manual, magic number. Do properly!
            offset = self.editor.contentOffset().x() + \
                2 * self.editor.document().documentMargin() + \
                cm.left() + cm.right() + 60
            x80 = round(metrics.width(' ') * pos) + offset
            def_sz.setWidth(x80)
        return def_sz

    def create_controls(self, path):
        editor = api.CodeEdit()
        editor.backend.start(server.__file__)

#        editor.panels.append(panels.FoldingPanel())
        editor.panels.append(panels.LineNumberPanel())
        editor.panels.append(panels.CheckerPanel())

        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.CodeCompletionMode())
        editor.modes.append(modes.ExtendedSelectionMode())
        editor.modes.append(modes.FileWatcherMode())
        editor.modes.append(modes.RightMarginMode())
        editor.modes.append(modes.SmartBackSpaceMode())
        editor.modes.append(modes.OccurrencesHighlighterMode())
        editor.modes.append(modes.SymbolMatcherMode())
#        editor.modes.append(modes.WordClickMode())
        editor.modes.append(modes.ZoomMode())

        editor.modes.append(pymodes.PythonSH(editor.document()))
        editor.modes.append(pymodes.CommentsMode())
        editor.modes.append(ConsoleCodeCalltipsMode(self))
        editor.modes.append(ConsoleCodeCheckerMode(self))
        editor.modes.append(pymodes.PEP8CheckerMode())
        editor.modes.append(pymodes.PyAutoCompleteMode())
        editor.modes.append(pymodes.PyAutoIndentMode())
        editor.modes.append(pymodes.PyIndenterMode())

        if path is not None:
            editor.file._path = path
        self.editor = editor
        self.tab = TabWidget(self)
        if path is not None and os.path.isfile(path):
            self.tab.add_code_edit(editor)
        else:
            self.tab.add_code_edit(editor, tr("untitled") + "%d.py")

        self.btn_save = QPushButton(tr("Save"))
        self.btn_run = QPushButton(tr("Run"))
        self.btn_make_plugin = QPushButton(tr("Make Plugin"))
        self.btn_reg_plugin = QPushButton(tr("Register Plugin"))
        self.btn_reg_plugin.setVisible(False)

        self.btn_save.clicked.connect(self.save)
        self.btn_run.clicked.connect(self.run)
        self.btn_make_plugin.clicked.connect(self.make_plugin)
        self.btn_reg_plugin.clicked.connect(self.register_plugin)

        self.hbox = QHBoxLayout()
        for w in [self.btn_save, self.btn_run,
                  self.btn_make_plugin, self.btn_reg_plugin]:
            self.hbox.addWidget(w)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.tab)
        vbox.addLayout(self.hbox)

        self.setLayout(vbox)
