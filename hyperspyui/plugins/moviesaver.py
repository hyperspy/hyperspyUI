# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.

from hyperspyui.plugins.plugin import Plugin
import matplotlib as mpl
import matplotlib.animation as animation
import os
import sys

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


def tr(text):
    return QCoreApplication.translate("MovieSaver", text)


# =============================================================================
# Check that we have a valid writer
writer = mpl.rcParams['animation.writer']
writers = animation.writers
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
# =============================================================================


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
            # Setup writer:
            fps = dlg.num_fps.value()
            codec = dlg.edt_codec.text()
            if not codec:
                codec = None
            extra = dlg.edt_extra.text()
            if extra:
                extra = list(extra.split())
            else:
                extra = None
            if dlg.chk_verbose.isChecked():
                old_verbose = mpl.verbose.level
                mpl.verbose.level = 'debug'
                if extra:
                    extra.extend(['-v', 'debug'])
                else:
                    extra = ['-v', 'debug']
            metadata = signal.metadata.as_dictionary()
            writer = mpl.rcParams['animation.writer']
            writers = animation.writers
            if writer in writers.avail:
                writer = writers[writer](fps=fps, metadata=metadata,
                                         codec=codec, extra_args=extra)
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

            # Set figure props:
            if not dlg.chk_colorbar.isChecked():
                cb_ax = signal._plot.signal_plot._colorbar.ax
                fig.delaxes(cb_ax)
            if not dlg.chk_axes.isChecked():
                signal._plot.signal_plot.ax.set_axis_off()

            try:
                with writer.saving(fig, fname, dpi):
                    for idx in signal.axes_manager:
                        QApplication.processEvents()
                        writer.grab_frame()
            finally:
                # Reset figure props:
                if dlg.chk_verbose.isChecked():
                    mpl.verbose.level = old_verbose
                if not dlg.chk_colorbar.isChecked():
                    fig.add_axes(cb_ax)
                if not dlg.chk_axes.isChecked():
                    signal._plot.signal_plot.ax.set_axis_on()
                fig.canvas.draw()


class MovieArgsPrompt(QWidget):

    def __init__(self, parent=None):
        super(MovieArgsPrompt, self).__init__(parent)
        self.create_controls()

    def create_controls(self):
        self.num_fps = QDoubleSpinBox()
        self.num_fps.setValue(15.0)
        self.num_fps.setMinimum(0.001)

        self.edt_fname = QLineEdit()
        self.btn_browse = QPushButton("...")

        self.num_dpi = QSpinBox()
        self.num_dpi.setValue(72)
        self.num_dpi.setMinimum(1)
        self.num_dpi.setMaximum(10000)

        self.chk_axes = QCheckBox("Axes")
        self.chk_colorbar = QCheckBox("Colorbar")

        # codec = mpl.rcParams['animation.codec']
        codec = 'h264'
        self.edt_codec = QLineEdit(codec)
        self.edt_extra = QLineEdit("-preset veryslow -crf 0")

        # TODO: Use QCompleter or QComboBox for codecs
        # TODO: Use QCompleter for 'extra' history
        # TODO: Bitrate and/or quality slider

        self.chk_verbose = QCheckBox("Verbose")
        try:
            sys.stdout.fileno()
        except:
            self.chk_verbose.setEnabled(False)
            self.chk_verbose.setToolTip("Verbose output does not work with " +
                                        "internal console.")

        frm = QFormLayout()
        frm.addRow(tr("FPS:"), self.num_fps)
        frm.addRow(tr("DPI:"), self.num_dpi)
        frm.addRow(tr("Codec:"), self.edt_codec)
        frm.addRow(tr("Extra args:"), self.edt_extra)
        frm.addRow(self.chk_axes, self.chk_colorbar)
        hbox = QHBoxLayout()
        hbox.addWidget(self.edt_fname)
        hbox.addWidget(self.btn_browse)
        frm.addRow(tr("File:"), hbox)
        frm.addRow("", self.chk_verbose)

        self.setLayout(frm)
