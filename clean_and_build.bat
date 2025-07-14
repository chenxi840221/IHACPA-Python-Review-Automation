@echo off
echo Cleaning up before build...

REM Kill any running IHACPA_Automation processes
taskkill /F /IM IHACPA_Automation.exe /T 2>nul
timeout /t 2 >nul

REM Remove existing executable if it exists
if exist "dist\IHACPA_Automation.exe" (
    echo Removing existing executable...
    del /F "dist\IHACPA_Automation.exe" 2>nul
    if exist "dist\IHACPA_Automation.exe" (
        echo Warning: Could not remove existing executable. Please close it manually.
        pause
    )
)

REM Clean build directories
if exist "build" rmdir /S /Q "build" 2>nul
if exist "dist" rmdir /S /Q "dist" 2>nul

echo Starting PyInstaller build...
call build_env\Scripts\activate.bat
pyinstaller ihacpa_automation.spec

if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo Executable location: dist\IHACPA_Automation.exe
) else (
    echo Build failed with error code %ERRORLEVEL%
)

pause