@ECHO OFF
PUSHD %~dp0

1>nul 2>nul REG ADD "HKCR\HyperSpy.Document\DefaultIcon" /t REG_SZ /f /d %~dp0images\hyperspy.ico

1>nul 2>nul ASSOC .hdf5=HyperSpy.Document
1>nul 2>nul FTYPE HyperSpy.Document="%%PYTHONPATH%%pythonw.exe" "%~dp0hyperspyui\main.py" "%%1" %%*

POPD
IF %ERRORLEVEL% NEQ 0 (
	ECHO You need to run this batch as an Administrator
	PAUSE
)