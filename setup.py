import sys
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [],
    'zip_exclude_packages': [],
    'excludes': [],
}

base = 'console'

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", "2.1.1", None, "Scale your avatar over OSC", "IconId", None),
    ],
    "Icon": [
        ("IconId", "Resources/VRChatOSCLeash.ico"),
    ],
    "Shortcut": [
        ("DesktopShortcut", "DesktopFolder", "OSCLeash",
         "TARGETDIR", "[TARGETDIR]OSCLeash.exe",
         None, None, None, None, None, None, "TARGETDIR"),
        ("StartMenuShortcut", "MyProgramMenu", "OSCLeash",
         "TARGETDIR", "[TARGETDIR]OSCLeash.exe",
         None, None, None, None, None, None, "TARGETDIR"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    "upgrade_code": "{111834E6-DD67-4BD9-A402-A38A8424C39E}",
    "output_name": "OSCLeash.msi",
    "summary_data": {
        "author": "Various Authors",
        "comments": "https://github.com/ZenithVal/OSCLeash/releases",
        "keywords": "VRChat, OSC, Leash, OSCLeash",
    }
}
bdist_appimage_options = {
    "target_name": "OSCLeash.AppImage",
}

# Pick the right icon per platform
if sys.platform == "win32":
    icon = 'Resources/VRChatOSCLeash.ico'
else:
    icon = 'Resources/VRChatOSCLeash.png'

executables = [
    Executable(
        'OSCLeash.py',
        base=base,
        icon=icon,
    ),
]

setup(name='OSCLeash',
      version = '2.1.1',
      description = "Change your avatar's scale over osc",
      license = "MIT License",
      options = {
      'build_exe': build_options,
      'bdist_msi': bdist_msi_options,
      'bdist_appimage': bdist_appimage_options,
      },
      executables = executables)
