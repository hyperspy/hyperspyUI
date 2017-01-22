from hyperspyui.plugins.plugin import Plugin

from hyperspy.utils.plot import plot_images, plot_spectra


class PlotUtils(Plugin):
    name = "Plot utils"

    def create_actions(self):
        self.add_action(self.name + '.plot_images', "Plot images",
                        self.plot_images,
                        tip="Plots several images together in one figure.")
        self.add_action(self.name + '.plot_spectra', "Plot spectra",
                        self.plot_spectra,
                        tip="Plots several spectra together in one figure.")

    def create_menu(self):
        self.add_menuitem('Image',
                          self.ui.actions[self.name + '.plot_images'])
        self.add_menuitem('Spectrum',
                          self.ui.actions[self.name + '.plot_spectra'])

    def plot_images(self, images=None):
        if images is None:
            images = self.ui.get_selected_signals()
        images_t = []
        for im in images:
            if len(im.axes_manager.shape) != 2 and len(images) > 1:
                raise ValueError(
                    "Signal shape invalid for plot_images(): %s" % str(im))
            if im.axes_manager.signal_dimension == 2:
                images_t.append(im)
            elif len(im.axes_manager.shape) != 2:
                raise ValueError(
                    "Signal needs to be an image, or a stack of images")
            else:
                images_t.append(im.as_signal2D((0, 1)))
        plot_images(images_t, colorbar=None, axes_decor=None)

    def plot_spectra(self, spectra=None):
        if spectra is None:
            spectra = self.ui.get_selected_signals()
            if len(spectra) == 1:
                spectra = spectra[0]

        spectra_t = []
        for im in spectra:
            if len(im.axes_manager.shape) != 1 and len(spectra) > 1:
                raise ValueError(
                    "Signal shape invalid for plot_spectra(): %s" % str(im))
            if im.axes_manager.signal_dimension == 1:
                spectra_t.append(im)
            elif len(im.axes_manager.shape) != 1:
                raise ValueError(
                    "Signal needs to be 1-dimensional, or a stack of 1D signals")
            else:
                spectra_t.append(im.as_signal1D(0))

        plot_spectra(spectra_t)
