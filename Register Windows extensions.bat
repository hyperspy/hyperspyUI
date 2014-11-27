ECHO OFF
PUSHD %~dp0

ASSOC .hdf5=HyperSpy.Document
FTYPE HyperSpy.Document="%%PYTHONPATH%%pythonw.exe" "%~dp0hyperspyui\main.py" "%%1" %%*

REM HKEY_CLASSES_ROOT\MyTextFile\DefaultIcon
REM     @="C:\WINDOWS\explorer.exe,2"

POPD