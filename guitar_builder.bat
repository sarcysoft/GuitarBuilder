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
:: Default to empty
set "NO_CUT_ARG="
set "CONFIG_ARG="
set "EXPORT_CONFIG_FLAG="
set "EXPORT_VAL_ARG="

:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="--no-cut" (
    set "NO_CUT_ARG=--no-cut"
    shift
    goto :parse_args
)
if "%~1"=="--no_cut" (
    set "NO_CUT_ARG=--no-cut"
    shift
    goto :parse_args
)
if "%~1"=="no_cut" (
    set "NO_CUT_ARG=--no-cut"
    shift
    goto :parse_args
)
if "%~1"=="--export-config" (
    set "EXPORT_CONFIG_FLAG=1"
    set "NEXT_ARG=%~2"
    if defined NEXT_ARG (
        set "FIRST_CHAR=!NEXT_ARG:~0,1!"
        if not "!FIRST_CHAR!"=="-" (
            set "EXPORT_VAL_ARG=!NEXT_ARG!"
            shift
        )
    )
    shift
    goto :parse_args
)
if "%~1"=="--export_config" (
    set "EXPORT_CONFIG_FLAG=1"
    set "NEXT_ARG=%~2"
    if defined NEXT_ARG (
        set "FIRST_CHAR=!NEXT_ARG:~0,1!"
        if not "!FIRST_CHAR!"=="-" (
            set "EXPORT_VAL_ARG=!NEXT_ARG!"
            shift
        )
    )
    shift
    goto :parse_args
)
if "%~1"=="--config" (
    set "CONFIG_ARG=%~2"
    shift
    shift
    goto :parse_args
)
:: Otherwise, assume it is a config argument (e.g. sarcaster)
set "CONFIG_ARG=%~1"
shift
goto :parse_args

:args_done

if defined EXPORT_CONFIG_FLAG (
    echo Exporting guitar model configuration...
    set "CMD_ARGS="
    if defined CONFIG_ARG set "CMD_ARGS=--config !CONFIG_ARG!"
    if defined EXPORT_VAL_ARG (
        set "CMD_ARGS=!CMD_ARGS! --export-config !EXPORT_VAL_ARG!"
    ) else (
        set "CMD_ARGS=!CMD_ARGS! --export-config"
    )
    python "%SCRIPT_DIR%configure_guitar.py" !CMD_ARGS!
    goto :eof
)

if defined CONFIG_ARG (
    echo Generating guitar model for config: %CONFIG_ARG%...
    python "%SCRIPT_DIR%configure_guitar.py" --config %CONFIG_ARG% --generate
    
    if defined NO_CUT_ARG (
        echo Running setup_scene.py with --no-cut and --config %CONFIG_ARG%...
        "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py" -- --no-cut --config %CONFIG_ARG%
    ) else (
        echo Running setup_scene.py with --config %CONFIG_ARG%...
        "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py" -- --config %CONFIG_ARG%
    )
) else (
    if defined NO_CUT_ARG (
        echo Running setup_scene.py with --no-cut...
        "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py" -- --no-cut
    ) else (
        echo Running setup_scene.py...
        "%BLENDER_CMD%" --background --python "%SCRIPT_DIR%setup_scene.py"
    )
)

endlocal

