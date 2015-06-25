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
      packages=find_packages(exclude=['tests*',
                                      'hyperspyui.plugins.user_plugins']),
      requires=['hyperspy',
                'matplotlib (>= 1.3)',
                'python_qt_binding',
                'pyqode.python (== 2.5.0)',
                'autopep8',
                'traits',
                'traitsui'],
      install_requires=['hyperspy',  # TODO: Find lowest allowed version of hyperspy
                        'matplotlib >= 1.3',
                        'python_qt_binding',
                        'pyqode.python == 2.5.0',
                        'autopep8',
                        'traits',
                        'traitsui'],
      package_data={
          'hyperspyui':
          ['images/*.svg',
           'images/*.png',
           'images/*.ico',
           'images/icon/*.png',
           'images/icon/*.ico',
           'images/attributions.txt',
           'ipython_profile/*'],
      },
      entry_points={
          'gui_scripts': [
              'HyperSpyUI = hyperspyui.launch:main',
           ]
      },
      scripts=[
          'bin/hyperspyui_install.py',
          # 'bin/hyperspyui_reg_linux_extensions.sh',
      ],
      )
