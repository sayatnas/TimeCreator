@echo off
REM Setup TimeCreator to start with Windows
REM This creates a shortcut in the Windows Startup folder

echo Setting up TimeCreator to start with Windows...

REM Get the current directory
set CURRENT_DIR=%~dp0

REM Get the startup folder path
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Create a shortcut to the start script
echo Creating shortcut in startup folder...

REM Use PowerShell to create the shortcut (using silent VBS version)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\TimeCreator.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%start_timecreator_silent.vbs'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = 'TimeCreator - Minimal Time Tracking Overlay'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo ✓ TimeCreator has been added to Windows startup!
    echo   It will start automatically when you log in.
    echo.
    echo To remove from startup, delete:
    echo   %STARTUP_FOLDER%\TimeCreator.lnk
) else (
    echo ✗ Failed to create startup shortcut.
    echo   You may need to run as administrator.
)

echo.
echo Press any key to exit...
pause > nul