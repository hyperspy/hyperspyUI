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

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QLabel

from hyperspy.learn.mva import LearningResults
from hyperspyui.util import win2sig, fig2win, Namespace
from hyperspyui.threaded import ProgressThreaded, ProcessCanceled
from hyperspyui.widgets.extendedqwidgets import ExToolWindow


def tr(text):
    return QtCore.QCoreApplication.translate("MVA", text)


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


def make_advanced_dialog(ui, algorithms=None):
    diag = ExToolWindow(ui)

    diag.setWindowTitle("Decomposition parameters")

    vbox = QtWidgets.QVBoxLayout()
    if algorithms:
        lbl_algo = QLabel(tr("Choose algorithm:"))
        cbo_algo = QtWidgets.QComboBox()
        cbo_algo.addItems(algorithms)

        vbox.addWidget(lbl_algo)
        vbox.addWidget(cbo_algo)
    else:
        lbl_comp = QLabel(tr(
            "Enter a comma-separated list of component numbers to use for "
            "the model:"))
        txt_comp = QLineEdit()
        vbox.addWidget(lbl_comp)
        vbox.addWidget(txt_comp)

    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                            QtCore.Qt.Horizontal)
    btns.accepted.connect(diag.accept)
    btns.rejected.connect(diag.reject)
    vbox.addWidget(btns)

    diag.setLayout(vbox)

    diag.algorithm = lambda: cbo_algo.currentText()
    diag.components = lambda: [int(s) for s in txt_comp.text().split(',')]
    return diag


