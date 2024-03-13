@REM This uses pyinstaller to create a single binary executable. Adjust as needed for your system.

cd ..\
set ICON_PATH=Resources\VRChatOSCLeash.ico
set SCRIPT_PATH=OSCLeash.py
set BUILD_PATH=Scripts\dist

pyinstaller --noconfirm --onefile --console --icon "%ICON_PATH%"  "%SCRIPT_PATH%"

@REM cleanup post build
del /q OSCLeash.spec
rmdir /s /q build
xcopy /i /s /y /q dist Scripts\dist 
rmdir /s /q dist

pause