# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:46:35 2014

@author: Vidar Tonaas Fauske
"""

from collections import OrderedDict
from functools import partial
import argparse
import os
import sys
import pickle

# Should go before any MPL imports:
from hyperspyui.mainwindowlayer5 import MainWindowLayer5, tr

from hyperspyui.util import create_add_component_actions, win2sig, dict_rlu
from hyperspyui.widgets.contrastwidget import ContrastWidget
from hyperspyui.widgets.pluginmanagerwidget import PluginManagerWidget
import hyperspyui.tools

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import hyperspy.utils.plot
import hyperspy.signals


class MainWindow(MainWindowLayer5):

    """
    Main window of the application. Top layer in application stack. Is
    responsible for adding default actions, and filling the menus and toolbars.
    Also creates the default widgets. Any button-actions should also be
    accessible as a slot, such that other things can connect into it, and so
    that it is accessible from the console's 'ui' variable.
    """

    signal_types = OrderedDict([('Signal', hyperspy.signals.Signal),
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

    def __init__(self, parent=None):
        # State variables
        self.signal_type_ag = None
        self._plugin_manager_widget = None

        super(MainWindow, self).__init__(parent)

        # Set window icon
        self.setWindowIcon(QIcon(os.path.dirname(__file__) +
                                 '/../images/hyperspy.svg'))

        # Parse any command line options
        self.parse_args()

        # All good!
        self.set_status("Ready")

        # Redirect streams (wait until the end to not affect during load)
        self.settings.set_default('Output to console', False)
        if self.settings['Output to console'] is True:
            sys.stdout = self.console.kernel.stdout
            sys.stderr = self.console.kernel.stderr

    def handleSecondInstance(self, argv):
        """
        A second instance was launched and suppressed. Process the arguments
        that were passed to the new instance.
        """
        super(MainWindow, self).handleSecondInstance(argv)
        argv = pickle.loads(argv)
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

        self.add_action('open', "&Open", self.load,
                        shortcut=QKeySequence.Open,
                        icon='open.svg',
                        tip="Open existing file(s)")
        self.add_action('close', "&Close", self.close_signal,
                        shortcut=QKeySequence.Close,
                        icon='close_window.svg',
                        selection_callback=self.select_signal,
                        tip="Close the selected signal(s)")

        close_all_key = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_F4,
                                     Qt.CTRL + Qt.ALT + Qt.Key_W)
        self.add_action('close_all', "&Close All", self.close_all_signals,
                        shortcut=close_all_key,
                        icon='close_windows.svg',
                        tip="Close all signals")
        self.add_action('save', "&Save", self.save,
                        shortcut=QKeySequence.Save,
                        icon='save.svg',
                        selection_callback=self.select_signal,
                        tip="Save the selected signal(s)")
        self.add_action('save_fig', "Save &figure", self.save_figure,
                        #                        icon=os.path.dirname(__file__) + '/../images/save.svg',
                        tip="Save the active figure")

        self.add_action('add_model', "Create Model", self.make_model,
                        selection_callback=self.select_signal,
                        tip="Create a model for the selected signal")

        # Settings:
        self.add_action('plugin_manager', "Plugin manager",
                        self.show_plugin_manager,
                        tip="Show the plugin manager")
        self.add_action('edit_settings', "Edit settings", self.edit_settings,
                        tip="Edit the application and plugins settings")

        # --- Add signal type selection actions ---
        signal_type_ag = QActionGroup(self)
        signal_type_ag.setExclusive(True)
        for st in self.signal_types.iterkeys():
            f = partial(self.set_signal_type, st)
            st_ac = self.add_action('signal_type_' + st, st, f)
            st_ac.setCheckable(True)
            signal_type_ag.addAction(st_ac)
        self.signal_type_ag = signal_type_ag

        # TODO: Set signal datatype

        # --- Add "add component" actions ---
        comp_actions = create_add_component_actions(self, self.make_component)
        self.comp_actions = []
        for ac_name, ac in comp_actions.iteritems():
            self.actions[ac_name] = ac
            self.comp_actions.append(ac_name)

    def create_menu(self):
        mb = self.menuBar()

        # File menu (I/O)
        self.menus['File'] = mb.addMenu(tr("&File"))
        self.add_menuitem('File', self.actions['open'])
        self.add_menuitem('File', self.actions['close'])
        self.add_menuitem('File', self.actions['save'])
        self.add_menuitem('File', self.actions['save_fig'])
        self.menus['File'].addSeparator()
        self.add_menuitem('File', self.actions['close_all'])

        # Signal menu
        self.menus['Signal'] = mb.addMenu(tr("&Signal"))
        stm = self.menus['Signal'].addMenu(tr("Signal type"))
        for ac in self.signal_type_ag.actions():
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

        self.add_menuitem('Settings', self.actions['plugin_manager'])
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

        cbw = ContrastWidget(self)
        self.main_frame.subWindowActivated.connect(cbw.on_figure_change)
        self.add_widget(cbw)

    # ---------------------------------------
    # Events
    # ---------------------------------------

    def on_subwin_activated(self, mdi_figure):
        super(MainWindow, self).on_subwin_activated(mdi_figure)
        s = win2sig(mdi_figure, self.signals)
        if s is None:
            for ac in self.signal_type_ag.actions():
                ac.setChecked(False)
        else:
            t = type(s.signal)
            key = 'signal_type_' + dict_rlu(self.signal_types, t)
            self.actions[key].setChecked(True)

    # ---------------------------------------
    # Slots
    # ---------------------------------------

    def show_plugin_manager(self):
        if self._plugin_manager_widget is None:
            self._plugin_manager_widget = PluginManagerWidget(
                self.plugin_manager, self)
        self._plugin_manager_widget.show()

    def close_signal(self, uisignals=None):
        uisignals = self.get_selected_signals()
        for s in uisignals:
            s.close()

    def close_all_signals(self):
        while len(self.signals) > 0:
            s = self.signals.pop()
            s.close()

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
            signal = self.get_selected_signal()

        # Sanity check
        if signal_type not in self.signal_types.keys():
            raise ValueError()

        signal.keep_on_close = True
        self.setUpdatesEnabled(False)
        try:
            if signal_type in ['Image', 'Image simulation']:
                if not isinstance(signal.signal, (hyperspy.signals.Image,
                                                  hyperspy.signals.ImageSimulation)):
                    signal.as_image()
            elif signal_type in['Spectrum', 'Spectrum simulation', 'EELS',
                                'EELS simulation', 'EDS SEM', 'EDS TEM']:
                if isinstance(signal.signal, (hyperspy.signals.Image,
                                              hyperspy.signals.ImageSimulation)):
                    signal.as_spectrum()

            if signal_type in ['EELS', 'EDS SEM', 'EDS TEM']:
                underscored = signal_type.replace(" ", "_")
                signal.signal.set_signal_type(underscored)
            elif signal_type == 'EELS simulation':
                signal.signal.set_signal_type('EELS')

            if signal_type in ['Spectrum simulation', 'Image simulation',
                               'EELS simulation']:
                signal.signal.set_signal_origin('simulation')
            else:
                signal.signal.set_signal_origin('')  # Undetermined

            signal.plot()
            signal.keep_on_close = False
        finally:
            self.setUpdatesEnabled(True)
