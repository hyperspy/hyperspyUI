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
Created on Mon Oct 27 23:17:25 2014

@author: Vidar Tonaas Fauske
"""


from qtpy import QtWidgets


class BindingList(list):

    """
    A list that has been extended to sync other lists or collections to changes
    in its contents. By custom targets, it can also be used to trigger events
    on addition/removal. Only append and remove actions are required, as
    extend, insert and pop can be inferred (insert loses order however), but
    for reasons of speed, it is recommended to supply all if they are
    available. Supported targets for add_target are types 'list' and
    'QListWidget'.
    """

    def __init__(self, target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_target(target)

    def __eq__(self, other):
        if not isinstance(other, BindingList):
            return False
        return list.__eq__(self, other) and self.targets == other.targets

    def set_target(self, target):
        self.targets = {}
        self.add_target(target)

    def add_custom(self, target, append, insert, extend, remove, pop):
        cb = {'ap': append, 'in': insert,
              'ex': extend, 're': remove, 'po': pop}
        self.targets[target] = cb

    def add_target(self, target):
        if target is None:
            return
        elif isinstance(target, list):
            cb = {'ap': target.append, 'in': target.insert,
                  'ex': target.extend, 're': target.remove, 'po': target.pop}
        elif isinstance(target, QtWidgets.QListWidget):
            def qlr(value):
                target.takeItem(self.index(value))
            cb = {'ap': target.addItem, 'in': target.insertItem,
                  'ex': target.addItems, 're': qlr,
                  'po': target.takeItem}
        else:
            raise TypeError("The argument `target` must be a of `list` or "
                            "`QListWidget` type.")
        self.targets[target] = cb

    def remove_target(self, target):
        self.targets.pop(target, 0)

    def append(self, object):
        super().append(object)
        for t in list(self.targets.values()):
            if t['ap'] is not None:
                t['ap'](object)

    def insert(self, index, object):
        super().insert(index, object)
        for t in list(self.targets.values()):
            if t['in'] is not None:
                t['in'](index, object)
            elif t['ap'] is not None:
                t['ap'](object)

    def extend(self, iterable):
        super().extend(iterable)
        for t in list(self.targets.values()):
            if t['ex'] is not None:
                t['ex'](iterable)
            if t['ap'] is not None:
                for v in iterable:
                    t['ap'](v)

    def remove(self, value):
        if value not in self:
            return

        for t in list(self.targets.values()):
            if t['re'] is not None:
                t['re'](value)
        super().remove(value)

    def pop(self, index=-1):
        if index < 0:
            index = len(self) + index
        for t in list(self.targets.values()):
            if t['po'] is not None:
                t['po'](index)
            elif t['re'] is not None:
                v = self[index]
                t['re'](v)
        return super().pop(index)
