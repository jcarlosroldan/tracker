@echo off
setlocal

rem Check if the batch file is already in the startup folder
set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if not exist "%startup_folder%\%~nx0" (
    copy "%~f0" "%startup_folder%"
)

start /B pythonw D:\Dropbox\propio\python\tracker\start.py > nul 2>&1

endlocal
exit