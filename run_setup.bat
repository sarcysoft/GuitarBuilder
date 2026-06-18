@echo off
setlocal enabledelayedexpansion

:: Determine directory of this script
set "SCRIPT_DIR=%~dp0"

:: Default to 'blender' as the command
set "BLENDER_CMD=blender"

:: Check if blender is in PATH
where blender >nul 2>nul
if %ERRORLEVEL% equ 0 goto :find_args

:: If not in PATH, search in standard Program Files locations
set "FOUND_BLENDER="
for /d %%D in ("C:\Program Files\Blender Foundation\Blender*") do (
    if exist "%%D\blender.exe" (
        set "FOUND_BLENDER=%%D\blender.exe"
    )
)

if not defined FOUND_BLENDER (
    echo Warning: blender.exe was not found in PATH or in "C:\Program Files\Blender Foundation".
    echo Attempting to run 'blender' anyway...
    goto :find_args
)

set "BLENDER_CMD=%FOUND_BLENDER%"

:find_args
:: Default to false
set "NO_CUT_ARG="

:: Check arguments passed to this script
for %%A in (%*) do (
    if "%%A"=="--no-cut" set "NO_CUT_ARG=--no-cut"
    if "%%A"=="--no_cut" set "NO_CUT_ARG=--no-cut"
    if "%%A"=="no_cut"   set "NO_CUT_ARG=--no-cut"
)

if defined NO_CUT_ARG (
    echo Running setup_scene.py with --no-cut - no cuts, exporting full body...
    "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py" -- --no-cut
) else (
    echo Running setup_scene.py - performing cuts and exporting all parts...
    "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py"
)

endlocal
