
from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.widgets.signallist import SignalList


class PickXSignalsWidget(QWidget):

    def __init__(self, signal_wrappers, x, parent=None, titles=None,
                 wrap_col=4):
        super(PickXSignalsWidget, self).__init__(parent)
        grid = QGridLayout()
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
            grid.addWidget(QLabel(titles[i]), 2*(i // wrap_col),
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
