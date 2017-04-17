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
TYPES = ["image/tiff"]
if not os.environ.get('XDG_DATA_HOME'):
    os.environ['XDG_DATA_HOME'] = os.path.expanduser('~/.local/share')
MIMEPATH = os.path.join(os.environ["XDG_DATA_HOME"], "mime")

if not os.path.exists(MIMEPATH):
    os.makedirs(MIMEPATH)
if not os.path.exists(os.path.join(MIMEPATH, "packages")):
    os.makedirs(os.path.join(MIMEPATH, "packages"))

for fformat in io_plugins:
    name = fformat.format_name
    if name in ["netCDF", "Signal2D", "Protochips", "TIFF"]:
        continue
    if name == "HDF5":
        extensions = set(["hspy", "hdf5"])
        defext = "hspy"
    else:
        extensions = set([ext.lower() for ext in fformat.file_extensions])
        defext = fformat.file_extensions[fformat.default_extension]
    extstr = "\n".join(
        ["<glob pattern=\"*.{}\"/>".format(ext) for ext in extensions])
    if name == "HDF5":
        extstr += '<sub-class-of type="application/x-hdf"/>\n'
    elif defext == "rpl":
        extstr += '<sub-class-of type="text/plain"/>\n'
    mime = MIME.format(defext, name, extstr)

    TYPES.append("application/x-{}".format(defext))
    fpath = os.path.join(
        MIMEPATH, "packages", "application-hyperspy-{}.xml".format(defext))
    print("Writing {}".format(fpath))
    with open(fpath, "w") as f:
        f.write(mime)
    # Register
print("Updating mime database")
subprocess.run(['update-mime-database',  MIMEPATH])
if not os.environ.get('XDG_DATA_HOME'):
    os.environ['XDG_DATA_HOME'] = os.path.expanduser('~/.local/share')
p = subprocess.run(["which", "hyperspyui"], stdout=subprocess.PIPE)
if p.stdout.decode('utf-8'):
    EXEC = p.stdout.decode('utf-8').replace("\n", "")
else:
    EXEC = "hyperspyui"
apps_dir = os.path.join(os.environ['XDG_DATA_HOME'], "applications/")
with open(os.path.join(apps_dir, "hyperspyui.desktop"), "w") as f:
    print("Writing hyperspyui.desktop to {}".format(apps_dir))
    f.write(DESKTOP.format(EXEC, ";".join(TYPES), _PKGDIR))

print("Updating desktop database")
subprocess.run(['update-desktop-database', apps_dir])