class MVA_Plugin(Plugin):

    """
    Implements MVA decomposition utilities.
    """
    name = 'MVA'    # Used for settings groups etc

    coc_values = {'convert': tr("Convert"),
                  'copy': tr("Copy")}

    # ----------- Plugin interface -----------
    def create_actions(self):
        self.settings.set_default('convert_or_copy', None)
        self.settings.set_enum_hint('convert_or_copy',
                                    self.coc_values.keys())
        self.add_action('plot_decomposition_results',
                        tr("Decompose"),
                        self.plot_decomposition_results,
                        icon='pca.svg',
                        tip=tr("Decompose signal using Principle Component "
                               "analysis"),
                        selection_callback=self.selection_rules)
        self.add_action('pca', tr("Decomposition model"), self.pca,
                        icon='pca.svg',
                        tip=tr("Create a Principal Component Analysis "
                               "decomposition model"),
                        selection_callback=self.selection_rules)
        self.add_action('bss', tr("BSS"), self.bss,
                        icon='bss.svg',
                        tip=tr("Run Blind Source Separation"),
                        selection_callback=self.selection_rules)
        self.add_action('bss_model', tr("BSS model"), self.bss_model,
                        icon='bss.svg',
                        tip=tr("Create a Blind Source Separation "
                               "decomposition model"),
                        selection_callback=self.selection_rules)
        self.add_action('clear', tr("Clear"), self.clear,
                        tip=tr("Clear decomposition cache"),
                        selection_callback=self.selection_rules)

    def create_menu(self):
        self.add_menuitem('Decomposition',
                          self.ui.actions['plot_decomposition_results'])
        self.add_menuitem('Decomposition', self.ui.actions['pca'])
        self.add_menuitem('Decomposition', self.ui.actions['bss'])
        self.add_menuitem('Decomposition', self.ui.actions['bss_model'])
        self.add_menuitem('Decomposition', self.ui.actions['clear'])

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
                [kv for kv in self.coc_values.items()],
                title=tr("Convert or copy"),
                descr=tr(
                    "Signal data has the wrong data type (float needed)." +
                    "Would you like to convert the current signal, or " +
                    "perform the decomposition on a copy?"))
            if cc is None:
                # User canceled
                raise ProcessCanceled()
            if cc == 'copy':
                s = s.deepcopy()
                s.metadata.General.title = signal.name + "[float]"
                s.plot()
            s.change_dtype(float)
        return s, signal

    def _do_decomposition(self, s, force=False, algorithm=None):
        """
        Makes sure we have decomposition results. If results already are
        available, it will only recalculate if the `force` parameter is True.
        """
        if algorithm:
            s.decomposition(algorithm=algorithm)
        elif force or s.learning_results.explained_variance_ratio is None:
            s.decomposition()
        return s

    def _do_bss(self, s, n_components, algorithm=None):
        """
        Makes sure we have BSS results. If results already are available, it
        will only recalculate if the `force` parameter is True.
        """
        if algorithm:
            s.blind_source_separation(n_components, algorithm=algorithm)
        else:
            s.blind_source_separation(n_components)

    def get_bss_results(self, signal):
        factors = signal.get_bss_factors()
        loadings = signal.get_bss_loadings()
        factors.axes_manager._axes[0] = loadings.axes_manager._axes[0]
        return loadings, factors

    def _record(self, autosig, model, signal, n_components):
        if autosig:
            self.record_code(r"<p>.{0}(n_components={1})".format(
                             model, n_components))
        else:
            self.record_code(r"<p>.{0}({1}, n_components={2})".format(
                             model, signal, n_components))

    def _decompose_threaded(self, callback, label, signal=None,
                            algorithm=None, ns=None):
        if ns is None:
            ns = Namespace()
            ns.autosig = signal is None
            ns.s, _ = self._get_signal(signal)

        def do_threaded():
            ns.s = self._do_decomposition(ns.s, algorithm=algorithm)

        def on_error(message=None):
            em = QtWidgets.QErrorMessage(self.ui)
            msg = tr("An error occurred during decomposition")
            if message:
                msg += ":\n" + message
            em.setWindowTitle(tr("Decomposition error"))
            em.showMessage(msg)

        t = ProgressThreaded(self.ui, do_threaded, lambda: callback(ns),
                             label=label)
        t.worker.error[str].connect(on_error)
        t.run()

    def _perform_model(self, ns, n_components):
        # Num comp. picked, get model, wrap new signal and plot
        if ns.model == 'pca':
            sc = ns.s.get_decomposition_model(n_components)
            sc.metadata.General.title = ns.signal.name + "[PCA-model]"
            sc.plot()
        elif ns.model == 'bss' or ns.model.startswith('bss.'):
            if ns.model.startswith('bss.'):
                algorithm = ns.model[len('bss.'):]
                self._do_bss(ns.s, n_components, algorithm=algorithm)
            else:
                self._do_bss(ns.s, n_components)
            f, o = self.get_bss_results(ns.s)
            o.metadata.add_dictionary(ns.s.metadata.as_dictionary())
            f.metadata.General.title = ns.signal.name + "[BSS-Factors]"
            o.metadata.General.title = ns.signal.name + "[BSS-Loadings]"
            f.plot()
            o.plot()
        elif ns.model == 'bss_model':
            # Here we have to assume the user has actually performed the BSS
            # decomposition first!
            sc = ns.s.get_bss_model(n_components)
            sc.metadata.General.title = ns.signal.name + "[BSS-model]"
            sc.plot()
        if not ns.recorded:
            self._record(ns.autosig, ns.model, ns.signal, n_components)

    def _show_scree(self, ns, callback):
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
            callback(ns, n_components)
        scree.mpl_connect('button_press_event', clicked)

    def do_after_scree(self, model, signal=None, n_components=None):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        ns = Namespace()
        ns.autosig = signal is None
        ns.model = model
        ns.s, ns.signal = self._get_signal(signal)
        if n_components is not None:
            self._record(ns.autosig, ns.model, ns.signal, n_components)
            ns.recorded = True
        else:
            ns.recorded = False

        def on_complete(ns):
            if n_components is None:
                self._show_scree(ns, self._perform_model)
            else:
                self._perform_model(ns, n_components)

        self._decompose_threaded(on_complete, "Performing %s" % model.upper(),
                                 n_components, ns=ns)

    def plot_decomposition_results(self, signal=None, advanced=False):
        """
        Performs decomposition if necessary, then plots the decomposition
        results according to the hyperspy implementation.
        """
        def on_complete(ns):
            ns.s.plot_decomposition_results()
            # Somewhat speculative workaround to HSPY not adding metadata
            sd = self.ui.hspy_signals[-1]
            sd.metadata.add_dictionary(ns.s.metadata.as_dictionary())

        if advanced:
            diag = make_advanced_dialog(
                self.ui, ['svd', 'fast_svd', 'mlpca', 'fast_mlpca', 'nmf',
                          'sparse_pca', 'mini_batch_sparse_pca'])
            dr = diag.exec_()
            if dr == QDialog.Accepted:
                self._decompose_threaded(
                    on_complete, "Decomposing signal",
                    algorithm=diag.algorithm())
        else:
            self._decompose_threaded(on_complete, "Decomposing signal")

    def pca(self, signal=None, n_components=None, advanced=False):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        if advanced:
            diag = make_advanced_dialog(self.ui)
            dr = diag.exec_()
            if dr == QDialog.Accepted:
                self.do_after_scree(
                    'pca', signal, n_components=diag.components())
        else:
            self.do_after_scree('pca', signal, n_components)

    def bss(self, signal=None, n_components=None, advanced=False):
        """
        Performs decomposition if neccessary, then plots the scree for the user
        to select the number of components to use for a blind source
        separation. The selection is made by clicking on the scree, which
        closes the scree and creates the model.
        """
        if advanced:
            diag = make_advanced_dialog(
                self.ui, ['orthomax', 'sklearn_fastica', 'FastICA', 'JADE',
                          'CuBICA', 'TDSEP'])
            dr = diag.exec_()
            if dr == QDialog.Accepted:
                model = 'bss.' + diag.algorithm()
                self.do_after_scree(model, signal, n_components)
        else:
            self.do_after_scree('bss', signal, n_components)

    def bss_model(self, signal=None, n_components=None, advanced=False):
        """
        Performs decomposition if neccessary, then plots the scree for the user
        to select the number of components to use for a blind source
        separation model. The selection is made by clicking on the scree, which
        closes the scree and creates the model.
        """
        if advanced:
            diag = make_advanced_dialog(self.ui)
            dr = diag.exec_()
            if dr == QDialog.Accepted:
                self.do_after_scree(
                    'bss_model', signal, n_components=diag.components())
        else:
            self.do_after_scree('bss_model', signal, n_components)

    def clear(self, signal=None):
        """
        Clears the learning results from the signal.
        """
        if signal is None:
            signal = self.ui.get_selected_signal()
        signal.learning_results = LearningResults()
