# -*- coding: utf-8 -*-
"""
Created on Fri Dec 19 03:43:51 2014

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtCore
import hyperspy.drawing.utils

orig_on_figure_window_close = hyperspy.drawing.utils.on_figure_window_close
def _on_figure_window_close(figure, function):
    """Connects a close figure signal to a given function.

    Parameters
    ----------

    figure : mpl figure instance
    function : function

    """
    window = figure.canvas.manager.window
    if not hasattr(figure, '_on_window_close'):
        figure._on_window_close = list()
    if function not in figure._on_window_close:
        figure._on_window_close.append(function)

    # PyQt
    # In PyQt window.connect supports multiple funtions
    window.connect(window, QtCore.SIGNAL('closing()'), function)
    
    
def override_hyperspy():
    hyperspy.drawing.utils.on_figure_window_close = _on_figure_window_close