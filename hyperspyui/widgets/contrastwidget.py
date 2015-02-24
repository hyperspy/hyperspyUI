# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 16:49:48 2014

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from extendedqwidgets import ExDoubleSlider, ExClickLabel
from hyperspy.drawing.mpl_he import MPL_HyperExplorer
from hyperspy.drawing.image import ImagePlot
from hyperspyui.util import win2fig

import numpy as np
from matplotlib.colors import Normalize, SymLogNorm

def fig2plot(fig, signals):
    for s in signals:
        p = s.signal._plot
        if isinstance(p, MPL_HyperExplorer):
            if isinstance(p.signal_plot, ImagePlot):
                if p.signal_plot.figure is fig:
                    return p.signal_plot
            elif isinstance(p.navigator_plot, ImagePlot):
                if p.navigator_plot.figure is fig:
                    return p.navigator_plot
    return None

class ContrastWidget(QDockWidget):
    LevelLabel = "Level"  # TODO: tr
    WindowLabel = "Window"  # TODO: tr
    
    def __init__(self, parent, figure=None):
        super(ContrastWidget, self).__init__(parent)
        self.setWindowTitle("Contrast control")
        self.create_controls()     
        
        self.cur_figure = None
        self.on_figure_change(figure)
        
    def on_figure_change(self, figure):
        if isinstance(figure, QMdiSubWindow):
            figure = win2fig(figure)
        
        self.cur_figure = figure
        signals = self.parent().signals
        p = fig2plot(self.cur_figure, signals)
        self._cur_plot = p
        self.update_controls_from_fig()
    
    def _plot_minmax(self):
        p = self._cur_plot
        if p is None:
            return 0.0, 0.0
        data = p.data_function().ravel()
        return np.nanmin(data), np.nanmax(data)
    
    def update_controls_from_fig(self):
        p = self._cur_plot
        if p is None:
            self.sl_level.setValue(0.0)
            self.sl_window.setValue(0.0)
            self.chk_log.setChecked(False)
            self.disable()
        else:
            self.enable()
            imin, imax = self._plot_minmax()
            
            old = self.sl_level.blockSignals(True)
            self.sl_level.setRange(imin, imax)
            self.sl_level.setValue(p.vmin)
            self.lbl_level.setText(self.LevelLabel + ": %.2G" % p.vmin)
            self.sl_level.blockSignals(old)
            
            old = self.sl_window.blockSignals(True)
            self.sl_window.setRange(0, imax-imin)
            window = p.vmax - p.vmin
            self.sl_window.setValue(window)
            self.lbl_window.setText(self.WindowLabel + ": %.2G" % window)
            self.sl_window.blockSignals(old)
            
            old = self.chk_auto.blockSignals(True)
            self.chk_auto.setChecked(p.auto_contrast)
            self.sl_level.setEnabled(not p.auto_contrast)
            self.sl_window.setEnabled(not p.auto_contrast)
            self.chk_auto.blockSignals(old)
            
            if p.ax.images:
                old = self.chk_log.blockSignals(True)
                self.chk_log.setEnabled(True)
                norm = isinstance(p.ax.images[-1].norm, SymLogNorm)
                self.chk_log.setChecked(norm)
                self.chk_log.blockSignals(old)
            else:
                self.chk_log.setEnabled(False)
    
    def level_changed(self, value):
        self.lbl_level.setText(self.LevelLabel + ": %.2G" % value)
        p = self._cur_plot
        if p is not None:
            p.vmin = self.sl_level.value()
            p.vmax = self.sl_level.value() + self.sl_window.value()
            p.update()
    
    def window_changed(self, value):
        self.lbl_window.setText(self.WindowLabel + ": %.2G" % value)
        p = self._cur_plot
        if p is not None:
            p.vmax = self.sl_level.value() + self.sl_window.value()
            p.update()
            
    def log_changed(self, value):
        p = self._cur_plot
        if p is not None and p.ax.images:
            old = p.ax.images[0].norm
            kw = dict(vmin=old.vmin, vmax=old.vmax, clip=old.clip)
            if value:
                n = SymLogNorm(1e-9, **kw)
            else:
                n = Normalize(**kw)
            p.ax.images[-1].norm = n
            p.update()
    
    def enable(self, enabled=True):
        self.lbl_level.setEnabled(enabled)
        self.lbl_window.setEnabled(enabled)
        self.sl_level.setEnabled(enabled)
        self.sl_window.setEnabled(enabled)
        self.chk_auto.setEnabled(enabled)
        self.chk_log.setEnabled(enabled)
    
    def disable(self):
        self.enable(False)
        
    def auto(self, checked):
        p = self._cur_plot
        if p is not None:
            p.auto_contrast = checked
            p.update()
            self.update_controls_from_fig()
            self.sl_level.setEnabled(not checked)
            self.sl_window.setEnabled(not checked)
            
    def reset_level(self):
        imin, imax = self._plot_minmax()
        self.sl_level.setValue(imin)   # Will trigger events
        
    def reset_window(self):
        imin, imax = self._plot_minmax()
        self.sl_window.setValue(imax - imin)   # Will trigger events
    
    def create_controls(self):
        self.sl_level = ExDoubleSlider(self, Qt.Horizontal)
        self.lbl_level = ExClickLabel(self.LevelLabel + ": 0.0")
        self.sl_window = ExDoubleSlider(self, Qt.Horizontal)
        self.lbl_window = ExClickLabel(self.WindowLabel + ": 0.0")
        
        for sl in [self.sl_level, self.sl_window]:
            sl.setRange(0.0, 1.0)
            sl.setValue(0.0)
            
        self.chk_auto = QCheckBox("Auto", self) # TODO: tr
        self.chk_log = QCheckBox("Log", self)   # TODO: tr
            
        self.lbl_level.clicked.connect(self.reset_level)
        self.lbl_window.clicked.connect(self.reset_window)
        self.sl_level.valueChanged[float].connect(self.level_changed)
        self.sl_window.valueChanged[float].connect(self.window_changed)
        self.connect(self.chk_auto, SIGNAL('toggled(bool)'), self.auto)
        self.connect(self.chk_log, SIGNAL('toggled(bool)'), self.log_changed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chk_auto)    
        hbox.addWidget(self.chk_log)
        vbox = QVBoxLayout()
        for w in [self.sl_level, self.lbl_level,
                  self.sl_window, self.lbl_window]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)
            
        wrap = QWidget()
        wrap.setLayout(vbox)
        height = vbox.sizeHint().height()
        wrap.setFixedHeight(height)
        self.setWidget(wrap)