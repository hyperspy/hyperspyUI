from hyperspyui.plugins.plugin import Plugin
import matplotlib as mpl
import os

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


def tr(text):
    return QCoreApplication.translate("MovieSaver", text)


# Check that we have a valid writer
writer = mpl.rcParams['animation.writer']
writers = mpl.animation.writers
if writer in writers.avail:
    writer = writers[writer]()
else:
    import warnings
    warnings.warn("MovieWriter %s unavailable" % writer)

    try:
        writer = writers[writers.list()[0]]()
    except IndexError:
        raise ValueError("Cannot save animation: no writers are "
                         "available. Please install mencoder or "
                         "ffmpeg to save animations.")
del writer


class MovieSaver(Plugin):
    name = "Movie Saver"

    def create_actions(self):
        self.add_action(self.name + '.save', self.name, self.save,
                        icon="../images/video.svg",
                        tip="")

    def create_menu(self):
        self.add_menuitem('File', self.ui.actions[self.name + '.save'])

    def create_toolbars(self):
        self.add_toolbar_button(
            'File',
            self.ui.actions[
                self.name +
                '.save'])

    def save(self, wrapper=None, fps=None, fname=None, dpi=None):
        if wrapper is None:
            wrapper = self.ui.get_selected_wrapper()
        signal = wrapper.signal

        # TODO: Input: writer type, FPS, file, resolution/dpi [, bitrate ++]
        dlg = MovieArgsPrompt(self.ui)
        fname = os.path.join(os.path.dirname(self.ui.cur_dir), wrapper.name)
        fname += os.path.extsep + "mp4"
        dlg.edt_fname.setText(fname)
        dlg_w = self.ui.show_okcancel_dialog(tr("Save movie"), dlg)
        if dlg_w.result() == QDialog.Accepted:
            fps = dlg.num_fps.value()
            metadata = signal.metadata.as_dictionary()
            writer = mpl.rcParams['animation.writer']
            writers = mpl.animation.writers
            if writer in writers.avail:
                writer = writers[writer](fps=fps, metadata=metadata)
            else:
                import warnings
                warnings.warn("MovieWriter %s unavailable" % writer)

                try:
                    writer = writers[writers.list()[0]](fps=fps,
                                                        metadata=metadata)
                except IndexError:
                    raise ValueError("Cannot save animation: no writers are "
                                     "available. Please install mencoder or "
                                     "ffmpeg to save animations.")

            fname = dlg.edt_fname.text()
            dpi = dlg.num_dpi.value()
            fig = signal._plot.signal_plot.figure
            with writer.saving(fig, fname, dpi):
                for idx in signal.axes_manager:
                    QApplication.processEvents()
                    writer.grab_frame()


class MovieArgsPrompt(QWidget):

    def __init__(self, parent=None):
        super(MovieArgsPrompt, self).__init__(parent)
        self.create_controls()

    def create_controls(self):
        self.num_fps = QDoubleSpinBox()
        self.num_fps.setValue(5.0)
        self.num_fps.setMinimum(0.001)

        self.edt_fname = QLineEdit()
        self.btn_browse = QPushButton("...")

        self.num_dpi = QSpinBox()
        self.num_dpi.setValue(72)
        self.num_dpi.setMinimum(1)
        self.num_dpi.setMaximum(10000)

        frm = QFormLayout()
        frm.addRow(tr("FPS:"), self.num_fps)
        frm.addRow(tr("DPI:"), self.num_dpi)
        hbox = QHBoxLayout()
        hbox.addWidget(self.edt_fname)
        hbox.addWidget(self.btn_browse)
        frm.addRow(tr("File:"), hbox)

        self.setLayout(frm)
