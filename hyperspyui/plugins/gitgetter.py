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

from hyperspyui.plugins.plugin import Plugin

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QDialogButtonBox
from qtpy.QtWidgets import (QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout,
                            QFormLayout, QDialog, QMessageBox, QLabel, QWidget,
                            QComboBox, QTextEdit)
from qtpy.QtCore import Qt

import os
import re
from collections import OrderedDict
import importlib
from functools import partial
from io import StringIO

from hyperspyui.util import block_signals


def check_git_repo(package_name):
    """
    Try to determine if the package "package_name" is installed as a source
    install from a git folder.
    """
    pkg_path = os.path.dname(importlib.util.find_spec(package_name).origin)
    while pkg_path:
        if os.path.exists(os.path.join(pkg_path, '.git')):
            return True
        pkg_path, dummy = os.path.split(pkg_path)
        if not dummy:
            break
    return False


def get_github_branches(repo_url):
    """
    Return a list of branches for the github repo at given URL.

    The branches are returned in the form of an ordered dictionary, with branch
    names as keys, and source zip URL as value.
    """
    import urllib.request
    branch_url = repo_url + '/branches/all'
    res = urllib.request.urlopen(branch_url)
    html = res.read().decode(res.headers.get_content_charset())
    names = re.findall(
        '<a href=".*?" class="branch-name css-truncate-target">(.*?)</a>',
        html)
    return OrderedDict(((n, repo_url + '/archive/%s.zip' % n) for n in names))

try:
    import git

    def check_git_cmd(prompt=True, parent=None):
        """
        Check if we have git.exe. If not prompt for its location (if `prompt`
        is True).
        """
        try:
            git.Git().status()
            return True
        except git.cmd.GitCommandNotFound:
            if prompt:
                ext_filt = '*.exe' if os.name == 'NT' else None
                path = QtWidgets.QFileDialog.getOpenFileName(
                    parent, tr('Specify git executable'),
                    git.Git.GIT_PYTHON_GIT_EXECUTABLE, ext_filt)
                # Pyside returns tuple, PyQt not
                if isinstance(path, (tuple, list)):
                    path = path[0]
                if path and os.path.exists(path):
                    git.Git.GIT_PYTHON_GIT_EXECUTABLE = path
                    return check_git_cmd(parent)
            return False

    def get_git_branches(package_name, fetch=False):
        """
        Get both local and remote branches for the local git repo of
        `package_name`. Ensure that the package has a local repo by calling
        `check_git_repo` first.
        """
        pkg_path = imp.find_module(package_name)[1]
        r = git.Repo(pkg_path, search_parent_directories=True)
        # Start with active branch:
        try:
            branches = OrderedDict(((r.active_branch.name, r.active_branch),))
        except TypeError:
            # active branch is detached
            branches = OrderedDict((("<Detached HEAD>", None),))
        # Add local branches:
        branches.update(((b.name, b) for b in r.heads))

        # Add remote branches:
        for remote in r.remotes:
            try:
                if fetch:
                    remote.fetch()
            except git.GitCommandError:
                continue
            # Don't include PRs in list
            branches.update(((b.name, b) for b in remote.refs if
                             '/pr/' not in b.name))
        return branches

    got_git = True
    use_git = True

except ImportError:
    got_git = False
    use_git = False


def get_branches(package_name, url):
    """
    Either get git branches, or fetch branches from github.com
    """
    if use_git and check_git_repo(package_name):
        return get_git_branches(package_name)
    else:
        return get_github_branches(url)


def checkout_branch(branch, stream=None):
    """
    If `branch` is a string, assume it is archive url. Try to install by pip.
    Otherwise `branch` is assumed by a branch object from the `git` package,
    which will be attempted to be checked out.
    """
    if branch is None:
        return
    if isinstance(branch, str):
        import pip
        import sys

        class WrapDownloadProgressBar(pip.download.DownloadProgressBar):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.file = stream

        class WrapDownloadProgressBarSpinner(
                pip.download.DownloadProgressSpinner):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.file = stream
        ic = pip.commands.InstallCommand()
        ic.log_streams = (stream, stream)
        old_classes = (pip.download.DownloadProgressBar,
                       pip.download.DownloadProgressSpinner)
        pip.download.DownloadProgressBar = WrapDownloadProgressBar
        pip.download.DownloadProgressSpinner = WrapDownloadProgressBarSpinner
        stdout_set = False
        if sys.__stdout__ is None:
            sys.__stdout__ = sys.stdout
            stdout_set = True
        try:
            ic.main(['--no-deps', '-I', branch])
            ic.main([branch])
        finally:
            if stdout_set:
                sys.__stdout__ = None  # Let's leave things as we found them.
            (pip.download.DownloadProgressBar,
             pip.download.DownloadProgressSpinner) = old_classes
    else:
        try:
            branch.checkout()
        except git.GitCommandError as e:
            mb = QMessageBox(QMessageBox.Critical, tr("Git checkout failed"),
                             e.stderr)
            mb.exec_()
            raise ValueError()


