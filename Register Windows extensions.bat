ECHO OFF
PUSHD %~dp0

REG ADD "HKCR\HyperSpy.Document\DefaultIcon" /t REG_SZ /d %~dp0images\hyperspy.ico

ASSOC .hdf5=HyperSpy.Document
FTYPE HyperSpy.Document="%%PYTHONPATH%%pythonw.exe" "%~dp0hyperspyui\main.py" "%%1" %%*

POPD