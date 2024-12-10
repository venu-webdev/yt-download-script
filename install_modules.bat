@echo off
:: Ensure Python is installed and available in PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not added to PATH. Please install Python and try again.
    pause
    exit /b
)

:: Install required Python modules
echo Installing required Python modules...
pip install yt-dlp pillow requests

:: Confirm completion
echo All modules have been installed successfully!
pause
