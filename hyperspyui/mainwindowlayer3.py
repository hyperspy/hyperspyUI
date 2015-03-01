# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 16:05:41 2015

@author: Vidar Tonaas Fauske
"""


from mainwindowlayer2 import MainWindowLayer2, tr

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import os
from functools import partial


class MainWindowLayer3(MainWindowLayer2):

    """
    Third layer in the application stack. Adds UI utility functions.
    """

    def __init__(self, parent=None):
        super(MainWindowLayer3, self).__init__(parent)

    def set_status(self, msg):
        """
        Display 'msg' in window's statusbar.
        """
        # TODO: What info is needed? Add simple label first, create utility to
        # add more?
        self.statusBar().showMessage(msg)

    def add_action(self, key, label, callback, tip=None, icon=None,
                   shortcut=None, userdata=None, selection_callback=None):
        """
        Create and add a QAction to self.actions[key]. 'label' is used as the
        short description of the action, and 'tip' as the long description.
        The tip is typically shown in the statusbar. The callback is called
        when the action is triggered(). The 'userdata' is stored in the
        QAction's data() attribute. The optional 'icon' should either be a
        QIcon, or a path to an icon file, and is used to depict the action on
        toolbar buttons and in menus.
        """
        # TODO: Update doc to reflect final decision on userdata
        if icon is None:
            ac = QAction(tr(label), self)
        else:
            if not isinstance(icon, QIcon):
                if isinstance(icon, basestring) and not os.path.isfile(icon):
                    sugg = os.path.dirname(__file__) + '/../images/' + icon
                    if os.path.isfile(sugg):
                        icon = sugg
                icon = QIcon(icon)
            ac = QAction(icon, tr(label), self)
        if shortcut is not None:
            ac.setShortcuts(shortcut)
        if tip is not None:
            ac.setStatusTip(tr(tip))
        if userdata is not None:
            ac.setData(userdata)
        if userdata is None:
            self.connect(ac, SIGNAL('triggered()'), callback)
        else:
            def callback_udwrap():
                callback(userdata)
            self.connect(ac, SIGNAL('triggered()'), callback_udwrap)
        self.actions[key] = ac
        if selection_callback is not None:
            self._action_selection_cbs[key] = selection_callback
            ac.setEnabled(False)
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
            tb = QToolBar(tr(category) + tr(" toolbar"), self)
            self.addToolBar(Qt.LeftToolBarArea, tb)
            self.toolbars[category] = tb

        if not isinstance(action, QAction):
            action = self.actions[action]
        tb.addAction(action)

    def add_menuitem(self, category, action, label=None):
        """
        Add the supplied 'action' as a menu entry. If the menu defined
        by 'cateogry' does not exist, it will be created in
        self.menus[category].

        If the category_label argument is not supplied, category will be used.
        """
        if category in self.menus:
            m = self.menus[category]
        else:
            if label is None:
                label = category
            if self.windowmenu is None:
                m = self.menuBar().addMenu(label)
            else:
                m = QMenu(label)
                self.menuBar().insertMenu(self.windowmenu.menuAction(), m)
            self.menus[category] = m

        if not isinstance(action, QAction):
            action = self.actions[action]
        m.addAction(action)

    def add_tool(self, tool_type, selection_callback=None):
        t = tool_type(self.figures)
        self.tools.append(t)
        key = tool_type.__name__
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

    def add_widget(self, widget, floating=None):
        """
        Add the passed 'widget' to the main window. If the widget is not a
        QDockWidget, it will be wrapped in one. The QDockWidget is returned.
        The widget is also added to the window menu self.windowmenu, so that
        it's visibility can be toggled.

        The parameter 'floating' specifies whether the widget should be made
        floating. If None, the value of the attribute 'default_widget_floating'
        is used.
        """
        if floating is None:
            floating = self.default_widget_floating
        if isinstance(widget, QDockWidget):
            d = widget
        else:
            d = QDockWidget(self)
            d.setWidget(widget)
            d.setWindowTitle(widget.windowTitle())
        d.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, d)
        d.setFloating(floating)

        self.widgets.append(widget)

        # Insert widgets in Windows menu before separator (figures are after)
        self.windowmenu.insertAction(self.windowmenu_sep, d.toggleViewAction())
        return d

    def show_okcancel_dialog(self, title, widget, modal=True):
        diag = QDialog(self)
        diag.setWindowTitle(title)
        diag.setWindowFlags(Qt.Tool)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                Qt.Horizontal, diag)
        btns.accepted.connect(diag.accept)
        btns.rejected.connect(diag.reject)

        box = QVBoxLayout(diag)
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
