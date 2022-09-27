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
Created on Sun Nov 23 17:10:41 2014

@author: Vidar Tonaas Fauske
"""

try:
    import traitsui.qt4.ui_base as ui_base
except RuntimeError:
    import sys

    if 'sphinx' in sys.modules:
        class Dummy: pass
        ui_base = Dummy()
        ui_base._StickyDialog = Dummy
    else:
        raise
orig_type = ui_base._StickyDialog


class HookedDialog(orig_type):

    def __init__(self, ui, parent, *args, **kwargs):
        _on_creating(self, ui, parent)
        super().__init__(ui, parent, *args, **kwargs)
        _on_created(self, ui, parent)

    def closeEvent(self, e):
        _on_closing(self, e)
        super().closeEvent(e)
        if e.isAccepted():
            _on_closed(self)

    def deleteLater(self):
        _on_destroyed(self)
        super().deleteLater()


def hook_traitsui():
    """
    Call this function to enable hooking of traitsui events
    """
    ui_base._StickyDialog = HookedDialog


def dehook_traitsui():
    """
    Call this function to remove hooks from traitsui
    """
    ui_base._StickyDialog = orig_type

# -----------------------------------------------------------
# The rest of this file is simply event callback handling
# -----------------------------------------------------------

_creating_cbs = {}
_created_cbs = {}
_closing_cbs = {}
_closed_cbs = {}
_destroyed_cbs = {}


def _cb(cbs, *args, **kwargs):
    for cb, userdata in cbs.items():
        if userdata is None:
            cb(*args, **kwargs)
        else:
            cb(userdata, *args, **kwargs)


def _on_creating(*args, **kwargs):
    _cb(_creating_cbs, *args, **kwargs)


def _on_created(*args, **kwargs):
    _cb(_created_cbs, *args, **kwargs)


def _on_closing(*args, **kwargs):
    _cb(_closing_cbs, *args, **kwargs)


def _on_closed(*args, **kwargs):
    _cb(_closed_cbs, *args, **kwargs)


def _on_destroyed(*args, **kwargs):
    _cb(_destroyed_cbs, *args, **kwargs)


def connect_creating(callback, userdata=None):
    """
    Call to subscribe to traitsui dialog creating events. 'callback' is called
    on the event, with the 'userdata' as it's first parameter if it is not
    None; otherwise this parameter is not included in the parameter list.
    The other parameters (listed in order) are the dialog reference, traitsui's
    'ui' parameter, and the parent of the dialog. 'Creating' events are called
    just before the dialog is actually created.
    """
    global _creating_cbs
    _creating_cbs[callback] = userdata


def disconnect_creating(callback):
    """
    Disconnect callback from subscription.
    """
    global _creating_cbs
    if callback in _creating_cbs:
        _creating_cbs.pop(callback)


def connect_created(callback, userdata=None):
    """
    Call to subscribe to traitsui dialog created events. 'callback' is called
    on the event, with the 'userdata' as it's first parameter if it is not
    None; otherwise this parameter is not included in the parameter list.
    The other parameters (listed in order) are the dialog reference, traitsui's
    'ui' parameter, and the parent of the dialog. 'Created' events are called
    just after the dialog is actually created.
    """
    global _created_cbs
    _created_cbs[callback] = userdata


def disconnect_created(callback):
    """
    Disconnect callback from subscription.
    """
    global _created_cbs
    if callback in _created_cbs:
        _created_cbs.pop(callback)


def connect_closing(callback, userdata=None):
    """
    Call to subscribe to traitsui dialog closing events. 'callback' is called
    on the event, with the 'userdata' as it's first parameter if it is not
    None; otherwise this parameter is not included in the parameter list.
    The only other parameter is the dialog reference. 'Closing' events are
    called before the dialog is actually closed, and might be aborted. Is not
    fired if the dialog is deleted before it is closed. (See destroyed event)
    """
    global _closing_cbs
    _closing_cbs[callback] = userdata


def disconnect_closing(callback):
    """
    Disconnect callback from subscription.
    """
    global _closing_cbs
    if callback in _closing_cbs:
        _closing_cbs.pop(callback)


def connect_closed(callback, userdata=None):
    """
    Call to subscribe to traitsui dialog closing events. 'callback' is called
    on the event, with the 'userdata' as it's first parameter if it is not
    None; otherwise this parameter is not included in the parameter list.
    The only other parameter is the dialog reference. 'Closed' events are
    called just after the dialog is actually closed, and cannot be aborted. Is
    not fired if the dialog is deleted before it is closed. (See destroyed
    event)
    """
    global _closed_cbs
    _closed_cbs[callback] = userdata


def disconnect_closed(callback):
    """
    Disconnect callback from subscription.
    """
    global _closed_cbs
    if callback in _closed_cbs:
        _closed_cbs.pop(callback)


def connect_destroyed(callback, userdata=None):
    """
    Call to subscribe to traitsui dialog destroyed events. 'callback' is called
    on  the event, with the 'userdata' as it's first parameter if it is not
    None; otherwise this parameter is not included in the parameter list.
    The only other parameter is the dialog reference.
    """
    global _destroyed_cbs
    _destroyed_cbs[callback] = userdata


def disconnect_destroyed(callback):
    """
    Disconnect callback from subscription.
    """
    global _destroyed_cbs
    if callback in _destroyed_cbs:
        _destroyed_cbs.pop(callback)
