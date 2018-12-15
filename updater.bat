@echo OFF
:: This batch file exists to run updater.ps1 without hassle
pushd %~dp0
if exist "%~dp0\installer\updater.ps1" (
    set updater_script="%~dp0\installer\updater.ps1"
) else (
    set updater_script="%~dp0\updater.ps1"
)
powershell -noprofile -nologo -executionpolicy bypass -File %updater_script%

@pause
