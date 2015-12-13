from hyperspyui.plugins.plugin import Plugin
import numpy as np
from hyperspy.signal import DataIterator
from skimage.filters import gaussian_filter
from hyperspyui.util import win2sig
from hyperspyui.widgets.extendedqwidgets import ExToolWindow

from python_qt_binding import QtGui, QtCore


def tr(text):
    return QtCore.QCoreApplication.translate("GaussianFilter", text)


class GaussianFilter(Plugin):
    name = "Gaussian Filter"

    def __init__(self, ui):
        super(GaussianFilter, self).__init__(ui)
        self.settings.set_default('sigma', 1.0)

    def create_actions(self):
        self.add_action(
            self.name +
            '.show_dialog',
            self.name,
            self.show_dialog,
            icon="gaussian_bare.svg",
            tip="Apply a gaussian filter",
            selection_callback=self.selection_rules)

    def create_menu(self):
        self.add_menuitem('Image', self.ui.actions[self.name + '.show_dialog'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'Image', self.ui.actions[
                self.name + '.show_dialog'])

    def selection_rules(self, win, action):
        """
        Callback to determine if rotation is valid for the passed window.
        """
        s = win2sig(win, self.ui.signals)
        ok = False
        if s is not None:
            if win == s.signal_plot and \
                    s.signal.axes_manager.signal_dimension == 2:
                ok = True
        if ok:
            action.setEnabled(True)
        else:
            action.setEnabled(False)

    def gaussian(self, sigma, signal=None, out=None, record=True,
                 *args, **kwargs):
        if signal is None:
            signal, axes, _ = self.ui.get_selected_plot()
            if isinstance(axes, basestring):
                axm = signal.signal.axes_manager
                if axes.startswith("nav"):
                    axes = (axm._axes.index(axm.navigation_axes[0]),
                            axm._axes.index(axm.navigation_axes[1]))
                elif axes.startswith("sig"):
                    axes = (axm._axes.index(axm.signal_axes[0]),
                            axm._axes.index(axm.signal_axes[1]))

        if out is None:
            if record:
                self.record_code(
                    r"<p>.gaussian({0}, {1}, {2})".format(
                        sigma, args, kwargs))
            data = np.zeros_like(signal.data, dtype=np.float)
            it = DataIterator(signal)
            for im in it:
                data[it.slices] = gaussian_filter(im, sigma)
            return signal._deepcopy_with_new_data(data)
        else:
            if out.data.dtype is not np.float:
                out.change_dtype(np.float)
            if record:
                self.record_code(
                    r"<p>.gaussian({0}, out={1}, {2}, {3})".format(
                        sigma, out, args, kwargs))
            it = DataIterator(signal)
            for im in it:
                out.data[it.slices] = gaussian_filter(im, sigma)
            if hasattr(out, 'events') and hasattr(out.events, 'data_changed'):
                out.events.data_changed.trigger()

    def on_dialog_accept(self, dialog):
        self.settings['sigma'] = dialog.num_sigma.value()

    def show_dialog(self):
        signal, space, _ = self.ui.get_selected_plot()
        if space != "signal":
            return
        dialog = GaussianFilterDialog(signal, self.ui, self)
        if 'sigma' in self.settings:
            dialog.num_sigma.setValue(float(self.settings['sigma']))
        dialog.accepted.connect(lambda: self.on_dialog_accept(dialog))
        self.open_dialog(dialog)


class GaussianFilterDialog(ExToolWindow):

    def __init__(self, signal, parent, plugin):
        super(GaussianFilterDialog, self).__init__(parent)
        self.ui = parent
        self.create_controls()
        self.accepted.connect(self.ok)
        self.rejected.connect(self.undo)
        self.signal = signal
        self.plugin = plugin
        self.new_out = None
        self._connected_updates = False
        self.setWindowTitle(tr("Gaussian Filter"))

        # TODO: TAG: Functionality check
        if not hasattr(signal.signal, 'events'):
            self.chk_preview.setVisible(False)

        # TODO: Add dynamic rotation, e.g. one that rotates when source
        # signal's data_changed event triggers

    def connect(self):
        self.opt_new.toggled.connect(self.close_new)
        self.num_sigma.valueChanged.connect(self.update)
        self.opt_new.toggled.connect(self.update)
        self.opt_replace.toggled.connect(self.update)

    def disconnect(self):
        self.opt_new.toggled.disconnect(self.close_new)
        self.num_sigma.valueChanged.disconnect(self.update)
        self.opt_new.toggled.disconnect(self.update)
        self.opt_replace.toggled.disconnect(self.update)

    def ok(self):
        # Draw figure if not already done
        # TODO: TAG: Functionality check
        if not hasattr(self.signal.signal, 'events') or \
                not self.chk_preview.isChecked():
            self.update()
        sigma = self.num_sigma.value()
        self.plugin.record_code(r"<p>.gaussian({0})".format(sigma))

    def undo(self):
        self.close_new()
        self.set_preview

    def close_new(self, value=False):
        if self.new_out is not None and not value:
            self.new_out.close()
            self.new_out = None

    def set_preview(self, value):
        if not hasattr(self.signal.signal, 'events'):
            return
        if value:
            self.connect()
            self.update()
        else:
            self.disconnect()
            self.close_new()

    def update(self):
        sigma = self.num_sigma.value()
        if self.opt_new.isChecked():
            if self.new_out is None:
                out = None
            else:
                out = self.new_out.signal
        elif self.opt_replace.isChecked():
            out = self.signal.signal
        else:
            return  # Indeterminate state, do nothing

        s = self.plugin.gaussian(sigma, self.signal.signal,
                                 record=False, out=out)

        if out is None:
            s.metadata.General.title = self.signal.name + "[GaussianFilter]"
            s.plot()
            if (self.chk_preview.isChecked() and self.opt_new.isChecked() and
                    self.new_out is None):
                self.new_out = self.ui.lut_signalwrapper[s]

    def create_controls(self):
        """
        Create UI controls.
        """
        vbox = QtGui.QVBoxLayout()

        form = QtGui.QFormLayout()
        self.num_sigma = QtGui.QDoubleSpinBox()
        self.num_sigma.setValue(1.0)
        self.num_sigma.setMinimum(0.0)
        self.num_sigma.setSingleStep(0.1)
        self.num_sigma.setMaximum(1e3)
        self.num_sigma.setDecimals(2)
        form.addRow(tr("Sigma:"), self.num_sigma)
        vbox.addLayout(form)

        self.chk_preview = QtGui.QCheckBox(tr("Preview"))
        self.chk_preview.setCheckable(True)
        self.chk_preview.setChecked(False)
        vbox.addWidget(self.chk_preview)

        self.chk_preview.toggled[bool].connect(self.set_preview)

        self.gbo_output = QtGui.QGroupBox(tr("Output"))
        self.opt_new = QtGui.QRadioButton(tr("New signal"))
        self.opt_replace = QtGui.QRadioButton(tr("In place"))
        self.opt_new.setChecked(True)
        gbo_vbox2 = QtGui.QVBoxLayout()
        gbo_vbox2.addWidget(self.opt_new)
        gbo_vbox2.addWidget(self.opt_replace)
        self.gbo_output.setLayout(gbo_vbox2)
        vbox.addWidget(self.gbo_output)

        self.btn_ok = QtGui.QPushButton(tr("&OK"))
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QtGui.QPushButton(tr("&Cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_ok)
        hbox.addWidget(self.btn_cancel)
        vbox.addLayout(hbox)

        vbox.addStretch(1)
        self.setLayout(vbox)
