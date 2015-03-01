# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:04:17 2014

@author: Vidar Tonaas Fauske
"""

from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


class ConsoleWidget(RichIPythonWidget):

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
            app.exit()  # TODO: Really?

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
