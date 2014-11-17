#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:58:16 2014

@author: vidarton
"""

from distutils.core import setup

setup(name='hyperspyUI',
      version='1.0a',
      description='Hyperspy Graphical Interface',
      author='Vidar Tonaas Fauske',
      author_email='vidartf+hyperspyui@gmail.com',
      packages=['hyperspyui'],
      requires=['hyperspy', 
                'matplotlib (>= 1.4)', 
                'python_qt_binding'],
      package_data=
      {
          'hyperspyui':
            ['images/*.svg',
            'images/*.png',
             'images/attribtutions.txt'],
     },
     url="https://github.com/vidartf/hyperspyUI",
     )