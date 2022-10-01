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
Created on Mon Nov 17 14:16:41 2014

@author: Vidar Tonaas Fauske
"""


from qtpy import QtCore, QtWidgets

import types

from hyperspyui.exceptions import ProcessCanceled


def tr(text):
    return QtCore.QCoreApplication.translate("Threaded", text)


class Worker(QtCore.QObject):
    progress = QtCore.Signal(int)
    finished = QtCore.Signal()
    error = QtCore.Signal(str)

    def __init__(self, run):
        super().__init__()
        self.run_function = run

    def process(self):
        self.progress.emit(0)
        try:
            if isinstance(self.run_function, types.GeneratorType):
                p = 0
                self.progress.emit(p)
                while p < 100:
                    p = self.run_function()
                    self.progress.emit(p)
            else:
                self.run_function()
            self.progress.emit(100)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
            raise


class Threaded(QtCore.QObject):

    """
    Executes a user provided function in a new thread, and pops up a
    QProgressBar until it finishes. To have an updating progress bar,
    have the provided function be a generator, and yield completion rate
    in percent (int from 0 to 100).
    """

    pool = []

    @staticmethod
    def add_to_pool(instance):
        Threaded.pool.append(instance)

    @staticmethod
    def remove_from_pool(instance):
        Threaded.pool.remove(instance)

    def __init__(self, parent, run, finished=None):
        super().__init__(parent)

        # Create thread/objects
        self.thread = QtCore.QThread()
        worker = Worker(run)
        worker.moveToThread(self.thread)
        Threaded.add_to_pool(self)

        # Connect error reporting
        worker.error[str].connect(self.errorString)

        # Start up
        self.thread.started.connect(worker.process)

        # Clean up
        worker.finished.connect(self.thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(self.thread.quit)
        worker.error.connect(worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        if finished is not None:
            worker.finished.connect(finished)

        def remove_ref():
            Threaded.remove_from_pool(self)
        self.thread.finished.connect(remove_ref)

        # Need to keep ref so they stay in mem
        self.worker = worker

    def errorString(self, error):
        print(error)

    def run(self):
        self.thread.start()


class ProgressThreaded(Threaded):

    def __init__(self, parent, run, finished=None, label=None, cancellable=False,
                 title=tr("Processing"), modal=True, generator_N=None):
        self.modal = modal
        self.generator_N = generator_N

        # Create progress bar.
        progressbar = QtWidgets.QProgressDialog(parent)
        if isinstance(run, types.GeneratorType):
            progressbar.setMinimum(0)
            if generator_N is None:
                generator_N = 100
            elif generator_N <= 1:
                progressbar.setMaximum(0)
            else:
                progressbar.setMaximum(generator_N)
        else:
            progressbar.setMinimum(0)
            progressbar.setMaximum(0)

#        progressbar.hide()
        progressbar.setWindowTitle(title)
        progressbar.setLabelText(label)
        if not cancellable:
            progressbar.setCancelButtonText(None)

        if isinstance(run, types.GeneratorType):
            def run_gen():
                for p in run:
                    self.worker.progress[int].emit(p)
                    if self.progressbar.wasCanceled():
                        raise ProcessCanceled(tr("User cancelled operation"))

            super().__init__(parent, run_gen, finished)
        else:
            super().__init__(parent, run, finished)

        self.thread.started.connect(self.display)
        self.worker.finished.connect(self.close)
        self.worker.error.connect(self.close)
        self.worker.progress[int].connect(progressbar.setValue)
        self.progressbar = progressbar

    def display(self):
        if not self.thread.isFinished():
            if self.modal:
                self.progressbar.exec_()
            else:
                self.progressbar.show()

    def close(self):
        self.progressbar.close()
        self.progressbar.deleteLater()
