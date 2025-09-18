@echo off
REM TimeCreator launcher batch file
REM Usage: timecreator.bat [command] [arguments]
REM Default: Start minimal overlay

cd /d "%~dp0"
python launch.py %*