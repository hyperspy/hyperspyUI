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
        ui = self.ui
        f = plt.gcf()
        if f:
            f.tight_layout()
            f.canvas.draw()
