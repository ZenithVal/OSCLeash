@REM This uses CX_Freeze to create an MSI installer file.
copy BuildInstaller.py ..\
cd ..\
BuildInstaller.py bdist_msi
del /q BuildInstaller.py

@REM Don't need to keep this.
del "%REPO_PATH%\Build
del "%REPO_PATH%\Scripts\build"