# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:01 2014

@author: Vidar Tonaas Fauske
"""


from hyperspyui.plugins.plugin import Plugin

import psutil, gc
import numpy as np
import tempfile

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspy.drawing.spectrum import SpectrumLine

from hyperspyui.util import win2sig, fig2win, Namespace
from hyperspyui.threaded import ProgressThreaded

def tr(text):
    return QCoreApplication.translate("PCA", text)
    
def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    if y2 > y1:
        ratio = y1/y2
    else:
        ratio = y2/y1
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny2, maxy2 = ax2.get_ylim()
    ax2.set_ylim((miny2+dy)/ratio, (maxy2+dy)/ratio)

class MVA_Plugin(Plugin):
    """
    Implements MVA decomposition utilities.
    """
    name = 'MVA'    # Used for settings groups etc
    
    # ----------- Plugin interface -----------
    def create_actions(self):
        self.add_action('pca', "PCA", self.pca,
                        icon='pca.svg',
                        tip="Run Principal Component Analysis",
                        selection_callback=self.selection_rules)
        self.add_action('bss', "BSS", self.bss,
                        icon='bss.svg',
                        tip="Run Blind Source Separation",
                        selection_callback=self.selection_rules)
        self.add_action('explore_decomposition', "Explore decomposition",
                        self.explore_components,
                        selection_callback=self.selection_rules)
    
    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions['pca'])
        self.add_menuitem('Signal', self.ui.actions['bss'])
        self.add_menuitem('Signal', self.ui.actions['explore_decomposition'])
    
    def create_toolbars(self):
        self.add_toolbar_button("Signal", self.ui.actions['pca'])
        self.add_toolbar_button("Signal", self.ui.actions['bss'])
                  
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
            signal = self.ui.get_selected_signal()
        s = signal.signal

        if s.data.dtype.char not in ['e', 'f', 'd']:  # If not float
            cc = self.settings.get_or_prompt('convert_copy', 
                     (('convert', tr("Convert")), ('copy', tr("Copy"))),
                     title=tr("Convert or copy"),
                     descr=tr("Signal data has the wrong data type (float " + 
                     "needed). Would you like to convert the current" +
                     " signal, or perform the decomposition on a " +
                     "copy?"))
            if cc == 'copy':
                s = s.deepcopy()
                self.ui.add_signal_figure(s, signal.name + "[float]")
            s.change_dtype(float)
        return s, signal
            
    def _do_decomposition(self, s, force=False):
        """
        Makes sure we have decomposition results. If results already are 
        available, it will only recalculate if the `force` parameter is True.
        """
        if s.data.ndim == 2:
            bk_s_navigate = \
                    s.axes_manager._get_axis_attribute_values('navigate')
            s.axes_manager.set_signal_dimension(1)
        
        if force or s.learning_results.explained_variance_ratio is None:
            s.decomposition()
        
        if s.data.ndim == 2:
            s.axes_manager._set_axis_attribute_values('navigate', 
                                                      bk_s_navigate)
        return s
    
    def _do_bss(self, s, n_components, force=False):
        """
        Makes sure we have BSS results. If results already are available, it 
        will only recalculate if the `force` parameter is True.
        """
        if force or s.learning_results.bss_factors is None:
            s.blind_source_separation(n_components)
        
    def get_model(self, model, signal=None, n_components=None):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        ns = Namespace()
        autosig = signal is None
        ns.s, signal = self._get_signal(signal)
        
        def do_threaded():
            ns.s = self._do_decomposition(ns.s)
            
        def on_complete():
            if n_components is None:
                ax = ns.s.plot_explained_variance_ratio()
                    
                # Clean up plot and present, allow user to select components 
                # by picker
                ax.set_title("")
                scree = ax.get_figure().canvas
                scree.draw()
                scree.setWindowTitle("Pick number of components")
                def clicked(event):
                    n_components = round(event.xdata)
                    # Num comp. picked, get model, wrap new signal and plot
                    if model == 'pca':
                        sc = ns.s.get_decomposition_model(n_components)
                    elif model == 'bss':
                        self._do_bss(ns.s, n_components)
                        sc = ns.s.get_bss_model(n_components)
                    self.ui.add_signal_figure(sc, signal.name + 
                                              "[%s]" % model.upper())
                    # Close scree plot
                    w = fig2win(scree.figure, self.ui.figures)
                    w.close()
                    if autosig:
                        self.record_code(r"<p>.%s(n_components=%d)" % 
                                         (model, n_components))
                    else:
                        self.record_code(
                            r"<p>.{0}({1}, n_components={2})".format(
                            model, signal, n_components))
                scree.mpl_connect('button_press_event', clicked)
            else:
                sc = ns.s.get_decomposition_model(n_components)
                self.ui.add_signal_figure(sc, signal.name + 
                                          "[%s]" % model.upper())
                if autosig:
                    self.record_code(r"<p>.%s(n_components=%d)" % 
                                     (model, n_components))
                else:
                    self.record_code(r"<p>.{0}({1}, n_components={2})".format(
                                     model, signal, n_components))
            
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
        return self.get_model('pca', signal, n_components)
        

    def bss(self, signal=None, n_components=None):
        """
        Performs decomposition if neccessary, then plots the scree for the user
        to select the number of components to use for a blind source 
        separation. The selection is made by clicking on the scree, which 
        closes the scree and creates the model.
        """
        return self.get_model('bss', signal, n_components)
 
            
    def explore_components(self, signal=None, mmap="auto", n_component=50):
        """
        Utility function for seeing the effect of compoenent selection. Plots
        signal and residual, as well as factors and loadings. Also supports 
        memmaps loading for large data sets, which would otherwise cause a 
        MemoryError. Default behavior is "auto", which compares the dataset 
        size and the free memory available.
        """
        ns = Namespace()
        ns.s, signal = self._get_signal(signal)
        
        if mmap == "auto":
            # Figure out which mode to use
            gc.collect()
            # res_size ~ size of resulting data
            res_size = ns.s.data.nbytes * 2*n_component
            free_mem = psutil.phymem_usage()[2]
            mmap = res_size > free_mem
        if mmap:
            single_step = ns.s.data.nbytes * 2
            free_mem = psutil.phymem_usage()[2]
            mmap_step = max(1, int(0.5*free_mem / single_step))
            print "mmap_step", mmap_step
            
        def make_compound(s_scree, s_residual):
            """ Called to make UI components after completing calculations """
            s = ns.s
            s_scree.metadata.General.title = signal.name + " Component model"
            sw_scree = self.ui.add_signal_figure(s_scree, name = signal.name + 
                                           "[Component model]", plot=False)
                                           
            s_residual.metadata.General.title = signal.name + " Residual"
            if s.data.ndim == 2:
                bk_s_navigate = \
                        s.axes_manager._get_axis_attribute_values('navigate')
                s.axes_manager.set_signal_dimension(1)
            
            
            s_factors = s.get_decomposition_factors()
            if s_factors.axes_manager.navigation_dimension < 1:
                s_factors.axes_manager.set_signal_dimension(
                    s_factors.axes_manager.signal_dimension-1)
            s_factors = s_factors.inav[:n_component]
                
            s_loadings = s.get_decomposition_loadings().inav[:n_component]
                                               
            if s.data.ndim == 2:
                s.axes_manager._set_axis_attribute_values('navigate', 
                                                          bk_s_navigate)
            
            for ax in s_scree.axes_manager.navigation_axes:
                s_residual.axes_manager._axes[ax.index_in_array] = ax

            # Set navigating axes common for all signals
            ax = s_scree.axes_manager['Principal component index']
            s_factors.axes_manager._axes[0] = ax
            s_loadings.axes_manager._axes[0] = ax
                    
            
            # Make navigator signal
            if s.axes_manager.navigation_dimension == 0:
                nav = s.get_explained_variance_ratio()
                nav.axes_manager[0].name = "Explained variance ratio"
                if n_component < nav.axes_manager[-1].size:
                    nav = nav.isig[1:n_component]
                else:
                    nav = nav.isig[1:]
            else:
                nav = s_loadings
            
            # Plot signals with common navigator
            sw_scree.plot(navigator=nav)
            if s.axes_manager.navigation_dimension == 0:
                nax = s_scree._plot.navigator_plot.ax
                nax.set_ylabel("Explained variance ratio")
                nax.semilogy()
            
            if s_scree.axes_manager.signal_dimension == 1:
                p = s_scree._plot.signal_plot
                sla = SpectrumLine()
                sla.data_function = s_residual.__call__
                sla.set_line_properties(color="blue", type='step')
                sla.axes_manager = s_residual.axes_manager
                sla.autoscale = True
                p.add_line(sla)
                p.create_right_axis()
                p.right_zero_lock = True
                slb = SpectrumLine()
                slb.autoscale = True
                slb.data_function = s_factors.__call__
                slb.set_line_properties(color="green", type='step')
                slb.axes_manager = s_factors.axes_manager
                slb.autoscale = True
                p.add_line(slb, ax='right')
                p.plot()
                slb.plot()
            else:
                sw_residual = self.ui.add_signal_figure(s_residual, name = signal.name + 
                                               "[Residual]", plot=False)
                sw_factors = self.ui.add_signal_figure(s_factors, 
                                               name = signal.name + "[Factor]",
                                               plot=False)
                sw_residual.plot(navigator=None)
                sw_factors.plot(navigator=None)
            #TODO: Plot scree nav + loadings on same plot if navdim=1
        
        def threaded_gen():
            ns.s = self._do_decomposition(ns.s)
            stack_shape = (n_component-1,) + ns.s.data.shape
            if mmap:
                scree_f = tempfile.NamedTemporaryFile()
                screedata = np.memmap(scree_f,
                                         dtype=ns.s.data.dtype,
                                         mode='w+',
                                         shape=stack_shape,)
                res_f = tempfile.NamedTemporaryFile()
                res_data = np.memmap(res_f,
                                     dtype=ns.s.data.dtype,
                                     mode='w+',
                                     shape=stack_shape,)
            else:
                screedata = np.zeros(stack_shape,
                                    dtype=ns.s.data.dtype)
            old_auto_replot = ns.s.auto_replot
            ns.s.auto_replot = False
            final_shape = ns.s.data.shape
            ns.s._unfolded4decomposition = ns.s.unfold_if_multidim()
            try:
                target = ns.s.learning_results
                factors = target.factors
                loadings = target.loadings.T
                if target.mean is None:
                    data = np.zeros_like(ns.s.data)
                else:
                    data = np.copy(target.mean) 
                for n in xrange(1, n_component):
                    a = np.dot(factors[:, n-1:n],
                           loadings[n-1:n, :])
                    data += a.T
                    screedata[n-1,...] = data.reshape(final_shape)
                    if mmap:
                        res_data[n-1,...] = ns.s.data[n-1,...] - \
                                            screedata[n-1,...]
                        if n % mmap_step == 0 or n == n_component:
                            # Flushes mmap to disk and frees mem
                            print "Flushing"
                            del screedata
                            screedata = np.memmap(scree_f,
                                                  dtype=ns.s.data.dtype,
                                                  mode='r+',
                                                  shape=stack_shape,)
                            del res_data
                            res_data = np.memmap(res_f,
                                                 dtype=ns.s.data.dtype,
                                                 mode='r+',
                                                 shape=stack_shape,)
                    yield n
            finally:
                if ns.s._unfolded4decomposition is True:
                    ns.s.fold()
                ns.s.auto_replot = old_auto_replot
            ns.screedata = screedata
            if mmap:
                ns.resdata = res_data
            
        def on_threaded_complete():
            axes = []
            s = ns.s
            new_axis = {
                'name': 'Principal component index',
                'size': n_component-1,
                'units': '',
                'navigate': True}
            axes.append(new_axis)
            axes.extend(s.axes_manager._get_axes_dicts())

            s_scree = s.__class__(
                ns.screedata,
                axes=axes,
                metadata=s.metadata.as_dictionary(),)
            ns.screedata = None
            if mmap:
                s_residual = s_scree._deepcopy_with_new_data(ns.resdata)
                ns.resdata = None
            else:
                s_residual = s_scree.deepcopy()
                s_residual.data -= s.data
                s_residual.data[...] = -s_residual.data[...]
                    
            make_compound(s_scree, s_residual)
        
        label = 'Performing PCA'
        if mmap:
            label += '\n[Using memory map for data]'
        t = ProgressThreaded(self.ui, threaded_gen(), on_threaded_complete, 
                             label=label,
                             cancellable=True,
                             generator_N=n_component-1)
        t.run()
