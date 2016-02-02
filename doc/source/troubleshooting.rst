
Troubleshooting
===============

    "Something went wrong!"

If you find yourself unable to complete some of the steps in this guide, or if
the application doesn't do something it should or is supposed to, please
consider letting us know. The best way is maybe to go to the `HyperSpy gitter
chat`_ first to discuss the issue, but if there's no help forthcoming, please
submit an issue on the `HyperSpyUI Github page`_.

.. _HyperSpy gitter chat: https://gitter.im/hyperspy/hyperspy
.. _HyperSpyUI Github page: https://github.com/vidartf/hyperspyUI/issues


Known issues
-----------------

For a list of previously reported issues, see the `HyperSpyUI Github page`_.
At the time of release, no major issues are known, but the following can be 
worth noticing:

    Closed signals are not always cleared from memory
        This is dependent on Pythons garbadge collector, and might be caused by
        remaining references to the signal held by parts of the UI or matplotlib
        figures. A program restart might be necessary to solve this, but using
        `Close all`_ might also help clearing out any remaining references.

    Signals can get stuck in "limbo"
        If a signal gets stuck in an invalid state, it might be problematic
        to close it fully. Similar to the above problem, this might be
        fixed by the `Close all`_ action, or in the last resort a program
        restart might be necessary.


Error output
-----------------

To help diagnose problems, it would be helpful to include the application
log. Depending on how you launch the program, there are different ways of
obtaining this log output. The easiest is if the program is launched from
a terminal, in which case the log is piped directly to its console. If 
you've not launched it with a terminal, the log is attempted written to
the folder of the ``launch.py`` file. If that location is noe writable,
the log file is attempted written to the users home folder (OS dependent).
In either case, the log file is named ``hyperspyui.log``.

Note that for a complete error output to the above sources, the
`output to console`_ settings option should be disabled.
