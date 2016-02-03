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
Created on Fri Dec 12 23:57:20 2014

@author: Vidar Tonaas Fauske
"""

import os
import glob
modules = glob.glob(os.path.dirname(__file__) + "/*.py")
# modules.extend(glob.glob(os.path.dirname(__file__)+"/*.py?"))
# TODO: In release form, we should support compiled plugins in pyc/pyo format
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in modules
           if not os.path.basename(f).startswith('_')]
if os.path.exists(os.path.join(os.path.dirname(__file__), "user_plugins")):
    modules = glob.glob(os.path.dirname(__file__) + "/user_plugins/*.py")
    __all__.extend(['.'.join(('user_plugins',
                             os.path.splitext(os.path.basename(f))[0]))
                   for f in modules
                   if not os.path.basename(f).startswith('_')])
__all__ = list(set(__all__))    # Make unique as py/pyc/pyo all match
