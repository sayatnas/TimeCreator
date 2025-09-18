@echo off
REM TimeCreator silent startup script
REM Starts the minimal overlay interface without showing terminal

cd /d "%~dp0"

REM Use pythonw.exe instead of python.exe to run without console window
pythonw launch.py overlay