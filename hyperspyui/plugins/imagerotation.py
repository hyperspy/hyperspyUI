# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 14:49:08 2015

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.widgets.extendedqwidgets import ExToolWindow
from scipy.ndimage import rotate
from hyperspyui.util import win2sig
from hyperspyui.signalwrapper import SignalWrapper


class ImageRotation_Plugin(Plugin):
    name = 'Image Rotation'
    
    def create_actions(self):
        self.ui.add_action('rotate', "Rotate", self.show_rotate_dialog,
#                        icon='rotate.svg',
                        tip="Rotate an image",
                        selection_callback=self.selection_rules)
    
    def create_menu(self):
        self.ui.add_menuitem('Signal', self.ui.actions['rotate'])
    
    def create_toolbars(self):
        self.ui.add_toolbar_button("Signal", self.ui.actions['rotate'])
    
    def selection_rules(self, win, action):
        """
        Callback to determine if rotation is valid for the passed window.
        """
        s = win2sig(win, self.ui.signals)
        ok = False
        if s is not None:
            if win == s.navigator_plot and \
                    s.signal.axes_manager.navigation_dimension >= 2:
                ok = True
            elif win == s.signal_plot and \
                    s.signal.axes_manager.signal_dimension == 2:
                ok = True
        if ok:
            action.setEnabled(True)
        else:
            action.setEnabled(False)
    
    @staticmethod
    def rotate_signal(signal, angle, reshape=False, out=None, *args, **kwargs):
        if isinstance(signal, SignalWrapper):
            signal = signal.signal
        data = rotate(signal.data, angle, reshape=reshape, *args, **kwargs)
        if out is None:
            sig = signal._deepcopy_with_new_data(None)
        else:
            sig = out
        sig.data  = data
        if out is None:
            return sig
        else:
            if reshape:
                out.get_dimensions_from_data()
            out.events.data_changed.trigger()
    
    def show_rotate_dialog(self):
        signal, space, _ = self.ui.get_selected_plot()
        if space not in ("navigation", "signal"):
            return
        self.dialog = ImageRotationDialog(signal, space, self.ui)
        self.dialog.show()
        # TODO: Use self.settings to keep dialog settings
        
        
