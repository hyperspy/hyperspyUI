# -*- coding: utf-8 -*-
# Copyright 2007-2016 The HyperSpyUI developers
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
Created on Fri Oct 24 16:46:35 2014

@author: Vidar Tonaas Fauske
"""

from collections import OrderedDict
from functools import partial
import argparse
import os
import sys
import json
import numpy as np

# Should go before any MPL imports:
from hyperspyui.mainwindowhyperspy import MainWindowHyperspy, tr

from hyperspyui.util import create_add_component_actions, win2sig, dict_rlu
from hyperspyui.widgets.contrastwidget import ContrastWidget
from hyperspyui.widgets.editorwidget import EditorWidget
from hyperspyui.widgets.pluginmanagerwidget import PluginManagerWidget
from hyperspyui.widgets.pickxsignals import PickXSignalsWidget
import hyperspyui.tools

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import hyperspy.utils.plot
import hyperspy.signals


class MainWindow(MainWindowHyperspy):

    """
    Main window of the application. Top layer in application stack. Is
    responsible for adding default actions, and filling the menus and toolbars.
    Also creates the default widgets. Any button-actions should also be
    accessible as a slot, such that other things can connect into it, and so
    that it is accessible from the console's 'ui' variable.
    """

    signal_types = OrderedDict(
        [('Signal', hyperspy.signals.Signal),
         ('Spectrum', hyperspy.signals.Spectrum),
         ('Spectrum simulation',
          hyperspy.signals.SpectrumSimulation),
         ('EELS', hyperspy.signals.EELSSpectrum),
         ('EELS simulation',
          hyperspy.signals.EELSSpectrumSimulation),
         ('EDS SEM', hyperspy.signals.EDSSEMSpectrum),
         ('EDS TEM', hyperspy.signals.EDSTEMSpectrum),
         ('Image', hyperspy.signals.Image),
         ('Image simulation', hyperspy.signals.ImageSimulation)])

    load_complete = Signal()

    def __init__(self, parent=None):
        # State variables
        self.signal_type_ag = None
        self.signal_datatype_ag = None
        self._plugin_manager_widget = None

        super(MainWindow, self).__init__(parent)

        # Set window icon
        self.setWindowIcon(QIcon(os.path.dirname(__file__) +
                                 '/images/hyperspy.svg'))

        # Parse any command line options
        self.parse_args()

        # All good!
        self.set_status("Ready")

        # Redirect streams (wait until the end to not affect during load)
        self.settings.set_default('output_to_console', False)
        if self.settings['output_to_console', bool]:
            self._old_stdout = sys.stdout
            self._old_stderr = sys.stdout
            sys.stdout = self.console.kernel.stdout
            sys.stderr = self.console.kernel.stderr
        else:
            self._old_stdout = self._old_stderr = None

    def handleSecondInstance(self, argv):
        """
        A second instance was launched and suppressed. Process the arguments
        that were passed to the new instance.
        """
        super(MainWindow, self).handleSecondInstance(argv)
        argv = json.loads(argv)
        self.parse_args(argv)

    def parse_args(self, argv=None):
        """
        Parse comman line arguments, either from sys.argv, or from parameter
        'argv'.
        """
        parser = argparse.ArgumentParser(
            description=QCoreApplication.applicationName() +
            " " + QCoreApplication.applicationVersion())
        parser.add_argument('files', metavar='file', type=str, nargs='*',
                            help='data file to open.')
        if argv:
            args = parser.parse_args(argv)
        else:
            args = parser.parse_args()
        files = args.files

        if len(files) > 0:
            self.load(files)

    def create_default_actions(self):
        super(MainWindow, self).create_default_actions()

        # Files:
        self.add_action('open', "&Open", self.load,
                        shortcut=QKeySequence.Open,
                        icon='open.svg',
                        tip="Open existing file(s)")
        self.add_action('open_stack', "Open S&tack", self.load_stack,
                        tip="Open files and combine into one signal (stacked)")
        self.add_action('close', "&Close", self.close_signal,
                        shortcut=QKeySequence.Close,
                        icon='close_window.svg',
                        selection_callback=self.select_signal,
                        tip="Close the selected signal(s)")
        self.add_action('new_editor', "&New editor", self.new_editor,
                        shortcut=QKeySequence.New,
                        tip="Opens a new code editor")

        close_all_key = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_F4,
                                     Qt.CTRL + Qt.ALT + Qt.Key_W)
        self.add_action('close_all', "&Close All", self.close_all_signals,
                        shortcut=close_all_key,
                        icon='close_windows.svg',
                        tip="Close all signals")
        self.add_action('exit', "E&xit", self.close,
                        shortcut=QKeySequence.Quit,
                        tip="Exits the application")

        # I/O:
        self.add_action('save', "&Save", self.save,
                        shortcut=QKeySequence.Save,
                        icon='save.svg',
                        selection_callback=self.select_signal,
                        tip="Save the selected signal(s)")
        self.add_action('save_fig', "Save &figure", self.save_figure,
                        tip="Save the active figure")

        self.add_action('add_model', "Create Model", self.add_model,
                        selection_callback=self.select_signal,
                        tip="Create a model for the selected signal")

        # Settings:
        self.add_action('plugin_manager', "Plugin manager",
                        self.show_plugin_manager,
                        tip="Show the plugin manager")
        self.add_action('hspy_settings', "HyperSpy settings",
                        self.edit_hspy_settings,
                        tip="Edit the HyperSpy package settings")
        self.add_action('edit_settings', "Edit settings", self.edit_settings,
                        tip="Edit the application and plugins settings")

        # --- Add signal type selection actions ---
        signal_type_ag = QActionGroup(self)
        signal_type_ag.setExclusive(True)
        for st in self.signal_types.keys():
            f = partial(self.set_signal_type, st)
            st_ac = self.add_action('signal_type_' + st, st, f)
            st_ac.setCheckable(True)
            signal_type_ag.addAction(st_ac)
        self.signal_type_ag = signal_type_ag

        # --- Add signal data type selection actions ---
        signal_datatype_ag = QActionGroup(self)
        signal_datatype_ag.setExclusive(True)
        import numpy as np
        for t in [np.bool, np.bool8, np.byte, np.complex, np.complex64,
                  np.complex128, np.float, np.float16, np.float32, np.float64,
                  np.int, np.int8, np.int16, np.int32, np.int64, np.long,
                  np.uint, np.uint8, np.uint16, np.uint32, np.uint64, 'Custom'
                  ]:
            f = partial(self.set_signal_dtype, t)
            if isinstance(t, str):
                st = t.lower()
            else:
                st = t.__name__

            sdt_ac = self.add_action('signal_data_type_' + st, st, f)
            sdt_ac.setCheckable(True)
            signal_datatype_ag.addAction(sdt_ac)
        self.signal_datatype_ag = signal_datatype_ag

        # Start disabled until a valid figure is selected
        self.signal_type_ag.setEnabled(False)
        self.signal_datatype_ag.setEnabled(False)

        # --- Add "add component" actions ---
        comp_actions = create_add_component_actions(self, self.make_component)
        self.comp_actions = []
        for ac_name, ac in comp_actions.items():
            self.actions[ac_name] = ac
            self.comp_actions.append(ac_name)
            self._action_selection_cbs[ac_name] = self._check_add_component_ok
            ac.setEnabled(False)

    def create_menu(self):
        mb = self.menuBar()

        # File menu (I/O)
        self.menus['File'] = mb.addMenu(tr("&File"))
        self.add_menuitem('File', self.actions['open'])
        self.add_menuitem('File', self.actions['open_stack'])
        self.add_menuitem('File', self.actions['close'])
        self.add_menuitem('File', self.actions['save'])
        self.add_menuitem('File', self.actions['save_fig'])
        self.add_menuitem('File', self.actions['new_editor'])

        # Signal menu
        self.menus['Signal'] = mb.addMenu(tr("&Signal"))
        stm = self.menus['Signal'].addMenu(tr("Signal type"))
        for ac in self.signal_type_ag.actions():
            stm.addAction(ac)
        stm = self.menus['Signal'].addMenu(tr("Signal data type"))
        for ac in self.signal_datatype_ag.actions():
            stm.addAction(ac)

        # Model menu
        self.menus['Model'] = mb.addMenu(tr("&Model"))
        self.add_menuitem('Model', self.actions['add_model'])
        self.modelmenu_sep1 = self.menus['Model'].addSeparator()

        componentmenu = self.menus['Model'].addMenu(tr("&Add Component"))
        for acname in self.comp_actions:
            componentmenu.addAction(self.actions[acname])

        # Create Windows menu
        super(MainWindow, self).create_menu()

        self.menus['File'].addSeparator()
        self.add_menuitem('File', self.actions['close_all'])
        self.add_menuitem('File', self.actions['exit'])

        # Ensure settings menu next to last
        if 'Settings' in self.menus:
            m = self.menus['Settings']
            self.menuBar().removeAction(m.menuAction())
            self.menuBar().insertMenu(self.windowmenu.menuAction(), m)

        self.add_menuitem('Settings', self.actions['plugin_manager'])
        self.add_menuitem('Settings', self.actions['reset_layout'])
        self.add_menuitem('Settings', self.actions['hspy_settings'])
        self.add_menuitem('Settings', self.actions['edit_settings'])

    def create_tools(self):
        super(MainWindow, self).create_tools()
        for tool_type in hyperspyui.tools.default_tools:
            self.add_tool(tool_type)

    def create_toolbars(self):
        self.add_toolbar_button("Files", self.actions['open'])
        self.add_toolbar_button("Files", self.actions['close'])
        self.add_toolbar_button("Files", self.actions['save'])

        super(MainWindow, self).create_toolbars()

    def create_widgetbar(self):
        super(MainWindow, self).create_widgetbar()

        self.add_widget(ContrastWidget(self, self))

    # ---------------------------------------
    # Events
    # ---------------------------------------

    def _check_add_component_ok(self, win, action):
        s = win2sig(win, self.signals, self._plotting_signal)
        if s is None:
            action.setEnabled(False)
        else:
            action.setEnabled(True)

    def on_subwin_activated(self, mdi_figure):
        super(MainWindow, self).on_subwin_activated(mdi_figure)
        s = win2sig(mdi_figure, self.signals, self._plotting_signal)
        if s is None:
            for ac in self.signal_type_ag.actions():
                ac.setChecked(False)
            for ac in self.signal_datatype_ag.actions():
                ac.setChecked(False)
            self.signal_type_ag.setEnabled(False)
            self.signal_datatype_ag.setEnabled(False)
        else:
            t = type(s.signal)
            key = 'signal_type_' + dict_rlu(self.signal_types, t)
            self.actions[key].setChecked(True)
            key2 = 'signal_data_type_' + s.signal.data.dtype.type.__name__
            if key2 in self.actions:
                self.actions[key2].setChecked(True)
            else:
                self.actions['signal_data_type_custom'].setChecked(True)
            self.signal_type_ag.setEnabled(True)
            self.signal_datatype_ag.setEnabled(True)

    def on_settings_changed(self):
        # Redirect streams (wait until the end to not affect during load)
        super(MainWindow, self).on_settings_changed()
        if self.settings['output_to_console', bool]:
            if self._old_stdout is None:
                self._old_stdout = sys.stdout
                self._old_stderr = sys.stderr
                sys.stdout = self.console.kernel.stdout
                sys.stderr = self.console.kernel.stderr
        else:
            if self._old_stdout is not None:
                sys.stdout = self._old_stdout
                sys.stderr = self._old_stderr

    # ---------------------------------------
    # Slots
    # ---------------------------------------

    def select_x_signals(self, x, titles=None, wrap_col=4):
        """
        Displays a blocking dialog prompting the user to select 'x' signals.
        Over each selection box, the title as defined by 'titles' is displayed.
        """
        w = PickXSignalsWidget(self.signals, x, parent=self,
                               titles=titles, wrap_col=wrap_col)
        diag = self.show_okcancel_dialog("Select signals", w, True)
        signals = None
        if diag.result() == QDialog.Accepted:
            signals = w.get_selected()
        w.unbind()
        return signals

    def show_plugin_manager(self):
        if self._plugin_manager_widget is None:
            self._plugin_manager_widget = PluginManagerWidget(
                self.plugin_manager, self)
        self._plugin_manager_widget.show()

    def close_signal(self, uisignals=None):
        uisignals = self.get_selected_wrappers()
        for s in uisignals:
            s.close()

    def close_all_signals(self):
        while len(self.signals) > 0:
            s = self.signals.pop()
            s.close()

    def new_editor(self):
        e = EditorWidget(self, self)
        self.editors.append(e)
        e.show()

    def set_signal_type(self, signal_type, signal=None):
        """
        Changes the signal type using a combination of hyperspy.Signal.:
         * set_signal_type()
         * set_signal_origin()
         * and by converting with as_image() and as_spectrum()
        """
        # The list of signal types is maintained as a list here and in
        # self.signal_types, as the names can be adapted, and since they need
        # to be diferentiated based on behavior either way.
        if signal is None:
            signal = self.get_selected_wrapper()
        self.record_code("signal = ui.get_selected_signal()")

        # Sanity check
        if signal_type not in list(self.signal_types.keys()):
            raise ValueError()

        self.setUpdatesEnabled(False)
        try:
            if signal_type in ['Image', 'Image simulation']:
                if not isinstance(signal.signal,
                                  (hyperspy.signals.Image,
                                   hyperspy.signals.ImageSimulation)):
                    signal.as_image()
                    self.record_code("signal = signal.as_image()")
            elif signal_type in['Spectrum', 'Spectrum simulation', 'EELS',
                                'EELS simulation', 'EDS SEM', 'EDS TEM']:
                if isinstance(signal.signal,
                              (hyperspy.signals.Image,
                               hyperspy.signals.ImageSimulation)):
                    signal.as_spectrum()
                    self.record_code("signal = signal.as_spectrum()")

            if signal_type in ['EELS', 'EDS SEM', 'EDS TEM']:
                underscored = signal_type.replace(" ", "_")
                signal.signal.set_signal_type(underscored)
                self.record_code("signal.set_signal_type('%s')" % underscored)
            elif signal_type == 'EELS simulation':
                signal.signal.set_signal_type('EELS')
                self.record_code("signal.set_signal_type('EELS')")

            if signal_type in ['Spectrum simulation', 'Image simulation',
                               'EELS simulation']:
                signal.signal.set_signal_origin('simulation')
                self.record_code("signal.set_signal_origin('simulation')")
            else:
                signal.signal.set_signal_origin('')  # Undetermined
                self.record_code("signal.set_signal_origin('')")

            signal.plot()
        finally:
            self.setUpdatesEnabled(True)

    def set_signal_dtype(self, data_type, signal=None, clip=False):
        if signal is None:
            signal = self.get_selected_signal()
        self.record_code("signal = ui.get_selected_signal()")
        if isinstance(data_type, str) and data_type.lower() == 'custom':
            return    # TODO: Show dialog and prompt
        if not clip:
            old_type = signal.data.dtype
            if np.issubdtype(data_type, np.integer):
                info = np.iinfo(data_type)
            elif np.issubdtype(data_type, np.float):
                info = np.finfo(data_type)
            if np.issubdtype(old_type, np.integer):
                old_info = np.iinfo(old_type)
            elif np.issubdtype(old_type, np.float):
                old_info = np.finfo(old_type)
            if old_info.max > info.max:
                signal.data *= float(info.max) / np.nanmax(signal.data)
                self.record_code("signal.data *= %f / np.nanmax(signal.data)" %
                                 float(info.max))
        signal.change_dtype(data_type)
        dts = data_type.__name__
        if data_type.__module__ == 'numpy':
            dts = 'np.' + dts
        self.record_code("signal.change_dtype(%s)" % dts)
