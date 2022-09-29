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
import sys

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


def _init_asyncio_patch():
    """set default asyncio policy to be compatible with tornado
    Tornado 6 (at least) is not compatible with the default
    asyncio implementation on Windows

    Pick the older SelectorEventLoopPolicy on Windows
    if the known-incompatible default policy is in use.
    do this as early as possible to make it a low priority and overrideable

    ref: https://github.com/tornadoweb/tornado/issues/2608
    FIXME: if/when tornado supports the defaults in asyncio,
    remove and bump tornado requirement for py38
    """
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        try:
            from asyncio import (
                WindowsProactorEventLoopPolicy,
                WindowsSelectorEventLoopPolicy,
                get_event_loop_policy,
                set_event_loop_policy,
            )
        except ImportError:
            pass
            # not affected
        else:
            if type(get_event_loop_policy()) is WindowsProactorEventLoopPolicy:
                # WindowsProactorEventLoopPolicy is not compatible with tornado 6
                # fallback to the pre-3.8 default of Selector
                set_event_loop_policy(WindowsSelectorEventLoopPolicy())


class ConsoleWidget(RichJupyterWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        _init_asyncio_patch()
        # Create an in-process kernel
        app = guisupport.get_app_qt4()
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()

        # Set the kernel data
        self.kernel = kernel_manager.kernel
        self.kernel.gui = 'qt'

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
        self._request_info['execute'][msg_id] = self._ExecutionRequest(
            msg_id, 'user', hidden)
        self._hidden = hidden
