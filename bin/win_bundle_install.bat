@ECHO OFF

CALL %1

SET params=
SET CMD=%2

(
SETLOCAL ENABLEDELAYEDEXPANSION
SET Skip=2

FOR %%I IN (%*) DO IF !Skip! LEQ 0 ( 
        SET params=!params! %%I
    ) ELSE SET /A Skip-=1
)
(
ENDLOCAL
SET params=%params%
)

%CMD% %params%