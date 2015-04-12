# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:43:47 2015

@author: Vidar Tonaas Fauske
"""

import sys
import os

pyw_executable = os.path.join(sys.prefix, "pythonw.exe")
shortcut_filename = "HyperSpyUI.lnk"
dirname = os.path.abspath('.')
script_path = os.path.join(dirname, "launch.py")
icon_path = os.path.join(dirname, 'images/icon/hyperspy.ico')

if sys.argv[1] == '-install':
    # Get paths to the desktop and start menu
    # TODO: Figure out if common or personal install
#    desktop_path = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
#    startmenu_path = get_special_folder_path("CSIDL_COMMON_STARTMENU")
    desktop_path = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
    startmenu_path = get_special_folder_path("CSIDL_STARTMENU")
    
    
    print 'Creating Shortcut'
    print pyw_executable
    print shortcut_filename
    print dirname
    print script_path
    print desktop_path
    print startmenu_path

    # Create shortcuts.
    for path in [desktop_path, startmenu_path]:
        create_shortcut(pyw_executable,
                    "A Graphical interface for HyperSpy",
                    os.path.join(path, shortcut_filename),
                    script_path,
                    dirname,
                    icon_path)