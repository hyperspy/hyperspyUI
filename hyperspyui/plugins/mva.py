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
Created on Fri Dec 12 23:44:01 2014

@author: Vidar Tonaas Fauske
"""


from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.util import win2sig, fig2win, Namespace
from hyperspyui.threaded import ProgressThreaded


def tr(text):
    return QCoreApplication.translate("MVA", text)


def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    if y2 > y1:
        ratio = y1 / y2
    else:
        ratio = y2 / y1
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1 - y2))
    miny2, maxy2 = ax2.get_ylim()
    ax2.set_ylim((miny2 + dy) / ratio, (maxy2 + dy) / ratio)


class MVA_Plugin(Plugin):

    """
    Implements MVA decomposition utilities.
    """
    name = 'MVA'    # Used for settings groups etc

    # ----------- Plugin interface -----------
    def create_actions(self):
        self.add_action('pca', tr("PCA"), self.pca,
                        icon='pca.svg',
                        tip=tr("Run Principal Component Analysis"),
                        selection_callback=self.selection_rules)
        self.add_action('bss', tr("BSS"), self.bss,
                        icon='bss.svg',
                        tip=tr("Run Blind Source Separation"),
                        selection_callback=self.selection_rules)
        self.add_action('plot_decomposition_results',
                        tr("Decomposition results"),
                        self.plot_decomposition_results,
                        tip=tr("Plot the decomposition results"),
                        selection_callback=self.selection_rules)

    def create_menu(self):
        self.add_menuitem('Decomposition', self.ui.actions['pca'])
        self.add_menuitem('Decomposition', self.ui.actions['bss'])
        self.add_menuitem('Decomposition',
                          self.ui.actions['plot_decomposition_results'])

    def create_toolbars(self):
        self.add_toolbar_button("Decomposition", self.ui.actions['pca'])
        self.add_toolbar_button("Decomposition", self.ui.actions['bss'])

    def selection_rules(self, win, action):
        """
        Callback to determine if action is valid for the passed window.
        """
        s = win2sig(win, self.ui.signals)
        if s is None or s.signal.data.ndim <= 1:
            action.setEnabled(False)
        else:
            action.setEnabled(True)

    # ------------ Action implementations --------------

    def _get_signal(self, signal):
        """
        Get a valid signal. If the signal is none, it ues the currently
        selected one. If the signal type is not float, it either converts it,
        or gets a copy of the correct type, depending on the 'convert_copy'
        setting.
        """
        if signal is None:
            signal = self.ui.get_selected_wrapper()
        s = signal.signal

        if s.data.dtype.char not in ['e', 'f', 'd']:  # If not float
            cc = self.settings.get_or_prompt(
                'convert_or_copy',
                (('convert', tr("Convert")),
                 ('copy', tr("Copy"))),
                title=tr("Convert or copy"),
                descr=tr(
                    "Signal data has the wrong data type (float needed)." +
                    "Would you like to convert the current signal, or " +
                    "perform the decomposition on a copy?"))
            if cc == 'copy':
                s = s.deepcopy()
                s.metadata.General.title = signal.name + "[float]"
                s.plot()
            s.change_dtype(float)
        return s, signal

    def _do_decomposition(self, s, force=False):
        """
        Makes sure we have decomposition results. If results already are
        available, it will only recalculate if the `force` parameter is True.
        """
        if force or s.learning_results.explained_variance_ratio is None:
            s.decomposition()
        return s

    def _do_bss(self, s, n_components, force=False):
        """
        Makes sure we have BSS results. If results already are available, it
        will only recalculate if the `force` parameter is True.
        """
        s.blind_source_separation(n_components)
#        if force or s.learning_results.bss_factors is None:
#            s.blind_source_separation(n_components)

    def plot_decomposition_results(self, signal=None):
        """
        Performs decomposition if necessary, then plots the decomposition
        results according to the hyperspy implementation.
        """
        s, _ = self._get_signal(signal)
        self._do_decomposition(s)
        s.plot_decomposition_results()
        # Somewhat speculative workaround to HSPY not adding metadata
        sd = self.ui.hspy_signals[-1]
        sd.metadata.add_dictionary(s.metadata.as_dictionary())

    def get_bss_results(self, signal):
        factors = signal.get_bss_factors()
        loadings = signal.get_bss_loadings()
        factors.axes_manager._axes[0] = loadings.axes_manager._axes[0]
        return loadings, factors

    def _record(self, autosig, model, signal, n_components):
        if autosig:
            self.record_code(r"<p>.%s(n_components=%d)" %
                             (model, n_components))
        else:
            self.record_code(r"<p>.{0}({1}, n_components={2})".format(
                             model, signal, n_components))

    def do_after_scree(self, model, signal=None, n_components=None):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        ns = Namespace()
        autosig = signal is None
        ns.s, signal = self._get_signal(signal)
        if n_components is not None:
            self._record(autosig, model, signal, n_components)
            recorded = True
        else:
            recorded = False

        def do_threaded():
            ns.s = self._do_decomposition(ns.s)

        def on_complete():
            def _do(n_components):
                # Num comp. picked, get model, wrap new signal and plot
                if model == 'pca':
                    sc = ns.s.get_decomposition_model(n_components)
                    sc.metadata.General.title = signal.name + "[PCA]"
                    sc.plot()
                elif model == 'bss':
                    self._do_bss(ns.s, n_components)
                    f, o = self.get_bss_results(ns.s)
                    o.metadata.add_dictionary(ns.s.metadata.as_dictionary())
                    f.metadata.General.title = signal.name + "[BSS-Factors]"
                    o.metadata.General.title = signal.name + "[BSS-Loadings]"
                    f.plot()
                    o.plot()
                if not recorded:
                    self._record(autosig, model, signal, n_components)
            if n_components is None:
                ax = ns.s.plot_explained_variance_ratio()

                # Clean up plot and present, allow user to select components
                # by picker
                ax.set_title("")
                scree = ax.get_figure().canvas
                scree.draw()
                scree.setWindowTitle("Pick number of components")

                def clicked(event):
                    n_components = int(round(event.xdata))
                    # Close scree plot
                    w = fig2win(scree.figure, self.ui.figures)
                    w.close()
                    _do(n_components)
                scree.mpl_connect('button_press_event', clicked)
            else:
                _do(n_components)

        t = ProgressThreaded(self.ui, do_threaded, on_complete,
                             label="Performing %s" % model.upper())
        t.run()

    def pca(self, signal=None, n_components=None):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        return self.do_after_scree('pca', signal, n_components)

    def bss(self, signal=None, n_components=None):
        """
        Performs decomposition if neccessary, then plots the scree for the user
        to select the number of components to use for a blind source
        separation. The selection is made by clicking on the scree, which
        closes the scree and creates the model.
        """
        return self.do_after_scree('bss', signal, n_components)
