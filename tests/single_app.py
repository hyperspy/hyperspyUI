import sys
from hyperspyui.singleapplication import get_app
from python_qt_binding import QT_BINDING

key = 'test_single_app'


def handle_second_instance(argv):
    print(argv)
    app.exit()


try:
    app = get_app(key)
except SystemExit:
    print('Exiting early!')
    raise

if QT_BINDING == 'pyqt':
    app.messageAvailable.connect(handle_second_instance)
elif QT_BINDING == 'pyside':
    app.messageReceived.connect(handle_second_instance)

print('Loaded app')
sys.exit(app.exec_())
