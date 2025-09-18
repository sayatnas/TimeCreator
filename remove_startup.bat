@echo off
REM Remove TimeCreator from Windows startup

echo Removing TimeCreator from Windows startup...

REM Get the startup folder path
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Check if shortcut exists
if exist "%STARTUP_FOLDER%\TimeCreator.lnk" (
    del "%STARTUP_FOLDER%\TimeCreator.lnk"
    if %errorlevel% equ 0 (
        echo ✓ TimeCreator has been removed from Windows startup.
    ) else (
        echo ✗ Failed to remove startup shortcut.
    )
) else (
    echo TimeCreator is not currently set to start with Windows.
)

echo.
echo Press any key to exit...
pause > nul