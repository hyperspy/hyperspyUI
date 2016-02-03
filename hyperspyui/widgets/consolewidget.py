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
"""
Created on Tue Nov 04 16:04:17 2014

@author: Vidar Tonaas Fauske
"""

try:
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess import QtInProcessKernelManager
except ImportError:
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget as \
        RichJupyterWidget
    from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


class ConsoleWidget(RichJupyterWidget):

    def __init__(self, *args, **kwargs):
        super(ConsoleWidget, self).__init__(*args, **kwargs)

        # Create an in-process kernel
        app = guisupport.get_app_qt4()
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()

        # Set the kernel data
        self.kernel = kernel_manager.kernel
        self.kernel.gui = 'qt4'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            app.exit()

        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client
        self.exit_requested.connect(stop)

    def ex(self, source):
        self.kernel.shell.ex(source)

    def push(self, variables):
        self.kernel.shell.push(variables)

    def _execute(self, source, hidden):
        """ Execute 'source'. If 'hidden', do not show any output.

        See parent class :meth:`execute` docstring for full details.

        Overriden copy to move 'executing' event before it is actually executed
        """
        if not hidden:
            self.executing.emit(source)
        msg_id = self.kernel_client.execute(source, hidden)
        self._request_info['execute'][
            msg_id] = self._ExecutionRequest(msg_id, 'user')
        self._hidden = hidden
