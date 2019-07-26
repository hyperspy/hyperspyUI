import sys
import argparse

parser = argparse.ArgumentParser(
    description='Install HyperspyUI into the OS')
parser.add_argument('--remove', action="store_true", help='uninstall flag')
parser.add_argument('--no-shortcuts', action="store_true",
                    help='(Windows only) do not create shortcuts')

args = parser.parse_args()


if __name__ == "__main__":
    if sys.platform.startswith("linux"):
        from hyperspyui.desktop_integration_linux import run_desktop_integration_linux
        run_desktop_integration_linux(args)
    elif sys.platform == 'win32':
        from hyperspyui.desktop_integration_windows import run_desktop_integration_windows
        run_desktop_integration_windows(args)
    else:
        raise NotImplementedError(
            "Desktop integration is currently only available for Linux and Microsoft Windows. Current OS is {}.".format( sys.platform))