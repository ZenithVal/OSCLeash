#new installer build script, using cx_freeze stable(6.15.x), and python 3.11 (3.12 should be supported in cx_freeze 6.16.x)
from cx_Freeze import setup, Executable
#change any area that says change me
#update items in "Summary_Data"
#update version numbers on new releases, i took the liberty of doing 2.1.1 for a new exe/installer

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'console'

#Create EXE and 2 shortcuts
executables = [
    #Desktop ShortCut
    Executable('OSCLeash.py', 
    base=base,
    shortcut_name="OSCLeash",
    shortcut_dir="DesktopFolder",
    icon="Resources\VRChatOSCLeash.ico",
    ),
    #StartMenu ShortCut
    Executable('OSCLeash.py', 
    base=base,
    shortcut_name="OSCLeash",
    shortcut_dir="MyProgramMenu",
    icon="Resources\VRChatOSCLeash.ico",
    ),
]

#not 100% sure what this is for, and idk if anything will break removing it
directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

#Data to show in win32_programs if, i understand correctly
msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", "2.1.1", None, "A program to control an avatar with a leash over OSC", "IconId", None),
    ],
    "Icon": [
        ("IconId", "Resources\VRChatOSCLeash.ico"),
    ],
}

#Values for the MSI installer file.
bdist_msi_options = {
    #we dont need the exe callable via cmd without the fullpath
    "add_to_path": False,
    "data": msi_data,
    #dont change  this, this tells windows what version to remove when performing an upgrade
    "upgrade_code": "{111834E6-DD67-4BD9-A402-A38A8424C39E}",
    #this changes the icon in Add/Remove programs, sadly not the MSI it'self
    "install_icon":  "Resources\VRChatOSCLeash.ico",
    #update the details tab in the MSI properties, these are the only values alloted
    "summary_data": {
        "author": "Change Me",
        "comments": "Change Me",
        "keywords": "VRCat, OSC, Leash, UwU",
    },
}

#setting for the EXE, and options for python setup.py <options>
setup(name='OSCLeash',
      version = '2.1.1',
      description = 'A program to control an avatar with a leash over OSC',
      license = "MIT License",
      options = {
      'build_exe': build_options,
      'bdist_msi': bdist_msi_options,
      },
      executables = executables)