def tr(text):
    return QtCore.QCoreApplication.translate("GitSelector", text)


class GitSelector(Plugin):
    name = "Version selector"

    def __init__(self, main_window):
        super().__init__(main_window)
        self.settings.set_default('check_for_updates_on_start', True)
        self.settings.set_default('check_for_git_updates', False)
        self.packages = {
            'HyperSpy': [True, 'https://github.com/hyperspy/hyperspy'],
            'HyperSpyUI': [True, 'https://github.com/hyperspy/hyperspyui'],
            }
        self.ui.load_complete.connect(self._on_load_complete)
        if got_git:
            git.Git.GIT_PYTHON_GIT_EXECUTABLE = \
                    self.settings['git_executable'] or ''

    def create_actions(self):
        self.add_action(
            self.name + '.show_dialog', self.name, self.show_dialog,
            tip="Open dialog to select branch/version of HyperSpy/HyperSpyUI",)
        self.add_action(
            self.name + '.update_check', "Check for updates",
            self.update_check,
            tip="Check for new versions of HyperSpy/HyperSpyUI",)

    def _check_git(self):
        for package_name in self.packages.keys():
            if check_git_repo(package_name.lower()):
                git_ok = use_git
                if git_ok:
                    git_ok = check_git_cmd(True, self.ui)
                    self.settings['git_executable'] = \
                        git.Git.GIT_PYTHON_GIT_EXECUTABLE
                self.packages[package_name][0] = git_ok

    def create_menu(self):
        self.add_menuitem('Settings',
                          self.ui.actions[self.name + '.show_dialog'])
        self.add_menuitem('Settings',
                          self.ui.actions[self.name + '.update_check'])

    def _on_load_complete(self):
        if self.settings['check_for_updates_on_start', bool]:
            self.update_check(silent=True)

    def _perform_update(self, package):
        stream = VisualLogStream(self.ui)
        try:
            checkout_branch(package, stream)
        finally:
            diag = getattr(stream, 'dialog', None)
            if diag is not None:
                diag.btn_close.setEnabled(True)

    def update_check(self, silent=False):
        """
        Checks for updates to hyperspy and hyperspyUI.

        If the packages are not source installs, it checks for a new version on
        PyPI.

        Parameters
        ----------
        silent: bool
            If not silent (default), a message box will appear if no
            updates are available, with a message to that fact.

        Returns
        -------
        None.

        """
        self._check_git()
        available = {}
        for Name, (enabled, url) in self.packages.items():
            name = Name.lower()
            if enabled:
                if (check_git_repo(name) and
                        self.settings['check_for_git_updates', bool]):
                    # TODO: Check for commits to pull
                    pass
                else:
                    import xmlrpc.client
                    pypi = xmlrpc.client.ServerProxy(
                        'https://pypi.python.org/pypi')
                    found = pypi.package_releases(name)
                    if not found:
                        # Try to capitalize pkg name
                        if name == 'hyperspyui':
                            found = pypi.package_releases('hyperspyUI', True)
                        else:
                            found = pypi.package_releases(Name, True)
                    if found:
                        import pip
                        dist = [d for d in pip.get_installed_distributions()
                                if d.project_name.lower() == name]
                        if dist[0].version < found[0]:
                            available[name] = found[0]

        if available:
            w = self._get_update_list(available.keys())
            diag = self.ui.show_okcancel_dialog("Updates available", w)
            if diag.result() == QDialog.Accepted:
                for chk in w.children():
                    if isinstance(chk, QtWidgets.QCheckBox):
                        name = chk.text()
                        if available[name]:
                            name += '==' + available[name]
                        self._perform_update(name)
        elif not silent:
            mb = QMessageBox(QMessageBox.Information, tr("No updates"),
                             tr("No new updates were found."),
                             parent=self.ui)
            mb.exec_()

    def _get_update_list(self, names):
        w = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(tr("The following updates are available. Do you "
                                 "want to update them?")))
        for n in names:
            vbox.addWidget(QCheckBox(n))
        w.setLayout(vbox)
        return w

    def show_dialog(self):
        if len(self.dialogs) > 0:
            diag = self.dialogs[0]
        else:
            self._check_git()
            diag = VersionSelectionDialog(self, self.ui)
        self.open_dialog(diag)


