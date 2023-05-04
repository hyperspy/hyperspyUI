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

from setuptools import setup, find_namespace_packages

from hyperspyui.version import __version__


with open('README.rst') as file:
    long_description=file.read()


setup(
    name='hyperspyUI',
    version=__version__,
    description='Hyperspy Graphical User Interface',
    author='Vidar Tonaas Fauske',
    author_email='vidartf+hyperspyui@gmail.com',
    url='http://github.com/hyperspy/hyperspyUI/',
    license='GPLv3',
    packages=find_namespace_packages(exclude=[
            'doc', 'bin', 'doc.*', 'hyperspyui.plugins.user_plugins']),
    python_requires='~=3.7',
    install_requires=[
        # Add rosettasciio when it is released
        'hyperspy >= 1.7.2',
        'hyperspy-gui-traitsui >= 1.3.1',
        'matplotlib >= 3.0.3',
        'packaging',
        'pyqode.python >= 4.0.2',
        'pyqode.core >= 4.0.10',
        'pyface >=6.0.0',
        'pyflakes',
        'autopep8',
        'traits',
        'traitsui >=5.2.0',
        'qtconsole >=5.2.0',
        'ipykernel >=5.2.0',
        'qtpy',
        ],
    extras_require={
        ':sys_platform == "win32"': [
            'pywin32',
        ],
        'tests': [
            'pytest-qt',
            'pytest-cov',
            'pytest-timeout',
        ],
        'build-doc':[
            'sphinx >=1.7,!=5.2.0.post0', # https://github.com/sphinx-doc/sphinx/issues/10860
            'sphinx_rtd_theme',
            'sphinx-toggleprompt',
        ],
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
            'hyperspyui = hyperspyui.__main__:main',
         ]
    },
    keywords=[
    ],
    classifiers=[

        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
    long_description_content_type="text/x-rst",
    long_description=long_description,
    )
