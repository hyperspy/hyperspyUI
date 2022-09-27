import os
from pathlib import Path
import subprocess

try:
    # HyperSpy >=2.0
    from rsciio import IO_PLUGINS
except Exception:
    # HyperSpy <2.0
    from hyperspy.io_plugins import io_plugins as IO_PLUGINS


_DESKTOP = \
    """[Desktop Entry]
Exec={} %F
Name=HyperSpy UI
Terminal=false
MimeType={}
Icon=application-x-hspy
Type=Application
X-MultipleArgs=true
Categories=Science;Physics;DataVisualization;

"""

_MIME = \
    """<?xml version="1.0"?>
<mime-info xmlns='http://www.freedesktop.org/standards/shared-mime-info'>
<mime-type type="application/x-{}">
<comment>{}</comment>
{}
</mime-type>
</mime-info>
"""

_PKGDIR = Path(__file__).resolve().parent
if not os.environ.get('XDG_DATA_HOME'):
    os.environ['XDG_DATA_HOME'] = os.path.expanduser('~/.local/share')
_MIMEPATH = os.path.join(os.environ["XDG_DATA_HOME"], "mime")
APPS_DIR = os.path.join(os.environ['XDG_DATA_HOME'], "applications/")


def create_mime_file(plugin, types=None, update_db=False):
    if not os.path.exists(_MIMEPATH):
        os.makedirs(_MIMEPATH)
    if not os.path.exists(os.path.join(_MIMEPATH, "packages")):
        os.makedirs(os.path.join(_MIMEPATH, "packages"))

    # Try first with attribute (HyperSpy <2.0), fallback with dictionary (RosettaSciIO)
    name = getattr(plugin, 'format_name', plugin['name'])

    if name == "HDF5":
        extensions = set(["hspy", "hdf5"])
        defext = "hspy"
    else:
        # Try first with attribute (HyperSpy <2.0), fallback with dictionary (RosettaSciIO)
        extensions = getattr(plugin, 'file_extensions', plugin['file_extensions'])
        defext = getattr(plugin, 'default_extension', plugin['default_extension'])

    extstr = "\n".join(
        ["<glob pattern=\"*.{}\"/>".format(ext) for ext in extensions])
    if name == "HDF5":
        extstr += '<sub-class-of type="application/x-hdf"/>\n'
    elif defext in ("rpl", "msa", "dens"):
        extstr += '<sub-class-of type="text/plain"/>\n'
    mime = _MIME.format(defext, name, extstr)

    fpath = os.path.join(
        _MIMEPATH, "packages", "application-hyperspy-{}.xml".format(defext))
    print("Writing {}".format(fpath))
    with open(fpath, "w") as f:
        f.write(mime)
    if types:
        types.append("application/x-{}".format(defext))
    if update_db:
        print("Updating mime database")
        subprocess.run(['update-mime-database',  _MIMEPATH])


def get_hyperspyui_exec_path():
    p = subprocess.run(["which", "hyperspyui"], stdout=subprocess.PIPE)
    if p.stdout.decode('utf-8'):
        hspyui_exec_path = p.stdout.decode('utf-8').replace("\n", "")
    else:
        hspyui_exec_path = "hyperspyui"
    return hspyui_exec_path


def remove_desktop_file():
    fpath = os.path.join(APPS_DIR, "hyperspyui.desktop")
    if os.path.isfile(fpath):
        os.remove(fpath)
        print(fpath + " removed.")
    else:
        print("The file hyperspyui.desktop was not found at the default location %s" % fpath)
        print("Nothing done.")


def write_desktop_file(types=""):
    with open(os.path.join(APPS_DIR, "hyperspyui.desktop"), "w") as f:
        print("Writing hyperspyui.desktop to {}".format(APPS_DIR))
        f.write(_DESKTOP.format(get_hyperspyui_exec_path(), ";".join(types)))


def register_hspy_icon():
    for size in (16, 22, 32, 48, 64, 128, 256):
        print("Registering icon size {}".format(size))
        subprocess.run(["xdg-icon-resource", "install",  "--context",
                        "mimetypes",
                        "--size", str(size),
                        "{}/images/icon/hyperspy{}.png".format(_PKGDIR, size),
                        "application-x-hspy"])


def run_desktop_integration_linux(args,):
    if args.remove:
        remove_desktop_file()
    else:
        exclude_formats=["netCDF", "Signal2D", "Protochips", "TIFF"]
        types = ["image/tiff"]

        for plugin in IO_PLUGINS:
            # Try first with attribute (HyperSpy <2.0), fallback with dictionary (RosettaSciIO)
            format_name = getattr(plugin, 'format_name', plugin['name'])
            if format_name not in exclude_formats:
                create_mime_file(plugin=plugin, types=types)
        print("Updating mime database")
        subprocess.run(['update-mime-database',  _MIMEPATH])
        register_hspy_icon()
        write_desktop_file(types=types)
        print("Updating desktop database")
        subprocess.run(['update-desktop-database', APPS_DIR])
