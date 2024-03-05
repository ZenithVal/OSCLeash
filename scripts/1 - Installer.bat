@REM This uses CX_Freeze to create an MSI installer file.
copy BuildInstaller.py ..\
cd ..\
BuildInstaller.py bdist_msi
del /q BuildInstaller.py