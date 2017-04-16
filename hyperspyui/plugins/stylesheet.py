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
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.

from hyperspyui.plugins.plugin import Plugin

from functools import partial

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.backend import server

from hyperspyui.widgets.extendedqwidgets import ExToolWindow
from hyperspyui.util import block_signals


def tr(text):
    return QCoreApplication.translate("Style", text)


class StylePlugin(Plugin):
    name = "Style"

    def __init__(self, *args, **kwargs):
        super(StylePlugin, self).__init__(*args, **kwargs)
        self.editor = None
        self.settings.set_default('_style', '')
        self.apply_styles()

    def create_actions(self):
        self.add_action('edit_style', tr("Edit styles"),
                        self.edit_dialog,
                        # icon='.svg',
                        tip=tr("Edit the application styles"))

    def create_menu(self):
        self.add_menuitem('Settings', self.ui.actions['edit_style'])

    def apply_styles(self):
        QApplication.instance().setStyleSheet(self.settings['_style'])
        palette = self.settings['_palette']
        if palette is not None:
            QApplication.setPalette(QPalette(palette))

    def edit_dialog(self):
        if self.editor is not None:
            self.editor.show()
        else:
            self.editor = StyleDialog(self, self.ui, self.ui)
            self.editor.show()


class StyleDialog(ExToolWindow):
    # Styleshhet ref: http://doc.qt.io/qt-4.8/stylesheet.html

    palette_entries = {
        'basic': [
            'Window',
            'WindowText',
        ],
        'extended': [
            'Base',
            'Text',
            'ToolTipBase',
            'ToolTipText',
            'Button',
            'ButtonText',
            'BrightText',
        ],
        'full': [
            'Light',
            'Midlight',
            'Dark',
            'Mid',
            'Shadow',
            'Highlight',
            'HighlightedText',
            'Link',
            'LinkVisited',
            'NoRole',
        ],
    }

    def __init__(self, plugin, ui, parent):
        super(StyleDialog, self).__init__(parent)
        self.ui = ui
        self.setWindowTitle(tr("Edit application styles"))
        self.plugin = plugin
        self._palette = QPalette()
        self._rows = {}
        i = 0
        for entries in self.palette_entries.values():
            for key in entries:
                self._rows[key] = i
                i += 1
        self.create_controls()

        self.save_action = QAction(self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save)
        self.addAction(self.save_action)

        self.load()

    def save(self):
        self.plugin.settings['_style'] = self.editor.toPlainText()
        self.plugin.settings['_palette'] = self._palette

    def apply(self):
        QApplication.instance().setStyleSheet(self.editor.toPlainText())
        QApplication.setPalette(self._palette)

    def load(self):
        self.editor.setPlainText(
            self.plugin.settings['_style'],
            'text/plain', 'utf8'
        )
        palette = self.plugin.settings['_palette']
        if palette is not None:
            self._palette = QPalette(palette)
        self.update_palette_controls()

    def _clear_styles(self):
        self._palette = QPalette(self.style().standardPalette())
        self.editor.clear()
        self.update_palette_controls()

    def create_controls(self):
        editor = api.CodeEdit()
        editor.backend.start(server.__file__)

        # editor.panels.append(panels.FoldingPanel())
        editor.panels.append(panels.LineNumberPanel())
        editor.panels.append(panels.CheckerPanel())

        editor.modes.append(AutoIndentMode())
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.CodeCompletionMode())
        editor.modes.append(modes.ExtendedSelectionMode())
        editor.modes.append(modes.SmartBackSpaceMode())
        editor.modes.append(modes.OccurrencesHighlighterMode())
        editor.modes.append(modes.SymbolMatcherMode())
        # editor.modes.append(modes.WordClickMode())
        editor.modes.append(modes.ZoomMode())

        self.editor = editor

        self.btn_apply = QPushButton(tr("Apply"))
        self.btn_apply.clicked.connect(self.apply)

        self.btn_save = QPushButton(tr("Save"))
        self.btn_save.clicked.connect(self.save)

        self.btn_revert = QPushButton(tr("Revert"))
        self.btn_revert.clicked.connect(self.load)

        self.btn_clear = QPushButton(tr("Clear"))
        self.btn_clear.clicked.connect(self._clear_styles)

        self.hbox = QHBoxLayout()
        for w in [self.btn_apply, self.btn_save,
                  self.btn_revert, self.btn_clear]:
            self.hbox.addWidget(w)

        vbox = QVBoxLayout(self)
        self.palette_box = self.create_palette_colors()
        vbox.addWidget(self.palette_box)
        vbox.addWidget(editor)
        vbox.addLayout(self.hbox)

        self.setLayout(vbox)

    def update_palette_controls(self):
        for key, entries in self.palette_entries.items():
            for subkey in entries:
                color = self._palette.color(
                    getattr(self._palette, subkey))
                btn = self.pickers[key][subkey]
                with block_signals(btn):
                    btn.color = color

    def _setvis_palette_entry(self, key, show):
        row = 1 + self._rows[key]
        layout = self.palette_box.layout()
        if show:
            layout.itemAtPosition(row, 0).widget().show()
            layout.itemAtPosition(row, 1).widget().show()
        else:
            layout.itemAtPosition(row, 0).widget().hide()
            layout.itemAtPosition(row, 1).widget().hide()

    def _on_color_pick(self, key, color):
        self._palette.setColor(
            getattr(self._palette, key),
            color
        )

    def _on_cbo_change(self, selection):
        # Use all up-until selection (base/extended/full is alphabetical)
        included = list(sorted(self.palette_entries.keys()))
        included = included[:1 + included.index(selection)]

        for key, entries in self.palette_entries.items():
            visible = key in included
            for subkey in entries:
                self._setvis_palette_entry(subkey, show=visible)

    def create_palette_colors(self):
        layout = QGridLayout()

        # Create combobox simple/extended/full
        cbo = QComboBox()
        cbo.addItems(list(sorted(self.palette_entries.keys())))
        cbo.currentIndexChanged[str].connect(self._on_cbo_change)
        layout.addWidget(cbo, 0, 0)
        self.cbo_mode = cbo

        # Create pickers for all
        self.pickers = {}
        row = 1
        for key, entries in self.palette_entries.items():
            self.pickers[key] = {}
            for subkey in entries:
                btn = ColorButton()
                self.pickers[key][subkey] = btn
                btn.colorChanged.connect(
                    partial(self._on_color_pick, subkey))
                label = QLabel(subkey)
                if key != 'basic':
                    btn.hide()
                    label.hide()
                layout.addWidget(label, row, 0)
                layout.addWidget(btn, row, 1)
                row += 1

        self.update_palette_controls()

        box = QGroupBox('Palette')
        box.setLayout(layout)
        return box


class AutoIndentMode(modes.AutoIndentMode):
    """
    Provides automatic stylesheet specific auto indentation.
    """
    def _get_indent(self, cursor):
        text = cursor.block().text().strip()
        pre, post = super(AutoIndentMode, self)._get_indent(cursor)
        if text.endswith('{'):
            post += self.editor.tab_length * ' '
        elif text.startswith('}'):
            pre = pre[self.editor.tab_length:]
        return pre, post


class ColorButton(QPushButton):

    colorChanged = Signal([QColor])

    def __init__(self, color=None, parent=None):
        super(ColorButton, self).__init__(parent)
        self.setMinimumWidth(50)
        if color is None:
            color = QColor('gray')
        self.color = color
        self.clicked.connect(self.choose_color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self.colorChanged.emit(color)
        self.update()

    def choose_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color

    def paintEvent(self, event):
        super(ColorButton, self).paintEvent(event)
        padding = 5

        rect = event.rect()
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QColor("#CECECE"))
        rect.adjust(
            padding, padding,
            -1-padding, -1-padding)
        painter.drawRect(rect)
