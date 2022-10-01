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
Created on Sun Apr 12 17:43:47 2015

@author: Vidar Tonaas Fauske
"""

import sys
import os
import subprocess

try:
    # HyperSpy >=2.0
    from rsciio import IO_PLUGINS
except Exception:
    # HyperSpy <2.0
    from hyperspy.io_plugins import io_plugins as IO_PLUGINS


def run_desktop_integration_windows(args):

    def create_shortcut(path, description, filename,
                        arguments="", workdir="", iconpath="",
                        iconindex=0):
        with open(filename, 'a'):
            pass    # Touch
        import pythoncom
        from win32com.shell import shell

        ilink = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        ilink.SetPath(path)
        ilink.SetDescription(description)
        if arguments:
            ilink.SetArguments(arguments)
        if workdir:
            ilink.SetWorkingDirectory(workdir)
        if iconpath or iconindex:
            ilink.SetIconLocation(iconpath, iconindex)
        # now save it.
        ipf = ilink.QueryInterface(pythoncom.IID_IPersistFile)
        ipf.Save(filename, 0)

    def get_special_folder_path(path_name):
        from win32com.shell import shell, shellcon

        for maybe in """
                CSIDL_COMMON_STARTMENU CSIDL_STARTMENU CSIDL_COMMON_APPDATA
                CSIDL_LOCAL_APPDATA CSIDL_APPDATA CSIDL_PROGRAM_FILES
                CSIDL_COMMON_DESKTOPDIRECTORY CSIDL_DESKTOPDIRECTORY
                CSIDL_COMMON_STARTUP CSIDL_STARTUP CSIDL_COMMON_PROGRAMS
                CSIDL_PROGRAMS CSIDL_PROGRAM_FILES_COMMON CSIDL_FONTS
                """.split():
            if maybe == path_name:
                csidl = getattr(shellcon, maybe)
                return shell.SHGetSpecialFolderPath(0, csidl, False)
        raise ValueError("%s is an unknown path ID" % (path_name,))

    pyw_executable = os.path.join(sys.prefix, "pythonw.exe")

    shortcut_filename = "HyperSpyUI.lnk"
    import hyperspyui
    dirname = os.path.dirname(hyperspyui.__file__)
    script_path = os.path.join(dirname, "__main__.py")
    icon_path = os.path.join(dirname, 'images', 'icon', 'hyperspy.ico')

    if args.remove:
        pass    # Should we delete registry entries? Maybe if not edited?
    else:
        if not args.no_shortcuts:
            # Get paths to the desktop and start menu
            print('Creating Shortcuts')
            try:
                desktop_path = get_special_folder_path(
                    "CSIDL_COMMON_DESKTOPDIRECTORY")
                startmenu_path = get_special_folder_path(
                    "CSIDL_COMMON_STARTMENU")

                # Create shortcuts.
                for path in [desktop_path, startmenu_path]:
                    create_shortcut(pyw_executable,
                                    "A Graphical interface for HyperSpy",
                                    os.path.join(path, shortcut_filename),
                                    '"%s"' % script_path,
                                    sys.prefix,
                                    icon_path)
            except IOError:
                # Try again with user folders
                desktop_path = get_special_folder_path(
                    "CSIDL_DESKTOPDIRECTORY")
                startmenu_path = get_special_folder_path("CSIDL_STARTMENU")

                # Create shortcuts.
                for path in [desktop_path, startmenu_path]:
                    create_shortcut(pyw_executable,
                                    "A Graphical interface for HyperSpy",
                                    os.path.join(path, shortcut_filename),
                                    '"%s"' % script_path,
                                    sys.prefix,
                                    icon_path)

        exclude_formats = [
            "netCDF", # old HyperSpy format.
            "Signal2D", # don't register it to open standard images
            "Protochips", # extension is csv
            ]
        filetypes = []
        for plugin in IO_PLUGINS:
            # Try first with attribute (HyperSpy <2.0), fallback with dictionary (RosettaSciIO)
            format_name = getattr(plugin, 'format_name', plugin['name'])
            file_extensions = getattr(plugin, 'file_extensions', plugin['file_extensions'])
            default_extension = getattr(plugin, 'default_extension', plugin['default_extension'])
            if format_name not in exclude_formats:
                defext = file_extensions[default_extension]
                filetypes.append("." + defext)

        if filetypes:
            d = dirname
            docname = "HyperSpy.Document"

            # Setup default icon
            cmd = r'1>nul 2>nul REG ADD "HKCR\%s\DefaultIcon" ' % docname
            cmd += '/t REG_SZ /f /d "' + d + r'\images\icon\hyperspy.ico"'

            # Try to register for all users (requires admin)
            r = subprocess.call(cmd, shell=True)
            cmds = []
            if r == 0:  # Everything OK, we're admin. Use ASSOC and FTYPE
                for ft in filetypes:
                    cmds.append(r'1>nul 2>nul ASSOC %s=%s' % (ft, docname))
                cmds.append(r'1>nul 2>nul FTYPE ' +
                            r'{0}="{1}" "'.format(docname, pyw_executable) +
                            d + r'\__main__.py" "%1" %*')
            else:
                # Not admin. We have to add everything to HKCU manually
                cmd = (r'1>nul 2>nul REG ADD ' +
                       r'"HKCU\Software\Classes\%s\DefaultIcon"' % docname) + \
                       r' /t REG_SZ /f /d "'
                cmd += d + r'\images\icon\hyperspy.ico"'
                cmds.append(cmd)
                for ft in filetypes:
                    cmds.append(
                        (r'1>nul 2>nul REG ADD "HKCU\Software\Classes\%s" ' %
                         ft) +
                        (r'/v "" /t REG_SZ /d "%s" /f' % docname))
                cmds.append(
                    r'1>nul 2>nul REG ADD ' +
                    (r'"HKCU\Software\Classes\%s\shell\open\command"' %
                     docname) +
                    r' /v "" /t REG_EXPAND_SZ /d ' +
                    (r'"\"%s\" "' % pyw_executable) +
                    d + r'\__main__.py" \"%1\" %*" /f')

            for cmd in cmds:
                subprocess.call(cmd, shell=True)
            print("File types registered: ", filetypes)
