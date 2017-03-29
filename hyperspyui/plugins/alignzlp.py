from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs


class Alignzlp(Plugin):
    name = "AlignZLP"

    def create_actions(self):
        self.add_action(
            self.name +
            '.default',
            self.name,
            self.default,
            icon="C:/dev/hyperspyUI/hyperspyui/images/align_zero_loss.svg",
            tip="")

    def create_menu(self):
        self.add_menuitem('EELS', self.ui.actions[self.name + '.default'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'EELS', self.ui.actions[
                self.name + '.default'])

    def default(self):
        ui = self.ui
        siglist = ui.hspy_signals
        s = ui.get_selected_signal()
        s.align_zero_loss_peak()