class ImageRotationDialog(ExToolWindow):
    def __init__(self, signal, axes, parent):
        super(ImageRotationDialog, self).__init__(parent)
        self.ui = parent
        self.create_controls()
        self.accepted.connect(self.ok)
        self.rejected.connect(self.close_new)
        self.signal = signal
        self.new_out = None
        self._connected_updates = False
        if isinstance(axes, basestring):
            axm = signal.signal.axes_manager
            if axes.startswith("nav"):
                axes = (axm._axes.index(axm.navigation_axes[0]),
                        axm._axes.index(axm.navigation_axes[1]))
            elif axes.startswith("sig"):
                axes = (axm._axes.index(axm.signal_axes[0]),
                        axm._axes.index(axm.signal_axes[1]))
        self.axes = axes
        self.setWindowTitle("Rotate")  #TODO: tr
        
        # TODO: Add dynamic rotation, e.g. one that rotates when source 
        # signal's data_changed event triggers
        
    def connect(self):
        # TODO: Don't have to con/dis those in gbo
        self.opt_new.toggled.connect(self.close_new)
        self.num_angle.valueChanged.connect(self.update)
        self.chk_grid.toggled.connect(self.update)
        self.num_grid.valueChanged.connect(self.update)
        self.chk_reshape.toggled.connect(self.update)
        self.opt_new.toggled.connect(self.update)
        self.opt_replace.toggled.connect(self.update)
    
    def disconnect(self):
        self.num_angle.valueChanged.disconnect(self.update)
        self.chk_grid.toggled.disconnect(self.update)
        self.num_grid.valueChanged.disconnect(self.update)
        self.chk_reshape.toggled.disconnect(self.update)
        self.opt_new.toggled.disconnect(self.update)
        self.opt_replace.toggled.disconnect(self.update)
        
    def ok(self):
        # Draw figure if not already done
        if not self.gbo_preview.isChecked():
            self.update()
        
        # Clean up event connections
        if self.new_out is not None:
            self.connect_update_plot(self.new_out.signal, disconnect=True)
        
    def close_new(self, value=False):
        if self.new_out is not None and not value:
            self.new_out.close()
            self.new_out = None
            self._connected_updates = False
    
    def set_preview(self, value):
        if value:
            self.connect()
            self.update()
        else:
            self.disconnect()
            self.close_new()
            
    def _axes_in_nav(self):
        axm = self.signal.signal.axes_manager
        navidx = [axm._axes.index(ax) for ax in axm.navigation_axes]
        if self.axes[0] in navidx:
            return True
        return False
        
    def connect_update_plot(self, signal, disconnect=False):
        if self._connected_updates != disconnect:
            return  # Nothing to do, prevent double connections
        if self._axes_in_nav():
            f = signal._plot.navigator_plot._update
        else:
            f = signal._plot.signal_plot._update
        if disconnect:
            signal.events.data_changed.disconnect(f)
        else:
            signal.events.data_changed.connect(f)
        self._connected_updates = not disconnect
        
    def update(self):
        angle = self.num_angle.value()
        reshape = self.chk_reshape.isChecked()
        if self.opt_new.isChecked():
            if self.new_out is None:
                out = None
            else:
                out = self.new_out.signal
        elif self.opt_replace.isChecked():
            out = self.signal.signal
        else:
            return  # Indeterminate state, do nothing
        
        tmp_suppress = reshape and self._connected_updates
        if tmp_suppress:
            self.connect_update_plot(out, disconnect=True)
        # Do atual rotation
        s = ImageRotation_Plugin.rotate_signal(self.signal.signal, angle, 
                                               reshape=reshape, 
                                               out=out, axes=self.axes)
        if tmp_suppress:
            self.connect_update_plot(out)
            
        if out is None:
            name = self.signal.name + "[Rotated]"
            self.new_out = self.ui.add_signal_figure(s, name)
            self.connect_update_plot(s)
        else:
            s = out
        
        if self.chk_grid.isChecked() is True:
            pass

        
    def create_controls(self):
        """
        Create UI controls.
        """
        vbox = QVBoxLayout()
        
        form = QFormLayout()
        self.num_angle = QDoubleSpinBox()
        self.num_angle.setValue(0.0)
        #TODO: tr
        form.addRow("Angle:", self.num_angle)
        vbox.addLayout(form)
        
        self.gbo_preview = QGroupBox("Preview")
        self.gbo_preview.setCheckable(True)
        self.gbo_preview.setChecked(False)
        gbo_vbox = QVBoxLayout()
        self.chk_grid = QCheckBox("Grid")
        self.chk_grid.setChecked(False)
        self.num_grid = QSpinBox()
        self.num_grid.setValue(4)
        self.num_grid.setMinimum(1)
        self.num_grid.setEnabled(False)
        self.chk_grid.toggled[bool].connect(self.num_grid.setEnabled)
        gbo_vbox.addWidget(self.chk_grid)
        gbo_vbox.addWidget(self.num_grid)
        self.gbo_preview.setLayout(gbo_vbox)
        vbox.addWidget(self.gbo_preview)
        
        self.gbo_preview.toggled[bool].connect(self.set_preview)
        
        self.gbo_output = QGroupBox("Output")
        self.opt_new = QRadioButton("New signal")
        self.opt_replace = QRadioButton("In place")
        self.opt_new.setChecked(True)
        gbo_vbox2 = QVBoxLayout()
        gbo_vbox2.addWidget(self.opt_new)
        gbo_vbox2.addWidget(self.opt_replace)
        self.gbo_output.setLayout(gbo_vbox2)
        vbox.addWidget(self.gbo_output)
        
        self.chk_reshape = QCheckBox("Resize to fit")
        self.chk_reshape.setChecked(False)
        vbox.addWidget(self.chk_reshape)
        
        self.btn_ok = QPushButton("&OK")
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("&Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_ok)
        hbox.addWidget(self.btn_cancel)
        vbox.addLayout(hbox)
        
        vbox.addStretch(1)
        self.setLayout(vbox)
        