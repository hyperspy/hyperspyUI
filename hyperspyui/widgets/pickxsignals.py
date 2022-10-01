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

from qtpy import QtWidgets

from hyperspyui.widgets.signallist import SignalList


class PickXSignalsWidget(QtWidgets.QWidget):

    def __init__(self, signal_wrappers, x, parent=None, titles=None,
                 wrap_col=4):
        super().__init__(parent)
        grid = QtWidgets.QGridLayout()
        self.pickers = []
        self._x = x
        self._sws = signal_wrappers

        if titles is None:
            titles = list(("",) * x)
        elif isinstance(titles, str):
            titles = list((titles,) * x)
        elif len(titles) < x:
            titles.extend(list(("",) * (x-len(titles))))

        for i in range(x):
            picker = SignalList(signal_wrappers, self, False)
            grid.addWidget(QtWidgets.QLabel(titles[i]), 2*(i // wrap_col),
                           i % wrap_col)
            grid.addWidget(picker, 1 + 2*(i // wrap_col), i % wrap_col)
            self.pickers.append(picker)
        self.setLayout(grid)

    def get_selected(self):
        signals = []
        for i in range(self._x):
            signals.append(self.pickers[i].get_selected())
        if self._x == 1:
            return signals[0]
        return signals

    def unbind(self):
        for i in range(self._x):
            self.pickers[i].unbind(self._sws)
