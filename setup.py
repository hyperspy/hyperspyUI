#!/usr/bin/env python

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
Created on Mon Nov 17 11:58:16 2014

@author: Vidar Tonaas Fauske
"""

from setuptools import setup, find_packages

import hyperspyui.info

setup(
    name='hyperspyUI',
    version=hyperspyui.info.version,
    description='Hyperspy Graphical User Interface',
    author='Vidar Tonaas Fauske',
    author_email='vidartf+hyperspyui@gmail.com',
    url='http://github.com/hyperspy/hyperspyUI/',
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
              ],
    install_requires=['hyperspy >= 0.8.1',
                      'matplotlib >= 1.3',
                      'python_qt_binding',
                      'pyqode.python >= 2.6.0',
                      'autopep8',
                      'traits',
                      'traitsui',
                      'qtconsole',
                      ],
    extras_require={
        ':sys_platform == "win32"': [
            'pywin32',
        ]
    },
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
            'hyperspyui = hyperspyui.launch:main',
         ]
    },
    scripts=[
        'bin/hyperspyui_install.py',
        # 'bin/hyperspyui_reg_linux_extensions.sh',
    ],
    keywords=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
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
