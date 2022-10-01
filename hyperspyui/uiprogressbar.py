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
Created on Wed Nov 26 19:11:19 2014

@author: Vidar Tonaas Fauske
"""

from __future__ import division, absolute_import
# future division is important to divide integers and get as
# a result precise floating numbers (instead of truncated int)
# import compatibility functions and utilities
import sys
from time import time

from qtpy.QtCore import QObject, Signal

import hyperspy.external.progressbar
from tqdm import tqdm

from hyperspyui.exceptions import ProcessCanceled


# Create signal object which will handle all events
class Signaler(QObject):
    created = Signal([int, int, str])
    progress = Signal([int, int, str], [int, int])
    finished = Signal(int)

    cancel = Signal(int)
    # This is necessary as it bugs out if not (it's a daisy chained event)

    def _on_cancel(self, pid):
        signaler.cancel.emit(pid)
    on_cancel = _on_cancel


signaler = Signaler()

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
    return UIProgressBar(*args, **kwargs)


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


class UIProgressBar(tqdm):

    """
    Connector between hyperspy process with a progressbar, and the UI. See also
    the doc for wrap() for more details.
    """

    uid = 1

    @classmethod
    def write(cls, s, file=sys.stdout, end="\n"):
        """
        Print a message via tqdm_gui (just an alias for print)
        """
        # TODO: print text on GUI?
        file.write(s)
        file.write(end)

    def __init__(self, *args, mininterval=0.5, **kwargs):
        self.id = self.uid
        self.uid += 1
        kwargs['gui'] = True
        self.cancelled = False
        super().__init__(*args, mininterval=mininterval, **kwargs)
        # Initialize the GUI display
        if self.disable or not kwargs['gui']:
            return

        # assert maxval >= 0
        # self.maxval = maxval
        self.signal_set = False

        global signaler
        signaler.cancel[int].connect(self.cancel)

        self.currval = 0
        self.finished = False
        self.start_time = None
        self.seconds_elapsed = 0

        signaler.created[int, int, str].emit(self.id, self.total, "")

    def cancel(self, pid):
        """
        Slot for the UI to call if it wants to cancel the process. Thread safe.
        """
        if pid == self.id:
            self.cancelled = True

    @staticmethod
    def format_string(n, total, elapsed, rate=None):
        return "ETA: " + (tqdm.format_interval((total - n) / rate)
                          if rate else '?')

    def __iter__(self):
        iterable = self.iterable
        if self.disable:
            for obj in iterable:
                if self.cancelled is True:
                    raise ProcessCanceled("User cancelled operation")
                yield obj
            return

        # ncols = self.ncols
        mininterval = self.mininterval
        maxinterval = self.maxinterval
        miniters = self.miniters
        dynamic_miniters = self.dynamic_miniters
        start_t = self.start_t
        last_print_t = self.last_print_t
        last_print_n = self.last_print_n
        n = self.n
        # dynamic_ncols = self.dynamic_ncols
        smoothing = self.smoothing
        avg_time = self.avg_time

        for obj in iterable:
            if self.cancelled is True:
                raise ProcessCanceled("User cancelled operation")
            yield obj
            # Update and print the progressbar.
            # Note: does not call self.update(1) for speed optimisation.
            n += 1
            delta_it = n - last_print_n
            # check the counter first (avoid calls to time())
            if delta_it >= miniters:
                cur_t = time()
                delta_t = cur_t - last_print_t
                if delta_t >= mininterval:
                    elapsed = cur_t - start_t
                    # EMA (not just overall average)
                    if smoothing and delta_t:
                        avg_time = delta_t / delta_it \
                            if avg_time is None \
                            else smoothing * delta_t / delta_it + \
                            (1 - smoothing) * avg_time

                    txt = self.format_string(
                        n, self.total, elapsed,
                        1 / avg_time if avg_time else None)

                    global signaler
                    signaler.progress[int, int, str].emit(self.id, n, txt)

                    # If no `miniters` was specified, adjust automatically
                    # to the maximum iteration rate seen so far.
                    if dynamic_miniters:
                        if maxinterval and delta_t > maxinterval:
                            # Set miniters to correspond to maxinterval
                            miniters = delta_it * maxinterval / delta_t
                        elif mininterval and delta_t:
                            # EMA-weight miniters to converge
                            # towards the timeframe of mininterval
                            miniters = smoothing * delta_it * mininterval \
                                / delta_t + (1 - smoothing) * miniters
                        else:
                            miniters = smoothing * delta_it + \
                                (1 - smoothing) * miniters

                    # Store old values for next call
                    last_print_n = n
                    last_print_t = cur_t

        # Closing the progress bar.
        # Update some internal variables for close().
        self.last_print_n = last_print_n
        self.n = n
        self.close()

    def update(self, n=1):
        """
        Updates the progress bar to a new value. Called by the hyperspy side.
        Not safe to call from UI.
        """
        if self.disable:
            return
        if self.cancelled is True:
            raise ProcessCanceled("User cancelled operation")

        if n < 0:
            n = 1
        self.n += n

        delta_it = self.n - self.last_print_n  # should be n?
        if delta_it >= self.miniters:
            # We check the counter first, to reduce the overhead of time()
            cur_t = time()
            delta_t = cur_t - self.last_print_t
            if delta_t >= self.mininterval:
                elapsed = cur_t - self.start_t
                # EMA (not just overall average)
                if self.smoothing and delta_t:
                    self.avg_time = delta_t / delta_it \
                        if self.avg_time is None \
                        else self.smoothing * delta_t / delta_it + \
                        (1 - self.smoothing) * self.avg_time

                txt = self.format_string(
                    self.n, self.total, elapsed,
                    1 / self.avg_time if self.avg_time else None)

                global signaler
                signaler.progress[int, int, str].emit(self.id, self.n, txt)

                # If no `miniters` was specified, adjust automatically to the
                # maximum iteration rate seen so far.
                # e.g.: After running `tqdm.update(5)`, subsequent
                # calls to `tqdm.update()` will only cause an update after
                # at least 5 more iterations.
                if self.dynamic_miniters:
                    if self.maxinterval and delta_t > self.maxinterval:
                        self.miniters = self.miniters * self.maxinterval \
                            / delta_t
                    elif self.mininterval and delta_t:
                        self.miniters = self.smoothing * delta_it \
                            * self.mininterval / delta_t + \
                            (1 - self.smoothing) * self.miniters
                    else:
                        self.miniters = self.smoothing * delta_it + \
                            (1 - self.smoothing) * self.miniters

                # Store old values for next call
                self.last_print_n = self.n
                self.last_print_t = cur_t

    def close(self):
        if self.disable:
            return

        self.disable = True
        self.finish()

        self._instances.remove(self)

    def finish(self):
        """
        Used to tell the progress is finished. Called by hyperspy side.
        """
        global signaler
        signaler.finished[int].emit(self.id)
