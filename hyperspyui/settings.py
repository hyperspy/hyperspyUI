# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 14:21:00 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from widgets.extendedqwidgets import ExRememberPrompt

class Settings(object):
    def __init__(self, parent=None, group=None, sep='.'):
        self.sep = sep
        self.group = group
        self.parent = parent
        
    def __getitem__(self, key):
        if isinstance(key, tuple):
            key, t = key
        else:
            t = None
        groupings = (self.group + self.sep + key).split(self.sep)
        key = groupings.pop()
        settings = QSettings(self.parent)
        for g in groupings:
            settings.beginGroup(g)
        ret = settings.value(key, t)
        for g in groupings:
            settings.endGroup()
        return ret
        
    def __setitem__(self, key, value):
        groupings = (self.group + self.sep + key).split(self.sep)
        key = groupings.pop()
        settings = QSettings(self.parent)
        for g in groupings:
            settings.beginGroup(g)
        settings.setValue(key, value)
        for g in groupings:
            settings.endGroup()
    
    def get_or_prompt(self, key, options, title="Prompt", descr=""):
        """
        Gets the setting specified by key. If it is not set, prompts the user
        to select one option out of several. The prompt includes a checkbox to
        remember the answer ("Remember this setting").
        
        The option parameter should be a list of two-tuples, specifying an
        ordered list of option values, and labels.
        """
        
        # First check if we have a remembered setting.
        val = self[key]
        if val is not None:
            return val
        
        # Setup the dialog
        mb = ExRememberPrompt(QMessageBox.Question, title, descr)
        if len(options) < 5:
            buttons = []
            opt = options[0]
            buttons.append(mb.addButton(opt[1], QMessageBox.AcceptRole))
            for opt in options[1:]:
                buttons.append(mb.addButton(opt[1], QMessageBox.RejectRole))
        else:
            pass #TODO: Make list selection
        mb.addButton(QMessageBox.Cancel)
        
        # Show the dialog
        mb.exec_()
        btn = mb.clickedButton()
        if btn not in buttons:
            # The user did not make a valid selection = cancelled
            return None
        sel = btn.text()
        idx = [o[1] for o in options].index(sel)
        ret = options[idx][0]
        if mb.isChecked():
            self[key] = ret
        return ret
        
    def write(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)
        
        for k, v in d.iteritems():
            settings.setValue(k, v)
        
        if group is not None:
            settings.endGroup()
            
    def read(self, d, group=None, settings=None):
        if settings is None:
            settings = QSettings(self)
        if group is not None:
            settings.beginGroup(group)
        
        for k, v in d.iteritems():
            if isinstance(v, tuple):
                settings.value(k, v)
        
        if group is not None:
            settings.endGroup()       