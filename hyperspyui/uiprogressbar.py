# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 19:11:19 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtCore
from QtCore import QObject, Signal, SIGNAL

import hyperspy.external.progressbar
import time

from hyperspyui.exceptions import ProcessCanceled

# Create signal object which will handle all events
signaler = QObject()
signaler.created = Signal(object)
signaler.progress = Signal((object, int), (object, int, str))
signaler.finished = Signal(object)
signaler.cancel = Signal(int)
# This is necessary as it bugs out if not (it's a daisy chained event)


def _on_cancel(pid):
    signaler.emit(SIGNAL('cancel(int)'), pid)
signaler.on_cancel = _on_cancel

# Hook function


def _wrap(*args, **kwargs):
    """
    Replacement function for hyperspy.external.progressbar.progressbar().
    Causes a UIProgressBar() to be made, which the MainWindow can connect to
    in order to create a progress indicator. It is important that the
    connection is made with QtCore.Signals, as they are thread aware, and the
    signal is processed on the GUI main event loop, i.e. the main thread. This
    is necessary as all UI operations have to happen on the main thread, and
    the hyperspy processing might be pushed to a worker thread "threaded.py".
    """
    disabled = kwargs.pop('disabled', False)
    maxval = kwargs.pop('maxval', 100)
    text = kwargs.pop('text', "")
    if disabled:
        return hyperspy.external.progressbar.DummyProgressBar()
    else:
        widgets = [text, "bar",
                   hyperspy.external.progressbar.ETA()]
        return UIProgressBar(widgets=widgets, maxval=maxval).start()

# Override hyperspy prgoressbar implementation
orig = hyperspy.external.progressbar.progressbar


def takeover_progressbar():
    """
    Replace hyperspy.external.progressbar.progressbar() with uiprogressbar.wrap().
    The main_window will be connected to all the events whenever a progressbar
    is created.
    """
    hyperspy.external.progressbar.progressbar = _wrap


def reset_progressbar():
    hyperspy.external.progressbar.progressbar = orig


class UIProgressBar(hyperspy.external.progressbar.ProgressBar):

    """
    Connector between hyperspy process with a progressbar, and the UI. See also
    the doc for wrap() for more details.
    """
    uid = 1

    def __init__(self, maxval=100, widgets=[""]):
        self.cancelled = False
        self.id = self.uid
        self.uid += 1

        assert maxval >= 0
        self.maxval = maxval
        self.signal_set = False

        global signaler
        signaler.connect(signaler, SIGNAL('cancel(int)'),
                         self.cancel)

        self.widgets = widgets

        self.currval = 0
        self.finished = False
        self.start_time = None
        self.seconds_elapsed = 0

    def cancel(self, pid):
        """
        Slot for the UI to call if it wants to cancel the process. Thread safe.
        """
        if pid == self.id:
            self.cancelled = True

    def update(self, value):
        """
        Updates the progress bar to a new value. Called by the hyperspy side.
        Not safe to call from UI.
        """
        if self.cancelled is True:
            raise ProcessCanceled("User cancelled operation")
        assert 0 <= value <= self.maxval
        self.currval = value
        if not self.start_time:
            self.start_time = time.time()
        self.seconds_elapsed = time.time() - self.start_time
        has_eta = False
        global signaler
        for w in self.widgets:
            if isinstance(w, hyperspy.external.progressbar.ETA):
                has_eta = True
                eta = w.update(self)
                txt = self.widgets[0] + " " + eta
                signaler.emit(SIGNAL('progress(int, int, QString)'),
                              self.id, value, txt)
        if not has_eta:
            signaler.emit(SIGNAL('progress(int, int)'), self.id,
                          value)

    def start(self):
        """
        Starts the progress. Called by hyperspy side.
        """
        global signaler
        signaler.emit(SIGNAL('created(int, int, QString)'), self.id,
                      self.maxval, self.widgets[0])
        ret = super(UIProgressBar, self).start()
        return ret

    def finish(self):
        """
        Used to tell the progress is finished. Called by hyperspy side.
        """
        self.update(self.maxval)
        global signaler
        signaler.emit(SIGNAL('finished(int)'), self.id)
