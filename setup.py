#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:58:16 2014

@author: Vidar Tonaas Fauske
"""

from setuptools import setup, find_packages

import hyperspyui.info

setup(name='hyperspyUI',
      version=hyperspyui.info.version,
      description='Hyperspy Graphical Interface',
      author='Vidar Tonaas Fauske',
      author_email='vidartf+hyperspyui@gmail.com',
      url='http://github.com/vidartf/hyperspyUI/',
      license='GPLv3',
      packages=find_packages(exclude=['tests*']),
      requires=['hyperspy',
                'matplotlib (>= 1.3)',
                'python_qt_binding',
                'pyqode.python',
                'autopep8',
                'traits',
                'traitsui'],
      install_requires=['hyperspy',  # TODO: Find lowest allowed version of hyperspy
                        'matplotlib >= 1.3',
                        'python_qt_binding',
                        'pyqode.python',
                        'autopep8',
                        'traits',
                        'traitsui'],
      package_data={
          'hyperspyui':
          ['images/*.svg',
           'images/*.png',
           'images/*.ico',
           'images/attributions.txt'],
      },
      scripts=['bin/register_linux_extensions.sh', 'bin/win_post_install.py',
               'bin/Register Windows extensions.bat'],
      )
