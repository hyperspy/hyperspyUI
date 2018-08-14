import sys
from hyperspyui.singleapplication import get_app
from qtpy import API

key = 'test_single_app'


def handle_second_instance(argv):
    print(argv)
    app.exit()


try:
    app = get_app(key)
except SystemExit:
    print('Exiting early!')
    raise

if "pyqt" in API:
    app.messageAvailable.connect(handle_second_instance)
elif API == 'pyside':
    app.messageReceived.connect(handle_second_instance)

print('Loaded app')
sys.exit(app.exec_())
