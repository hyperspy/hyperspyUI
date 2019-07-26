import hyperspy.signals
from hyperspyui.plugins.plugin import Plugin
from hyperspyui.util import SignalTypeFilter
from hyperspyui.widgets.signallist import SignalList
from hyperspyui.log import logger
from qtpy.QtWidgets import QDialog


class Alignzlp(Plugin):
    name = "AlignZLP"

    def create_actions(self):
        self.add_action(
            self.name +
            '.default',
            self.name,
            self.default,
            icon="align_zero_loss.svg",
            tip="Align the zero loss peak of an EELS spectrum image",
            selection_callback=SignalTypeFilter(
                hyperspy.signals.EELSSpectrum, self.ui))

    def create_menu(self):
        self.add_menuitem('EELS', self.ui.actions[self.name + '.default'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'EELS', self.ui.actions[
                self.name + '.default'])

    def default(self):
        ui = self.ui
        s = ui.get_selected_signal()
        logger.debug('Align zero loss peak of ' + str(s))
        title = s.metadata.General.title

        signal_list = [
            sig for sig in ui.signals if (
                sig.signal is not s and
                isinstance(sig.signal, hyperspy.signals.EELSSpectrum))]
        also_align = []
        if len(signal_list) > 0:
            picker = SignalList(items=signal_list, parent=ui, multiselect=True)
            diag = ui.show_okcancel_dialog("Select signals to align with {}".format(
                title), picker, modal=True)
            if diag.result() != QDialog.Accepted:
                return
            also_align = [sig.signal for sig in picker.get_selected()]
        logger.debug(
            'Also aligning the following signals\n' + str(also_align))
        s.align_zero_loss_peak(also_align=also_align)
        logger.debug('ZLP alignment complete')
