from hyperspyui.plugins.plugin import Plugin
import hyperspy.roi

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


class NavigatorSwitch(Plugin):
    name = "Navigator switch"

    def create_actions(self):
        self.add_action(self.name + '.point', "Point", self.point,
                        tip="Use a point navigator.")
        self.add_action(self.name + '.mean', "Mean", self.mean,
                        tip="Use a mean navigator.")

    def create_menu(self):
        self._nav_ag = QActionGroup(self.ui)
        self._nav_ag.setExclusive(True)
        self._nav_menu = QMenu("Navigator")
        for ac in self.actions.itervalues():
            ac.setCheckable(True)
            self._nav_ag.addAction(ac)
            self._nav_menu.addAction(ac)
        self.add_menuitem('Signal', self._nav_menu.menuAction())

    def point(self, signal=None):
        s = self.ui.get_selected_signal()
        if s is None or s._plot is None:
            return
        nd = len(s._plot.pointer.position)
        if nd == 1:
            roi = hyperspy.roi.Point1DROI(*s._plot.pointer.coordinates)
        elif nd == 2:
            roi = hyperspy.roi.Point2DROI(*s._plot.pointer.coordinates)
        roi.navigate(s)

    def mean(self, signal=None):
        s = self.ui.get_selected_signal()
        if s is None or s._plot is None:
            return
        nd = len(s._plot.pointer.position)
        if nd == 1:
            left = s._plot.pointer.coordinates[0]
            idx_left = s._plot.pointer.position[0]
            right = s._plot.navigator_plot.axis[idx_left + 1]
            roi = hyperspy.roi.SpanROI(left=left, right=right)
        elif nd == 2:
            roi = hyperspy.roi.RectangularROI(0, 0, 0, 0)
            # Read out current position from existing widget
            # TODO: Maybe a bit brittle?
            roi._on_widget_change(s._plot.pointer)
        roi.navigate(s)
