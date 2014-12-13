# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:01 2014

@author: Vidar Tonaas Fauske
"""


import plugin
from hyperspyui.util import win2sig, fig2win
from signalwrapper import SignalWrapper

class PCA_Plugin(plugin.Plugin):
    def create_actions(self):
        self.ui.add_action('pca', "PCA", self.pca,
                        icon='pca.svg',
                        tip="Run Principal Component Analysis",
                        selection_callback=self.selection_rules)
    
    def create_menu(self):
        self.ui.signalmenu.addAction(self.ui.actions['pca'])
    
    def create_toolbars(self):
        self.ui.add_toolbar_button("Signal", self.ui.actions['pca'])
                  
    # --- Add PCA action ---
    def selection_rules(self, win, action):
        s = win2sig(win, self.ui.signals)
        if s is None or s.signal.data.ndim <= 1:
            action.setEnabled(False)
        else:
            action.setEnabled(True)

    def pca(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        s = signal.signal
        
        try:
            s.decomposition()
            ax = s.plot_explained_variance_ratio()  # Make scree plot
        # decomp.. warns if wrong type, but plot_expl.. raises exception
        except AttributeError:
            # TODO: Messagebox prompt in place change or copy
            s = s.deepcopy()
            s.change_dtype(float)
            s.decomposition()
            ax = s.plot_explained_variance_ratio()
            
        # Clean up plot and present, allow user to select components by picker
        ax.set_title("")
        scree = ax.get_figure().canvas
        scree.draw()
        scree.setWindowTitle("Pick number of components")
        def clicked(event):
            components = round(event.xdata)
            # Num comp. picked, perform PCA, wrap new signal and plot
            sc = s.get_decomposition_model(components)
            scw = SignalWrapper(sc, self.ui, signal.name + "[PCA]")
            self.ui.signals.append(scw)
            # Close scree plot
            w = fig2win(scree.figure, self.ui.figures)
            w.close()
        scree.mpl_connect('button_press_event', clicked)
        
                        
                        
        
        