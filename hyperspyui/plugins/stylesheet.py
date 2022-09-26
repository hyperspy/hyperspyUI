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
from collections import OrderedDict

from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtWidgets import (QApplication, QPushButton, QLabel, QGroupBox,
                            QHBoxLayout, QVBoxLayout, QComboBox)

from qtpy.QtGui import QPalette


from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.backend import server

from hyperspyui.widgets.extendedqwidgets import ExToolWindow
from hyperspyui.widgets.colorpicker import ColorButton
from hyperspyui.util import block_signals


def tr(text):
    return QtCore.QCoreApplication.translate("Style", text)


class StylePlugin(Plugin):
    name = "Style"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        palette = self.settings['_palette']
        if palette is not None:
            QApplication.setPalette(QPalette(palette))
        QApplication.instance().setStyleSheet(self.settings['_style'] or '')

    def edit_dialog(self):
        if self.editor is not None:
            self.editor.show()
        else:
            self.editor = StyleDialog(self, self.ui, self.ui)
            self.editor.show()


class StyleDialog(ExToolWindow):
    """A dialog for editing Qt palette and stylesheet.

    Edits and sets Qt's application wide palette and stylesheet.
    See http://doc.qt.io/qt-4.8/stylesheet.html,
    and http://doc.qt.io/qt-4.8/qpalette.html
    for documentation of the effects of various settings, and
    the style sheet syntax.
    """

    palette_entries = OrderedDict((
        ('basic', (
            'Window',
            'WindowText',
        )),
        ('extended', (
            'Base',
            'Text',
            'ToolTipBase',
            'ToolTipText',
            'Button',
            'ButtonText',
        )),
        ('full', (
            'Highlight',
            'HighlightedText',
            'BrightText',
            'Light',
            'Midlight',
            'Mid',
            'Dark',
            'Shadow',
            'Link',
            'LinkVisited',
            'NoRole',
        )),
    ))

    pairs = [
        ('Window', 'WindowText'),
        ('Base', 'Text'),
        ('Button', 'ButtonText'),
        ('ToolTipBase', 'ToolTipText'),
        ('Highlight', 'HighlightedText'),
        ('Light', 'Midlight'),
        ('Mid', 'Dark'),
        ('Link', 'LinkVisited'),
    ]

    def __init__(self, plugin, ui, parent):
        super().__init__(parent)
        self.ui = ui
        self.setWindowTitle(tr("Edit application styles"))
        self.plugin = plugin
        self._palette = QPalette()
        self._rows = {}
        i = 0
        for entries in self.palette_entries.values():
            for key in entries:
                self._rows[key] = i
                for pair in self.pairs:
                    if key == pair[0]:
                        break
                else:
                    i += 1
        self.create_controls()

        self.save_action = QtWidgets.QAction(self)
        self.save_action.setShortcut(QtGui.QKeySequence.Save)
        self.save_action.triggered.connect(self.save)
        self.addAction(self.save_action)

        self.load()

    def save(self):
        """Store the palette and stylesheet to the plugin's settings"""
        self.plugin.settings['_style'] = self.editor.toPlainText()
        self.plugin.settings['_palette'] = self._palette

    def apply(self):
        """Apply current palette and stylesheet application wide"""
        QApplication.setPalette(self._palette)
        QApplication.instance().setStyleSheet(self.editor.toPlainText())

    def load(self):
        """Load palette and stylesheet from the plugin't settings"""
        self.editor.setPlainText(
            self.plugin.settings['_style'] or '',
            'text/plain', 'utf8'
        )
        palette = self.plugin.settings['_palette']
        if palette is not None:
            self._palette = QPalette(palette)
        self.update_palette_controls()

    def _clear_styles(self):
        """Reset style inputs to default values"""
        self._palette = QPalette(self.style().standardPalette())
        self.editor.clear()
        self.update_palette_controls()

    def create_controls(self):
        """Build the editor's controls"""
        # First set up the stylesheet editor:
        editor = api.CodeEdit()
        editor.backend.start(server.__file__)

        editor.panels.append(panels.LineNumberPanel())
        editor.panels.append(panels.CheckerPanel())

        editor.modes.append(AutoIndentMode())
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.modes.append(modes.CodeCompletionMode())
        editor.modes.append(modes.ExtendedSelectionMode())
        editor.modes.append(modes.SmartBackSpaceMode())
        editor.modes.append(modes.OccurrencesHighlighterMode())
        editor.modes.append(modes.SymbolMatcherMode())
        editor.modes.append(modes.ZoomMode())

        self.editor = editor

        # Create the pushbuttons for the button bar:
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

        # Create the group-box with the palette editor
        self.palette_box = self.create_palette_colors()

        # Lay out the various components:
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.palette_box)
        vbox.addWidget(editor)
        vbox.addLayout(self.hbox)

        self.setLayout(vbox)

    def create_palette_colors(self):
        """Create the controls for editing the palette"""
        layout = QtWidgets.QGridLayout()

        # Create combobox simple/extended/full
        cbo = QComboBox()
        cbo.addItems(list(self.palette_entries.keys()))
        cbo.currentIndexChanged[str].connect(self._on_cbo_change)
        layout.addWidget(cbo, 0, 0)
        self.cbo_mode = cbo

        # Create pickers for all
        self.pickers = {}
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
                row = 1 + self._rows[subkey]
                for pair in self.pairs:
                    if subkey == pair[1]:
                        layout.addWidget(label, row, 2)
                        layout.addWidget(btn, row, 3)
                        break
                else:
                    layout.addWidget(label, row, 0)
                    layout.addWidget(btn, row, 1)

        # Initialize colors:
        self.update_palette_controls()

        box = QGroupBox('Palette')
        box.setLayout(layout)
        return box

    def update_palette_controls(self):
        """Update palette controls from internal QPalette"""
        for key, entries in self.palette_entries.items():
            for subkey in entries:
                color = self._palette.color(
                    getattr(self._palette, subkey))
                btn = self.pickers[key][subkey]
                with block_signals(btn):
                    btn.color = color

    def _setvis_palette_entry(self, key, show):
        """Show/hide specific palette entries"""
        row = 1 + self._rows[key]
        layout = self.palette_box.layout()
        # Always show/hide pairs together:
        for i in range(4):
            item = layout.itemAtPosition(row, i)
            if item is not None:
                item.widget().setVisible(show)

    def _on_color_pick(self, key, color):
        """Callback when a palette color has been picked"""
        if self.cbo_mode.currentText() == 'basic':
            # Other values should be auto-generated
            self._palette = QPalette(self.pickers['basic']['Window'].color)

        self._palette.setColor(
            getattr(self._palette, key),
            color
        )

    def _on_cbo_change(self, selection):
        """Callback for when palette-mode selection changes"""
        # Use all up-until selection (keys are ordered)
        included = list(self.palette_entries.keys())
        included = included[:1 + included.index(selection)]

        for key, entries in self.palette_entries.items():
            visible = key in included
            for subkey in entries:
                self._setvis_palette_entry(subkey, show=visible)


class AutoIndentMode(modes.AutoIndentMode):
    """
    Provides automatic stylesheet-specific auto indentation.
    """
    def _get_indent(self, cursor):
        text = cursor.block().text().strip()
        pre, post = super()._get_indent(cursor)
        print(repr(text), repr(pre), repr(post))
        if text.endswith('{'):
            post += self.editor.tab_length * ' '
        elif text.startswith('}'):
            pre = pre[self.editor.tab_length:]
        return pre, post
