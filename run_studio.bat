@echo off
setlocal
where godot >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" godot --path project
    exit /b 0
)

for /f "delims=" %%I in ('powershell -NoProfile -Command "(Get-ChildItem -Path \"$env:LOCALAPPDATA\Microsoft\WinGet\Packages\" -Recurse -Filter \"Godot*.exe\" | Select-Object -First 1).FullName"') do set "GODOT_EXE=%%I"

if exist "%GODOT_EXE%" (
    start "" "%GODOT_EXE%" --path project
    exit /b 0
)

echo Error: Godot Engine executable could not be found.
pause
exit /b 1
