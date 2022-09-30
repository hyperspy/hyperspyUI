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

from hyperspyui.plugins.plugin import Plugin
import matplotlib.pyplot as plt


class Tightlayout(Plugin):
    name = "TightLayout"

    def create_actions(self):
        self.add_action(
            self.name + '.default', "Tight layout", self.default,
            icon="move.svg",
            tip="Apply a tight layout to the selected plot.")

    def create_menu(self):
        self.add_menuitem('Plot', self.ui.actions[self.name + '.default'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'Plot',
            self.ui.actions[
                self.name +
                '.default'])

    def default(self):
        f = plt.gcf()
        if f:
            f.tight_layout()
            f.canvas.draw()
