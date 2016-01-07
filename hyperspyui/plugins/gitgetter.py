# -*- coding: utf-8 -*-


from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.widgets.extendedqwidgets import ExToolWindow

import os
from collections import OrderedDict
import imp
from functools import partial
from io import StringIO


def check_git_repo(package_name):
    pkg_path = imp.find_module(package_name)[1]
    while pkg_path:
        if os.path.exists(pkg_path + os.path.sep + '.git'):
            return True
        pkg_path, dummy = os.path.split(pkg_path)
        if not dummy:
            break
    return False


def get_github_branches(repo_url):
    import re
    import urllib.request, urllib.error, urllib.parse
    branch_url = repo_url + '/branches/all'
    html = urllib.request.urlopen(branch_url).read()
    names = re.findall(
        '<a href=".*?" class="branch-name css-truncate-target">(.*?)</a>',
        html)
    return OrderedDict(((n, repo_url + '/archive/%s.zip' % n) for n in names))

try:
    import git

    def check_git_cmd(prompt=True, parent=None):
        try:
            git.Git().status()
            return True
        except git.cmd.GitCommandNotFound:
            if prompt:
                ext_filt = '*.exe' if os.name == 'NT' else None
                path = QFileDialog.getOpenFileName(
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
    if use_git and check_git_repo(package_name):
        return get_git_branches(package_name)
    else:
        return get_github_branches(url)


def checkout_branch(branch, stream=None):
    if branch is None:
        return
    if isinstance(branch, str):
        import pip
        ic = pip.commands.InstallCommand()
        ic.log_streams = (stream, stream)
        old_files = (pip.download.DownloadProgressBar.file,
                     pip.download.DownloadProgressSpinner.file)
        pip.download.DownloadProgressBar.file = stream
        pip.download.DownloadProgressSpinner.file = stream
        try:
            ic.main(['-U', branch])
        finally:
            (pip.download.DownloadProgressBar.file,
             pip.download.DownloadProgressSpinner.file) = old_files
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
        super(GitSelector, self).__init__(main_window)
        if got_git:
            git.Git.GIT_PYTHON_GIT_EXECUTABLE = \
                    self.settings['git_executable'] or ''

    def create_actions(self):
        self.add_action(
            self.name + '.show_dialog', self.name, self.show_dialog,
            tip="Open dialog to select branch/version of HyperSpy/HyperSpyUI",)

    def create_menu(self):
        self.add_menuitem('Settings',
                          self.ui.actions[self.name + '.show_dialog'])

    def show_dialog(self):
        if len(self.dialogs) > 0:
            diag = self.dialogs[0]
        else:
            diag = VersionSelectionDialog(self, self.ui)
        self.open_dialog(diag)


class VersionSelectionDialog(QDialog):

    def __init__(self, plugin, parent=None):
        super(VersionSelectionDialog, self).__init__(parent)
        self.plugin = plugin
        self.packages = {
            'HyperSpy': [True, 'https://github.com/hyperspy/hyperspy'],
            'HyperSpyUI': [True, 'https://github.com/vidartf/hyperspyui'],
            }
        for package_name in self.packages.keys():
            if check_git_repo(package_name.lower()):
                git_ok = use_git
                if git_ok:
                    git_ok = check_git_cmd(True, parent)
                    self.plugin.settings['git_executable'] = \
                        git.Git.GIT_PYTHON_GIT_EXECUTABLE
                if not git_ok:
                    self.packages[package_name][0] = False
#                    msg = tr('Package "%s" is in a git repo, but set to not '
#                             'use git.') % package_name
        self._prev_indices = {}
        self.create_controls()

    def _cbo_changed(self, cbo, index):
        branch = cbo.itemData(index)
        stream = VisualLogStream(self.plugin.ui)
        try:
            checkout_branch(branch, stream)
        except ValueError:
            old = cbo.blockSignals
            cbo.blockSignals = True
            cbo.setCurrentIndex(self._prev_indices[cbo])
            cbo.blockSignals = old
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
        StringIO.__init__(self, buf)
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
        else:
            StringIO.write(self, s)
            self._ensure_dialog()
            self.dialog.output.setPlainText(self.getvalue())
            QApplication.processEvents()


class PipOutput(QDialog):

    def __init__(self, parent=None):
        super(PipOutput, self).__init__(parent)
        self.create_controls()

    def sizeHint(self):
        def_sz = super(PipOutput, self).sizeHint()
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
