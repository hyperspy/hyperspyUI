# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 14:16:41 2014

@author: Vidar Tonaas Fauske
"""



from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import types
import hyperspy.misc.progressbar
import time

class ProcessCanceled(Exception):
    pass

#orig = hyperspy.misc.progressbar.progressbar
def wrap(*args, **kwargs):
    disabled = kwargs.pop('disabled', False)
    maxval = kwargs.pop('maxval',100)
    text = kwargs.pop('text', "")
    if disabled:
        return hyperspy.misc.progressbar.DummyProgressBar()
    else:
        widgets = [text, "bar", 
                   hyperspy.misc.progressbar.ETA()]
        return UIProgressBar(widgets=widgets, maxval=maxval).start()
hyperspy.misc.progressbar.progressbar = wrap

class UIProgressBar(hyperspy.misc.progressbar.ProgressBar):
    uid = 1
    def __init__(self, maxval=100, widgets=[""]):
        self.cancelled = False
        self.id = self.uid
        self.uid += 1
        
        assert maxval >= 0
        self.maxval = maxval
        self.signal_set = False
        
        self.signaler = QObject()
        self.signaler.created = Signal(object)
        self.signaler.progress = Signal(object, int)
        self.signaler.finished_sig = Signal(object)
        
        # Hack to get parent window of dialog
        tlw = QApplication.instance().topLevelWidgets()
        for w in tlw:
            if w.windowTitle() == "HyperSpy":
                break
        
        self.signaler.connect(self.signaler, SIGNAL('created(int, int, QString)'),
                              w.on_progressbar_wanted)
        self.signaler.connect( self.signaler, SIGNAL('progress(int, int)'),
                              w.on_progressbar_update)
        self.signaler.connect( self.signaler, SIGNAL('progress(int, int, QString)'),
                              w.on_progressbar_update)
        self.signaler.connect( self.signaler, SIGNAL('finished_sig(int)'),
                              w.on_progressbar_finished)
        self.signaler.connect( w, SIGNAL('cancel_progressbar(int)'), 
                              self.cancel)
        self.widgets = widgets

        self.currval = 0
        self.finished = False
        self.start_time = None
        self.seconds_elapsed = 0

    def cancel(self, pid):
        if pid == self.id:
            self.cancelled = True

    def update(self, value):
        "Updates the progress bar to a new value."
        if self.cancelled is True:
            raise ProcessCanceled()
        assert 0 <= value <= self.maxval
        self.currval = value
        if not self.start_time:
            self.start_time = time.time()
        self.seconds_elapsed = time.time() - self.start_time
        has_eta = False
        for w in self.widgets:
            if isinstance(w, hyperspy.misc.progressbar.ETA):
                has_eta = True
                eta = w.update(self)
                txt = self.widgets[0] + " " + eta
                self.signaler.emit(SIGNAL('progress(int, int, QString)'), 
                                   self.id, value, txt)
        if not has_eta:
            self.signaler.emit(SIGNAL('progress(int, int)'), self.id,
                               value)
        
    def start(self):
        self.signaler.emit(SIGNAL('created(int, int, QString)'), self.id,
                           self.maxval, self.widgets[0])
        ret = super(UIProgressBar, self).start()
#        self.progressbar.exec_()
        return ret

    def finish(self):
        """Used to tell the progress is finished."""
        self.update(self.maxval)
        self.signaler.emit(SIGNAL('finished_sig(int)'), self.id)

class Worker(QObject):
    progress = QtCore.Signal(int)
    finished = QtCore.Signal()
    error = QtCore.Signal(str)
    
    def __init__(self, run):
        super(Worker, self).__init__()
        self.run_function = run
    
    def process(self):
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
        

class ProgressThread(QObject):
    """
    Executes a user provided function in a new thread, and pops up a
    QProgressBar until it finishes. To have an updating progress bar,
    have the provided function be a generator, and yield completion rate
    in percent (int from 0 to 100).
    """
    
    Block_Wait = 3 * 1000

    pool = []    
    def add_to_pool(instance):
        ProgressThread.pool.append(instance)
    
    def remove_from_pool(instance):
        ProgressThread.pool.remove(instance)
    
    def __init__(self, parent, run, finished=None, label=None, title="Processing"):
        super(ProgressThread, self).__init__()
        
        self.block_wait = self.Block_Wait
        
        # Create thread/objects
        self.thread = QThread()
        worker = Worker(run)
        worker.moveToThread(self.thread)
        ProgressThread.add_to_pool(self)
             
        
        # Connect error reporting
        self.connect(worker, SIGNAL('error(QString)'), self.errorString)
        
        # Start up
        self.connect(self.thread, SIGNAL('started()'), worker.process)
        
        # Clean up
        self.connect(worker, SIGNAL('finished()'), self.thread.quit)
        self.connect(worker, SIGNAL('finished()'), worker.deleteLater)
        self.connect(self.thread, SIGNAL('finished()'), self.thread.deleteLater)
        
        def remove_ref():
            ProgressThread.remove_from_pool(self)
        self.connect(self.thread, SIGNAL('finished()'), remove_ref)
        
        if finished is not None:
            self.connect(worker, SIGNAL('finished()'), finished)
        
        # Need to keep ref so they stay in mem
        self.worker = worker
        
    def errorString(self, error):
        print error
        
    def run(self):
        self.thread.start()
#        self.thread.wait(self.block_wait)