from hyperspyui.plugins.plugin import Plugin
import numpy as np

from hyperspyui.util import win2sig


class EnsureLt2D:

    def __init__(self, ui):
        self.ui = ui

    def __call__(self, win, action):
        sig = win2sig(win, self.ui.signals, self.ui._plotting_signal)
        valid = sig is not None and (
            len(sig.signal.data.shape) <= 2 or (
                win is sig.signal_plot and
                sig.signal.axes_manager.signal_dimension <= 2))

        action.setEnabled(valid)


class SaveDataAsText(Plugin):
    name = "Save data as text"

    def create_actions(self):
        self.add_action(self.name + '.save_as_text', self.name,
                        self.save_as_text,
                        tip="",
                        selection_callback=EnsureLt2D(self.ui))

    def create_menu(self):
        self.add_menuitem('File', self.ui.actions[self.name + '.save_as_text'])

    def save_as_text(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        # What to save
        if len(signal.data.shape) <= 2:
            data = signal.data
        elif signal.axes_manager.signal_dimension <= 2:
            data = signal().data
        else:
            raise ValueError("Ivalid signal dimensions for saving as text.")

        extensions = "Text file (*.txt);;*.csv;;*.dat;;All files (*.*)"
        filename = self.ui.prompt_files(extensions, exists=False)
        if filename:
            np.savetxt(filename, data, delimiter=',\t')
