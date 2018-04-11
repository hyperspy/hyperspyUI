# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:57:20 2014

@author: Vidar Tonaas Fauske
"""

import os
import glob
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
# modules.extend(glob.glob(os.path.dirname(__file__)+"/*.py?"))
# TODO: In release form, we should support compiled plugins in pyc/pyo format
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in modules
           if not os.path.basename(f).startswith('_')]
__all__ = list(set(__all__))    # Make unique as py/pyc/pyo all match
