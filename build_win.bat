python setup.py bdist_wininst  --plat-name=win32 --install-script hyperspyui_win_post_install.py  --user-access-control auto
python setup.py bdist_wininst  --plat-name=win-amd64 --install-script hyperspyui_win_post_install.py  --user-access-control auto
python setup.py bdist_msi  --plat-name=win32 --install-script hyperspyui_win_post_install.py
python setup.py bdist_msi  --plat-name=win-amd64 --install-script hyperspyui_win_post_install.py
