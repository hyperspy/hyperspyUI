# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 18:47:05 2014

@author: vidarton
"""



def lstrip(string, prefix):
    if string is not None:
        if string.startswith(prefix):
            return string[len(prefix):]