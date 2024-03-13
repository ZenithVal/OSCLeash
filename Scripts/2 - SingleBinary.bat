@REM This uses pyinstaller to create a single binary executable. Adjust as needed for your system.

@echo off
set REPO_PATH=%~dp0..
set ICON_PATH=%REPO_PATH%\Resources\VRChatOSCLeash.ico
set SCRIPT_PATH=%REPO_PATH%\OSCLeash.py
set BUILD_PATH=%REPO_PATH%\Build\dist

pyinstaller --noconfirm --onefile --console --icon "%ICON_PATH%"  "%SCRIPT_PATH%"

@REM Don't need to keep this.
del "%REPO_PATH%\Build"
del "%REPO_PATH%\Scripts\build"

pause