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
Created on Sat Feb 21 16:05:41 2015

@author: Vidar Tonaas Fauske
"""

from .mainwindowbase import MainWindowBase, tr

import os
import inspect
from functools import partial

from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialogButtonBox

from hyperspyui.smartcolorsvgiconengine import SmartColorSVGIconEngine
from hyperspyui.advancedaction import AdvancedAction

from hyperspyui.log import logger as _logger

from hyperspyui import hooktraitsui

hooktraitsui.hook_traitsui()


class MainWindowUtils(MainWindowBase):
    """
    Adds UI utility functions to the main window, including traitsui dialog
    capture.
    """

    def __init__(self, parent=None):
        # traitsui backend bindings
        hooktraitsui.connect_created(self.on_traits_dialog)
        hooktraitsui.connect_destroyed(self.on_traits_destroyed)

        super().__init__(parent)


    # --------- traitsui Events ---------

    def capture_traits_dialog(self, callback):
        self.should_capture_traits = callback

    def on_traits_dialog(self, dialog, ui, parent):
        self.traits_dialogs.append(dialog)
        if parent is None:
            if self.should_capture_traits:
                self.should_capture_traits(dialog)
                self.should_capture_traits = None
            else:
                dialog.setParent(self, QtCore.Qt.Tool)
                dialog.show()
                dialog.activateWindow()

    def on_traits_destroyed(self, dialog):
        if dialog in self.traits_dialogs:
            self.traits_dialogs.remove(dialog)

    # --------- End traitsui Events ---------

    def set_status(self, msg):
        """
        Display 'msg' in window's statusbar.
        """
        # TODO: What info is needed? Add simple label first, create utility to
        # add more?
        self.statusBar().showMessage(msg)

    def _make_action(self, label, icon, shortcut, tip):
        ac = AdvancedAction(tr(label), self)
        if icon:
            ac.setIcon(self.make_icon(icon))
        if shortcut is not None:
            ac.setShortcut(shortcut)
        if tip is not None:
            ac.setStatusTip(tr(tip))
        return ac

    def _wire_action(self, ac, key, callback, selection_callback):
        try:
            keywords = inspect.getfullargspec(callback).args
        except TypeError:
            keywords = None
        if keywords and 'advanced' in keywords:
            orig_callback = callback

            def wrap(checked, advanced):
                orig_callback(advanced=advanced)
            callback = wrap
            ac.triggered[bool, bool].connect(callback)
        else:
            ac.triggered.connect(callback)
        # Use docstring for action
        if callback.__doc__:
            d = callback.__doc__
            if d.startswith('partial('):
                # Fix docstring of partial functions:
                d = callback.func.__doc__
            ac.__doc__ = d
        if selection_callback is not None:
            self._action_selection_cbs[key] = selection_callback
            ac.setEnabled(False)


    def add_action(self, key, label, callback, tip=None, icon=None,
                   shortcut=None, selection_callback=None):
        """
        Create and add a QAction to self.actions[key]. 'label' is used as the
        short description of the action, and 'tip' as the long description.
        The tip is typically shown in the statusbar. The callback is called
        when the action is triggered(). The optional 'icon' should either be a
        QIcon, or a path to an icon file, and is used to depict the action on
        toolbar buttons and in menus.

        If `selection_callback` is supplied, it is called whenever the
        currently selected signal/figure changes. This allows the callback to
        enable/disable the action to reflect whether the selected figure/signal
        is supported for the action.
        """
        ac = self._make_action(label, icon, shortcut, tip)
        self._wire_action(ac, key, callback, selection_callback)
        self.actions[key] = ac
        return ac

    def add_toolbar_button(self, category, action):
        """
        Add the supplied 'action' as a toolbar button. If the toolbar defined
        by 'cateogry' does not exist, it will be created in
        self.toolbars[category].
        """
        if category in self.toolbars:
            tb = self.toolbars[category]
        else:
            tb = QtWidgets.QToolBar(tr(category) + tr(" toolbar"), self)
            tb.setObjectName(category + "_toolbar")
            self.addToolBar(Qt.LeftToolBarArea, tb)
            self.toolbars[category] = tb

        if not isinstance(action, QtWidgets.QAction):
            action = self.actions[action]
        tb.addAction(action)

    def remove_toolbar_button(self, category, action):
        tb = self.toolbars[category]
        tb.removeAction(action)
        if len(tb.actions()) < 1:
            self.removeToolBar(tb)

    def add_menuitem(self, category, action, label=None):
        """
        Add the supplied 'action' as a menu entry. If the menu defined
        by 'cateogry' does not exist, it will be created in
        self.menus[category].

        If the label argument is not supplied, category will be used.
        """
        if category in self.menus:
            m = self.menus[category]
        else:
            if label is None:
                label = category
            # Make sure we add menu before window menu
            if self.windowmenu is None:
                m = self.menuBar().addMenu(label)
            else:
                m = QtWidgets.QMenu(label)
                self.menuBar().insertMenu(self.windowmenu.menuAction(), m)
            self.menus[category] = m

        if not isinstance(action, QtWidgets.QAction):
            action = self.actions[action]
        m.addAction(action)

    def add_tool(self, tool, selection_callback=None):
        if isinstance(tool, type):
            t = tool(self.figures)
            key = tool.__name__
        else:
            t = tool
            try:
                key = t.get_name()
            except NotImplementedError:
                key = tool.__class__.__name__
        self.tools.append(t)
        if t.single_action() is not None:
            self.add_action(key, t.get_name(), t.single_action(),
                            selection_callback=selection_callback,
                            icon=t.get_icon(), tip=t.get_description())
            self.add_toolbar_button(t.get_category(), self.actions[key])
        elif t.is_selectable():
            f = partial(self.select_tool, t)
            self.add_action(key, t.get_name(), f, icon=t.get_icon(),
                            selection_callback=selection_callback,
                            tip=t.get_description())
            self.selectable_tools.addAction(self.actions[key])
            self.actions[key].setCheckable(True)
            self.add_toolbar_button(t.get_category(), self.actions[key])
        return key

    def remove_tool(self, tool):
        if isinstance(tool, type):
            for t in self.tools:
                if isinstance(t, tool):
                    break
            key = tool.__name__
        else:
            t = tool
            try:
                key = t.get_name()
            except NotImplementedError:
                key = tool.__class__.__name__
        self.tools.remove(t)
        ac = self.actions.pop(key, None)
        if ac is not None:
            self.remove_toolbar_button(t.get_category(), ac)
            if t.is_selectable():
                self.selectable_tools.removeAction(ac)

    def add_widget(self, widget, floating=None):
        """
        Add the passed 'widget' to the main window. If the widget is not a
        QDockWidget, it will be wrapped into one. The QDockWidget is returned.
        The widget is also added to the window menu self.windowmenu, so that
        it's visibility can be toggled.

        The parameter 'floating' specifies whether the widget should be made
        floating. If None, the value of the setting 'default_widget_floating'
        is used.
        """
        if floating is None:
            floating = self.settings['default_widget_floating', bool]
        if isinstance(widget, QtWidgets.QDockWidget):
            d = widget
        else:
            d = QtWidgets.QDockWidget(self)
            d.setWidget(widget)
            d.setWindowTitle(widget.windowTitle())
        if not d.objectName():
            d.setObjectName(d.windowTitle())
        d.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, d)
        d.setFloating(floating)

        self.widgets.append(widget)

        # Insert widgets in Windows menu before separator (figures are after)
        self.windowmenu.insertAction(self.windowmenu_sep, d.toggleViewAction())
        return d

    def make_icon(self, icon):
        """
        Create an icon that coheres to the internal standard for icons.

        Parameters
        ----------
        icon : {string | QIcon}
            If icon is a path, it loads the file. If the path does not
            correspond to a valid file, it is checked if it is a valid
            path relative to the 'images' folder of the package.
            After loading, SVG files will be run through
            `SmartColorSVGIconEngine` to adapt suitable icons to the
            current palette. If a QIcon is passed directly, it is also
            sent through `SmartColorSVGIconEngine`.
        """
        if not isinstance(icon, QtGui.QIcon):
            if isinstance(icon, str) and not os.path.isfile(icon):
                sugg = os.path.dirname(__file__) + '/images/' + icon
                if os.path.isfile(sugg):
                    icon = sugg
            if isinstance(icon, str) and (
                    icon.endswith('svg') or
                    icon.endswith('svgz') or
                    icon.endswith('svg.gz')):
                ie = SmartColorSVGIconEngine()
                path = icon
                icon = QtGui.QIcon(ie)
                icon.addFile(path)
            else:
                icon = QtGui.QIcon(icon)
        else:
            icon = QtGui.QIcon(SmartColorSVGIconEngine(icon))
        return icon

    def prompt_files(self, extension_filter=None, path=None, exists=True,
                     title=None, def_filter=None):
        if title is None:
            title = tr('Load file') if exists else tr('Save file')
        path = path or self.cur_dir or ''
        if def_filter is None and extension_filter:
            def_filter = extension_filter.split(';;', maxsplit=1)[0]

        if exists:
            filenames = QtWidgets.QFileDialog.getOpenFileNames(
                self, title, path, extension_filter)
        else:

            filenames = QtWidgets.QFileDialog.getSaveFileName(
                self, title, path, extension_filter, def_filter)
        # Pyside returns tuple, PyQt not
        if isinstance(filenames, tuple):
            filenames = filenames[0]
        return filenames

    def get_figure_filepath_suggestion(self, figure, deault_ext=None):
        """
        Get a suggestion for a file path for saving `figure`.
        """
        canvas = figure.widget()
        if deault_ext is None:
            deault_ext = canvas.get_default_filetype()

        f = canvas.get_default_filename()
        if not f:
            f = self.cur_dir

        # Analyze suggested filename
        base, tail = os.path.split(f)
        fn, ext = os.path.splitext(tail)
        _logger.debug('fn before cleaning is: {}'.format(fn))

        # Remove illegal characters and newlines from filename:
        reserved_characters = r'<>:"/\|?*'
        for c in reserved_characters:
            fn = fn.replace(c, '')
        fn = fn.replace('\n', ' ')

        _logger.debug('fn after cleaning is: {}'.format(fn))

        # If no directory in filename, use self.cur_dir's dirname
        if base is None or base == "":
            base = os.path.dirname(self.cur_dir)
        # If extension is not valid, use the defualt
        if ext not in canvas.get_supported_filetypes():
            ext = deault_ext

        # Build suggestion and return
        path_suggestion = os.path.sep.join((base, fn))
        path_suggestion = os.path.extsep.join((path_suggestion, ext))
        return path_suggestion

    def save_figure(self, figure=None):
        """
        Save the matplotlib figure. If a figure is not passed, it tries to
        save whichever is active (using `activeSubWindow()` of the MDI area).
        """
        if figure is None:
            figure = self.main_frame.activeSubWindow()
            if figure is None:
                return
        path_suggestion = self.get_figure_filepath_suggestion(figure)
        canvas = figure.widget()

        # Build type selection string
        def_type = os.path.extsep + canvas.get_default_filetype()
        extensions = canvas.get_supported_filetypes_grouped()
        type_choices = "All types (*.*)"
        for group, exts in extensions.items():
            fmt = group + \
                ' (' + \
                '; '.join(["*" + os.path.extsep + sube for sube in exts]) + ')'
            type_choices = ';;'.join((type_choices, fmt))
            if def_type[1:] in exts:
                def_type = fmt

        # Present filename prompt
        filename = self.prompt_files(type_choices, path_suggestion,
                                     exists=False, def_filter=def_type)
        if filename:
            canvas.figure.savefig(filename)

    def show_okcancel_dialog(self, title, widget, modal=True):
        """
        Show a dialog with the passed widget and OK and cancel buttons.
        """
        diag = QtWidgets.QDialog(self)
        diag.setWindowTitle(title)
        diag.setWindowFlags(Qt.Tool)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                Qt.Horizontal, diag)
        btns.accepted.connect(diag.accept)
        btns.rejected.connect(diag.reject)

        box = QtWidgets.QVBoxLayout(diag)
        box.addWidget(widget)
        box.addWidget(btns)
        diag.setLayout(box)

        if modal:
            diag.exec_()
        else:
            diag.show()
        # Return the dialog for result checking, and to keep widget in scope
        # for caller
        return diag


class MainWindowActionRecorder(MainWindowUtils):

    """
    Adds recorder functionality.
    """

    def __init__(self, parent=None):
        self.recorders = []
        super().__init__(parent)

    def _wire_action(self, ac, key, callback, selection_callback):
        # Connect monitor
        ac.triggered.connect(partial(self.record_action, key))
        # Wire as normal
        super()._wire_action(
            ac, key, callback, selection_callback)

    def record_action(self, key):
        for r in self.recorders:
            r.add_action(key)

    def record_code(self, code):
        for r in self.recorders:
            r.add_code(code)

    def on_console_executing(self, source):
        super().on_console_executing(source)
        self.record_code(source)
