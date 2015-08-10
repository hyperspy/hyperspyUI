from hyperspyui.plugins.plugin import Plugin
import matplotlib.pyplot as plt


class Tightlayout(Plugin):
    name = "TightLayout"

    def create_actions(self):
        self.add_action(
            self.name + '.default', "Tight layout", self.default,
            icon="move.svg",
            tip="Apply a tight layout to all plots of selected signal.")

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
        plot = ui.get_selected_plot()[2]
        if plot and hasattr(plot, 'figure'):
            plot.figure.tight_layout()
            plot.figure.canvas.draw()
