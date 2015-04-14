python setup.py clean
python setup.py build
python setup.py bdist_wheel
python setup.py bdist_wininst  --plat-name=win32 --install-script hyperspyui_install.py  --user-access-control auto
python setup.py bdist_wininst  --plat-name=win-amd64 --install-script hyperspyui_install.py  --user-access-control auto
