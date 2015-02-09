# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:01 2014

@author: Vidar Tonaas Fauske
"""


import plugin

import psutil, gc
import numpy as np
import tempfile

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspy.drawing.spectrum import SpectrumLine

from hyperspyui.util import win2sig, fig2win, Namespace
from hyperspyui.threaded import ProgressThreaded
from hyperspyui.widgets.extendedqwidgets import ExRememberPrompt

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

class PCA_Plugin(plugin.Plugin):
    """
    Implements PCA decomposition utilities.
    """
    name = 'PCA'    # Used for settings groups etc
    
    # ----------- Plugin interface -----------
    def create_actions(self):
        self.ui.add_action('pca', "PCA", self.pca,
                        icon='pca.svg',
                        tip="Run Principal Component Analysis",
                        selection_callback=self.selection_rules)
        self.ui.add_action('pca_explore_components', "Explore PCA components",
                           self.explore_components,
                           selection_callback=self.selection_rules)
    
    def create_menu(self):
        self.ui.signalmenu.addAction(self.ui.actions['pca'])
        self.ui.signalmenu.addAction(self.ui.actions['pca_explore_components'])
    
    def create_toolbars(self):
        self.ui.add_toolbar_button("Signal", self.ui.actions['pca'])
                  
    def selection_rules(self, win, action):
        """
        Callback to determine if PCA is valid for the passed window.
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
                s_nav = s.get_explained_variance_ratio()
                s_nav.axes_manager[0].name = "Explained variance ratio"
                if n_component < s_nav.axes_manager[-1].size:
                    s_nav = s_nav.isig[1:n_component]
                else:
                    s_nav = s_nav.isig[1:]
            else:
                s_nav = "auto"
            
            # Plot signals with common navigator
            sw_scree.plot(navigator=s_nav)
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
                oldup = slb.update
                def newup(force_replot=False):
                    oldup(force_replot)
#                    align_yaxis(p.ax, 0, p.right_ax, 0)
                    p.right_ax.hspy_fig._draw_animated()
                slb.update = newup
                p.add_line(slb, ax='right')
                p.plot()
                slb.plot()
#                align_yaxis(p.ax, 0, p.right_ax, 0)
                sw_residual = None
                sw_factors = None
            else:
                sw_residual = self.ui.add_signal_figure(s_residual, name = signal.name + 
                                               "[Residual]", plot=False)
                sw_factors = self.ui.add_signal_figure(s_factors, 
                                               name = signal.name + "[Factor]",
                                               plot=False)
                sw_residual.plot(navigator=None)
                sw_factors.plot(navigator=None)
                
            #TODO: Plot scree nav + loadings on same plot if navdim=1
                
            sw_loadings = self.ui.add_signal_figure(s_loadings, 
                                            name = signal.name + "[Loading]", 
                                            plot=False)
            sw_loadings.plot(navigator=None)
            return sw_scree, sw_residual, sw_factors, sw_loadings
        
        def threaded_gen():
            ns.s = self._do_decomposition(ns.s)
            stack_shape = (n_component-1,) + ns.s.data.shape
            if mmap:
                tempf = tempfile.NamedTemporaryFile()
                ns.screedata = np.memmap(tempf,
                                         dtype=ns.s.data.dtype,
                                         mode='w+',
                                         shape=stack_shape,)
            else:
                ns.screedata = np.zeros(stack_shape,
                                    dtype=ns.s.data.dtype)
            for n in xrange(1, n_component):
                m = ns.s.get_decomposition_model(n)
                ns.screedata[n-1,...] = m.data
                del m.data
                del m
                yield n
            
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
            s_residual = s_scree.deepcopy()
            s_residual.data -= s.data
                    
            make_compound(s_scree, s_residual)
        
        t = ProgressThreaded(self.ui, threaded_gen(), on_threaded_complete, 
                             label='Performing PCA',
                             cancellable=True,
                             generator_N=n_component-1)
        t.run()
        

    def pca(self, signal=None):
        """
        Performs decomposition, then plots the scree for the user to select
        the number of components to use for a decomposition model. The
        selection is made by clicking on the scree, which closes the scree
        and creates the model.
        """
        ns = Namespace()
        ns.s, signal = self._get_signal(signal)
        
        def do_threaded():
            ns.s = self._do_decomposition(ns.s)
            
        def on_complete():
            ax = ns.s.plot_explained_variance_ratio()
                
            # Clean up plot and present, allow user to select components by picker
            ax.set_title("")
            scree = ax.get_figure().canvas
            scree.draw()
            scree.setWindowTitle("Pick number of components")
            def clicked(event):
                components = round(event.xdata)
                # Num comp. picked, perform PCA, wrap new signal and plot
                sc = ns.s.get_decomposition_model(components)
                self.ui.add_signal_figure(sc, signal.name + "[PCA]")
                # Close scree plot
                w = fig2win(scree.figure, self.ui.figures)
                w.close()
            scree.mpl_connect('button_press_event', clicked)
            
        t = ProgressThreaded(self.ui, do_threaded, on_complete, 
                             label="Performing PCA")
        t.run()
        
                        
                        
        
        