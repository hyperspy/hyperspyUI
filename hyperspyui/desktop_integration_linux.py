import os
from pathlib import Path
import subprocess
from hyperspy.io_plugins import io_plugins


DESKTOP = \
    """[Desktop Entry]
Exec={} %F
Name=HyperSpy UI
Terminal=false
MimeType={}
Icon={}/images/hyperspy.svg
Type=Application
X-MultipleArgs=true
Categories=Science;Physics;DataVisualization;

"""

MIME = \
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
MIMEPATH = os.path.join(os.environ["XDG_DATA_HOME"], "mime")
APPS_DIR = os.path.join(os.environ['XDG_DATA_HOME'], "applications/")


def create_mime_file(hspy_format, types=None, update_db=False):
    if not os.path.exists(MIMEPATH):
        os.makedirs(MIMEPATH)
    if not os.path.exists(os.path.join(MIMEPATH, "packages")):
        os.makedirs(os.path.join(MIMEPATH, "packages"))
    name = hspy_format.format_name
    if name == "HDF5":
        extensions = set(["hspy", "hdf5"])
        defext = "hspy"
    else:
        extensions = set([ext.lower() for ext in hspy_format.file_extensions])
        defext = hspy_format.file_extensions[hspy_format.default_extension]
    extstr = "\n".join(
        ["<glob pattern=\"*.{}\"/>".format(ext) for ext in extensions])
    if name == "HDF5":
        extstr += '<sub-class-of type="application/x-hdf"/>\n'
    elif defext in ("rpl", "msa", "dens"):
        extstr += '<sub-class-of type="text/plain"/>\n'
    mime = MIME.format(defext, name, extstr)

    fpath = os.path.join(
        MIMEPATH, "packages", "application-hyperspy-{}.xml".format(defext))
    print("Writing {}".format(fpath))
    with open(fpath, "w") as f:
        f.write(mime)
    if types:
        types.append("application/x-{}".format(defext))
    if update_db:
        print("Updating mime database")
        subprocess.run(['update-mime-database',  MIMEPATH])


def get_hyperspyui_exec_path():
    p = subprocess.run(["which", "hyperspyui"], stdout=subprocess.PIPE)
    if p.stdout.decode('utf-8'):
        hspyui_exec_path = p.stdout.decode('utf-8').replace("\n", "")
    else:
        hspyui_exec_path = "hyperspyui"
    return hspyui_exec_path


def write_desktop_file(types=""):
    with open(os.path.join(APPS_DIR, "hyperspyui.desktop"), "w") as f:
        print("Writing hyperspyui.desktop to {}".format(APPS_DIR))
        f.write(DESKTOP.format(get_hyperspyui_exec_path,
                               ";".join(types), _PKGDIR))

def run_desktop_integration(
        exclude_formats=["netCDF", "Signal2D", "Protochips", "TIFF"]):
    types = ["image/tiff"]
    for hspy_format in io_plugins:
        if hspy_format.format_name not in exclude_formats:
            create_mime_file(hspy_format=hspy_format, types=types)
    print("Updating mime database")
    subprocess.run(['update-mime-database',  MIMEPATH])
    write_desktop_file(types=types)
    print("Updating desktop database")
    subprocess.run(['update-desktop-database', APPS_DIR])

if __name__ == "__main__":
    run_desktop_integration()
