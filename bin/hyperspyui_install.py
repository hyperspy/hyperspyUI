# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:43:47 2015

@author: Vidar Tonaas Fauske
"""

import sys
import os
import platform
import subprocess


if platform.system().lower() == 'windows':
    try:
        create_shortcut
    except NameError:
        # Create a function with the same signature as create_shortcut provided
        # by bdist_wininst
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

        # Support the same list of "path names" as bdist_wininst.
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

    # import sys
    # import win32com.shell.shell as shell
    # ASADMIN = 'asadmin'
    #
    # if sys.argv[-1] != ASADMIN:
    #    script = os.path.abspath(sys.argv[0])
    #    params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
    #    shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable,
    #                         lpParameters=params)
    #    sys.exit(0)

    pyw_executable = os.path.join(sys.prefix, "pythonw.exe")

    shortcut_filename = "HyperSpyUI.lnk"
    import hyperspyui
    dirname = os.path.dirname(hyperspyui.__file__)
    script_path = os.path.join(dirname, "launch.py")
    icon_path = os.path.join(dirname, 'images', 'icon', 'hyperspy.ico')

    if (len(sys.argv) <= 1) or (sys.argv[1] != '-remove'):
        # Get paths to the desktop and start menu
        print('Creating Shortcuts')
        try:
            desktop_path = get_special_folder_path(
                "CSIDL_COMMON_DESKTOPDIRECTORY")
            startmenu_path = get_special_folder_path("CSIDL_COMMON_STARTMENU")

            # Create shortcuts.
            for path in [desktop_path, startmenu_path]:
                create_shortcut(pyw_executable,
                                "A Graphical interface for HyperSpy",
                                os.path.join(path, shortcut_filename),
                                script_path,
                                dirname,
                                icon_path)
        except IOError as e:
            desktop_path = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
            startmenu_path = get_special_folder_path("CSIDL_STARTMENU")

            # Create shortcuts.
            for path in [desktop_path, startmenu_path]:
                create_shortcut(pyw_executable,
                                "A Graphical interface for HyperSpy",
                                os.path.join(path, shortcut_filename),
                                script_path,
                                dirname,
                                icon_path)

        d = dirname
        docname = "HyperSpy.Document"
        filetypes = ['.msa', '.hdf5', '.dens', '.blo']

        # Setup default icon
        cmd = r'1>nul 2>nul REG ADD "HKCR\%s\DefaultIcon" ' % docname
        cmd += '/t REG_SZ /f /d ' + d + r'\images\icon\hyperspy.ico'

        # Try to register for all users (requires admin)
        r = subprocess.call(cmd, shell=True)
        cmds = []
        if r == 0:  # Everything OK, we're admin. Use ASSOC and FTYPE
            for ft in filetypes:
                cmds.append(r'1>nul 2>nul ASSOC %s=%s' % (ft, docname))
            cmds.append(r'1>nul 2>nul FTYPE ' +
                        r'{0}="%PYTHONPATH%pythonw.exe" '.format(docname) +
                        d + r'\launch.py "%1" %*')
        else:
            # Not admin. We have to add everything to HKCU
            cmd = (r'1>nul 2>nul REG ADD ' +
                   '"HKCU\Software\Classes\%s\DefaultIcon' % docname) + \
                   r'" /t REG_SZ /f /d '
            cmd += d + r'\images\icon\hyperspy.ico'
            cmds.append(cmd)
            for ft in filetypes:
                cmds.append(
                    (r'1>nul 2>nul REG ADD "HKCU\Software\Classes\%s" ' % ft) +
                    (r'/v "" /t REG_SZ /d "%s" /f' % docname))
            cmds.append(
                r'1>nul 2>nul REG ADD ' +
                (r'"HKCU\Software\Classes\%s\shell\open\command"' % docname) +
                r' /v "" /t REG_EXPAND_SZ /d "\"%PYTHONPATH%pythonw.exe\" ' +
                d + r'\launch.py \"%1\" %*" /f')

        for cmd in cmds:
            r = subprocess.call(cmd, shell=True)
            r
        print("File types registered")
    elif len(sys.argv) > 0 and sys.argv[1] == '-remove':
        pass    # Should we delete registry entries? Maybe if not edited?
