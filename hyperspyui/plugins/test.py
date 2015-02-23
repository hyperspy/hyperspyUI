from hyperspyui.plugins.plugin import Plugin
import numpy as np
from hyperspy.hspy import *

class Test(Plugin):
    name = "Test"
    
    def create_actions(self):
        self.add_action('Test.default', "Test", self.default,
                        icon="C:/GitHub/hyperspyUI/images/analysis.svg",
                        tip="")

    def create_menu(self):
        self.add_menuitem('Debug', self.ui.actions['Test.default'])

    def create_toolbars(self):
        self.add_toolbar_button('Debug', self.ui.actions['Test.default'])

    def default(self):
        ui = self.ui
        siglist = ui.signals
        ui.load([u'G:\\TEM Surface recon\\20140214 - NWG130 refibbed\\EELS_02_Map\\Spectrum Imaging-001\\cropped.hdf5'])
        ui.plugins['PCA'].pca(n_components=5)
        ui.close_signal(siglist[-1])
