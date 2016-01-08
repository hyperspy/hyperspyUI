#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 11:58:16 2014

@author: Vidar Tonaas Fauske
"""

import os
from setuptools import setup, find_packages

import hyperspyui.info

platform_req = []
if os.name == 'nt':
    platform_req.append('pywin32')

setup(
    name='hyperspyUI',
    version=hyperspyui.info.version,
    description='Hyperspy Graphical User Interface',
    author='Vidar Tonaas Fauske',
    author_email='vidartf+hyperspyui@gmail.com',
    url='http://github.com/vidartf/hyperspyUI/',
    license='GPLv3',
    packages=find_packages(exclude=['tests*',
                                    'hyperspyui.plugins.user_plugins']),
    requires=['hyperspy (>= 0.8.1)',
              'matplotlib (>= 1.3)',
              'python_qt_binding',
              'pyqode.python (>= 2.6.0)',
              'autopep8',
              'traits',
              'traitsui',
              'qtconsole',
              ] + platform_req,
    install_requires=['hyperspy >= 0.8.1',
                      'matplotlib >= 1.3',
                      'python_qt_binding',
                      'pyqode.python >= 2.6.0',
                      'autopep8',
                      'traits',
                      'traitsui',
                      'qtconsole',
                      ] + platform_req,
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
            'HyperSpyUI = hyperspyui:main',
         ]
    },
    scripts=[
        'bin/hyperspyui_install.py',
        # 'bin/hyperspyui_reg_linux_extensions.sh',
    ],
    keywords=[
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    )
