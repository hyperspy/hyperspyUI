from hyperspyui.plugins.plugin import Plugin
import numpy as np
import hyperspy.api as hs


class DpcFftMask(Plugin):
    name = "Beam shifts from segmented"

    def create_actions(self):
        self.add_action(self.name + '.default', self.name, self.default,
                        tip="")

    def create_menu(self):
        self.add_menuitem('Magnetic', self.ui.actions[self.name + '.default'])

    def default(self):
        ui = self.ui
        signals = [s.signal for s in ui.select_x_signals(
            4, ["ext 0", "ext 1", "ext 2", "ext 3"])]
        s_ext0 = signals[0]
        s_ext1 = signals[1]
        s_ext2 = signals[2]
        s_ext3 = signals[3]
        s_ext0.change_dtype('float64')
        s_ext1.change_dtype('float64')
        s_ext2.change_dtype('float64')
        s_ext3.change_dtype('float64')
        s_ext02 = s_ext0 - s_ext2
        s_ext13 = s_ext1 - s_ext3
        s_ext02.metadata.General.title = 'dif02'
        s_ext13.metadata.General.title = 'dif13'
        s_ext02.plot()
        s_ext13.plot()
