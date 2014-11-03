# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 18:47:05 2014

@author: vidarton
"""



def lstrip(string, prefix):
    if string is not None:
        if string.startswith(prefix):
            return string[len(prefix):]
            
def fig2win(fig, windows):
    # Each figure has FigureCanvas as widget, canvas has figure property
    matches = [w for w in windows if w.widget().figure == fig]
    return matches[0]
    
def win2fig(window):
    # Each figure has FigureCanvas as widget, canvas has figure property
    return window.widget().figure