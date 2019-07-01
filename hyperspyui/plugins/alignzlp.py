from hyperspyui.plugins.plugin import Plugin
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
            tip="")

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

        signal_list = [sig for sig in ui.signals if sig.signal is not s]
        picker = SignalList(items=signal_list, parent=ui, multiselect=True)
        diag = ui.show_okcancel_dialog("Select signals to align with {}".format(
            title), picker, modal=True)
        signals = []
        if diag.result() == QDialog.Accepted:
            signals = picker.get_selected()
        else:
            return
        signals = [] if not signals else signals  # if none selected
        signals = [sig.signal for sig in signals]
        logger.debug('Also aligning the following signals\n' + str(signals))
        # unclear how to incorporate this. It needs a blist argument
        # picker.unbind(blist=?)
        s.align_zero_loss_peak(also_align=signals)
        logger.debug('ZLP alignment complete')
