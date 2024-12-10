@echo off
:: Get the directory of the current script
set "script_dir=%~dp0"

:: Navigate to the script directory
cd /d "%script_dir%"

:: Run the Python script without opening a terminal
start pythonw yt_downloader_v2.py
