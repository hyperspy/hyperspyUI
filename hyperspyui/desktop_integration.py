
import argparse

parser = argparse.ArgumentParser(
    description='Install HyperspyUI into the OS')
parser.add_argument('-remove', action="store_true", help='uninstall flag')
parser.add_argument('-no-shortcuts', action="store_true",
                    help='(Windows only) do not create shortcuts')
parser.add_argument('-filetypes', dest='filetypes', nargs='*',
                    default=['hdf5', 'msa', 'dens', 'blo'],
                    help='filetypes to register with HyperspyUI')

args = parser.parse_args()
filetypes = args.filetypes
for i, f in enumerate(filetypes):
    if not 'a'.startswith('.'):
        filetypes[i] = '.' + f


if __name__ == "__main__":
    if "linux" in sys.platform:
        from hyperspyui.desktop_integration_linux import run_desktop_integration_linux
        run_linux_desktop_integration(args)
    elif platform.system().lower() == 'windows':
        from hyperspyui.desktop_integration_windows import run_desktop_integration_windows
        run_windows_desktop_integration(args)
    else:
        raise NotImplementedError(
            "Desktop integration is currently only available for Linux and Microsoft Windows. Current OS is {}.".format( sys.platform))