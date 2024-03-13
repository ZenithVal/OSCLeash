@REM This uses CX_Freeze to create an MSI installer file.
copy BuildInstaller.py ..\
cd ..\
BuildInstaller.py bdist_msi

@REM cleanup post build
del /q BuildInstaller.py
rmdir /s /q build
xcopy /i /s /y /q dist Scripts\dist 
rmdir /s /q dist

pause