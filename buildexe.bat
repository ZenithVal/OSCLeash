pyinstaller %~dp0/OSCLeash.py --onefile --ico %~dp0/VRChatOSCLeash.ico --name OSCLeash --noconfirm --paths=%~dp0/env/Lib/site-packages
move /Y OSCLeash.spec %~dp0