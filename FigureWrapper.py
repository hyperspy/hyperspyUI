# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 18:27:15 2014

@author: vidarton
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from util import lstrip
import FigureManager

class FigureWrapper(QDockWidget):
    def __init__(self, fig, ui_parent=None, on_close=None):
        super(FigureWrapper, self).__init__(ui_parent)
        
        self.signal = None
        
        self._set_fig(fig)
        
        self.setWindowTitle(self.title)
        self.fig.tight_layout()
        
        self.on_close = on_close
        self.connect(self, SIGNAL('visibilityChanged(bool)'), self._on_close)
        
        f = FigureManager.FigureManager.Instance()
        f.add(self)
    
    def draw(self):
        self.canvas.draw()
        
    def _set_fig(self, fig):
        frame = QWidget(self)
        self.fig = fig
        if fig.canvas is None:
            self.canvas = FigureCanvas(self.fig)
        else:
            self.canvas = fig.canvas
        self.title = lstrip(self.canvas.get_window_title(), "Figure ")
        self.fig.axes[0].set_title("")
#        self.canvas.set_window_title("")
        self.canvas.setParent(frame)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        frame.setLayout(vbox)
        self.setWidget(frame)
        
    def change_fig(self, newfig):
        self._set_fig(newfig)
        self.setWindowTitle(self.title)
        self.fig.tight_layout()
        self.draw()
        
    def close(self):
        self.disconnect(self, SIGNAL('visibilityChanged(bool)'), self._on_close)
        super(FigureWrapper, self).close()
        f = FigureManager.FigureManager.Instance()
        f.remove(self) 
        
    def _on_close(self, vis):
        if not vis:
            self.close()
            if self.on_close is not None:
                self.on_close()