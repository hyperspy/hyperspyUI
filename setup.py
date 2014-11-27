#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:58:16 2014

@author: Vidar Tonaas Fauske
"""

from distutils.core import setup

import hyperspyui.info

setup(name='hyperspyUI',
      version=hyperspyui.info.version,
      description='Hyperspy Graphical Interface',
      author='Vidar Tonaas Fauske',
      author_email='vidartf+hyperspyui@gmail.com',
      packages=['hyperspyui'],
      requires=['hyperspy', 
                'matplotlib (>= 1.3)', 
                'python_qt_binding',
                'traits',
                'traitsui'],
      install_requires=['hyperspy',     #TODO: Find lowest allowed version of hyperspy
                'matplotlib >= 1.3', 
                'python_qt_binding',
                'traits',
                'traitsui'],
      package_data=
      {
          'hyperspyui':
            ['images/*.svg',
            'images/*.png',
             'images/attribtutions.txt'],
     },
     url="https://github.com/vidartf/hyperspyUI",
     )