class VersionSelectionDialog(QDialog):

    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.packages = plugin.packages
        self._prev_indices = {}
        self.create_controls()

    def _cbo_changed(self, cbo, index):
        branch = cbo.itemData(index)
        stream = VisualLogStream(self.plugin.ui)
        try:
            checkout_branch(branch, stream)
        except ValueError:
            with block_signals(cbo):
                cbo.setCurrentIndex(self._prev_indices[cbo])
        finally:
            diag = getattr(stream, 'dialog', None)
            if diag is not None:
                diag.btn_close.setEnabled(True)
        self._prev_indices[cbo] = index

    def create_controls(self):
        self.setWindowTitle(tr(self.plugin.name))

        vbox = QVBoxLayout()
        form = QFormLayout()
        for Name, (enabled, url) in self.packages.items():
            name = Name.lower()
            cbo = QComboBox()
            if enabled:
                branches = get_branches(name, url)
                for n, b in branches.items():
                    cbo.addItem(n, b)
                if not check_git_repo(name):
                    cbo.insertItem(0, "<Select to change>", None)
                cbo.setCurrentIndex(0)
                self._prev_indices[cbo] = 0
                cbo.currentIndexChanged.connect(
                    partial(self._cbo_changed, cbo))
            else:
                cbo.setEditText("<git repository>")
                cbo.setToolTip(tr(
                    "This is installed in a git repository but we're set to "
                    "not use git."))
            cbo.setEnabled(enabled)
            form.addRow(Name + ':', cbo)

        vbox.addLayout(form)
        vbox.addWidget(QLabel(tr(
            "You should restart the application if you make any changes!")))

        btns = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        vbox.addWidget(btns)
        self.setLayout(vbox)


class VisualLogStream(StringIO):
    def __init__(self, parent=None, buf=''):
        super().__init__(self, buf)
        self.parent = parent
        self.dialog = None
        self.ignore = ['\x1b[?25l', '\x1b[?25h', '']
        self.clearln = '\r\x1b[K'

    def _ensure_dialog(self):
        if self.dialog is None:
            self.dialog = PipOutput(self.parent)
            self.dialog.setModal(True)
            self.dialog.show()

    def isatty(self):
        if self.closed:
            raise ValueError("Cannot call isatty when stream is closed.")
        return True

    def write(self, s):
        if s in self.ignore:
            return
        if s == self.clearln:
            v = self.getvalue()
            pos = v.rfind('\n', 0, len(v)-1)
            if pos > 0:
                self.truncate(pos+1)
                self.seek(pos+1)
        else:
            super().write(self, s)
            self._ensure_dialog()
            self.dialog.output.setPlainText(self.getvalue())
            QtWidgets.QApplication.processEvents()


class PipOutput(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_controls()

    def sizeHint(self):
        def_sz = super().sizeHint()
        def_sz.setWidth(500)
        return def_sz

    def create_controls(self):
        self.setWindowTitle(tr("Updating via pip"))

        wFlags = self.windowFlags()
        if Qt.WindowCloseButtonHint == (wFlags & Qt.WindowCloseButtonHint):
            wFlags ^= Qt.WindowCloseButtonHint
            self.setWindowFlags(wFlags)
        vbox = QVBoxLayout()
        self.output = QTextEdit()
        if self.parent() and hasattr(self.parent(), 'console'):
            self.output.setFont(self.parent().console.font)
        vbox.addWidget(self.output)
        hbox = QHBoxLayout()
        hbox.addStretch()
        self.btn_close = QPushButton(tr("Close"))
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setEnabled(False)
        hbox.addWidget(self.btn_close)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
