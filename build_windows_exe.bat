@echo off
REM Build script for IHACPA Python Package Review Automation Windows Executable
REM This creates a standalone .exe file with all dependencies bundled

echo ========================================
echo IHACPA Automation Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from python.org
    pause
    exit /b 1
)

echo [1/6] Installing build dependencies...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/6] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist src\__pycache__ rmdir /s /q src\__pycache__

echo.
echo [3/6] Running PyInstaller...
pyinstaller ihacpa_automation.spec --clean
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [4/6] Checking output...
REM Handle timestamped builds by renaming if needed
for %%f in (dist\IHACPA_Automation_*.exe) do (
    if exist "%%f" (
        echo Found timestamped executable: %%f
        move "%%f" "dist\IHACPA_Automation.exe"
    )
)

if not exist dist\IHACPA_Automation.exe (
    echo ERROR: Executable was not created
    dir dist\
    pause
    exit /b 1
)

echo.
echo [5/6] Creating distribution folder...
if not exist dist\IHACPA_Package mkdir dist\IHACPA_Package

REM Copy executable
copy dist\IHACPA_Automation.exe dist\IHACPA_Package\

REM Create README for distribution
echo Creating distribution README...
(
echo IHACPA Python Package Review Automation v1.5.0
echo ============================================
echo.
echo This is a standalone Windows executable that automates the cybersecurity 
echo vulnerability review process for Python packages.
echo.
echo FEATURES:
echo - Processes Excel files with 486 Python packages
echo - Checks PyPI for latest versions and updates
echo - Scans 5 vulnerability databases: NIST NVD, MITRE CVE, SNYK, Exploit DB, GitHub
echo - Optional AI-powered analysis with Azure OpenAI
echo - Automatic formatting and color-coding
echo - No installation required - everything is bundled in the .exe
echo.
echo HOW TO USE:
echo 1. Double-click IHACPA_Automation.exe to start
echo 2. Select your input Excel file
echo 3. Choose where to save the output
echo 4. [Optional] Enter Azure OpenAI credentials for AI analysis
echo 5. Click "Start Processing"
echo.
echo SYSTEM REQUIREMENTS:
echo - Windows 7 or later (64-bit recommended)
echo - At least 4GB RAM
echo - Internet connection for API access
echo.
echo SUPPORT:
echo For issues or questions, contact your IT support team.
echo.
echo Version: 1.5.0
echo Build Date: %date%
) > dist\IHACPA_Package\README.txt

REM Copy sample settings if exists
if exist 05-Configuration-Templates\settings-template.yaml (
    copy 05-Configuration-Templates\settings-template.yaml dist\IHACPA_Package\settings-template.yaml
)

echo.
echo [6/6] Build complete!
echo.
echo ========================================
echo BUILD SUCCESSFUL
echo ========================================
echo.
echo Executable location: dist\IHACPA_Automation.exe
echo Package location: dist\IHACPA_Package\
echo.
echo File size: 
dir dist\IHACPA_Automation.exe | find "IHACPA"
echo.
echo The executable can now be distributed and run on any Windows machine
echo without Python or any dependencies installed.
echo.
pause