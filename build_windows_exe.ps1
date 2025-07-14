# PowerShell build script for IHACPA Python Package Review Automation
# Creates a standalone Windows executable with all dependencies

Write-Host "========================================"
Write-Host "IHACPA Automation Build Script" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or later from python.org"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
Write-Host "[1/7] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "build_env")) {
    python -m venv build_env
    Write-Host "Created new virtual environment" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "build_env\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "[2/7] Installing build dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "[3/7] Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "build", "dist", "__pycache__", "src\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

# Run PyInstaller
Write-Host ""
Write-Host "[4/7] Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller ihacpa_automation.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if executable was created
Write-Host ""
Write-Host "[5/7] Verifying build output..." -ForegroundColor Yellow
if (-not (Test-Path "dist\IHACPA_Automation.exe")) {
    Write-Host "ERROR: Executable was not created" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$exeInfo = Get-Item "dist\IHACPA_Automation.exe"
$sizeMB = [math]::Round($exeInfo.Length / 1MB, 2)
Write-Host "Executable created successfully!" -ForegroundColor Green
Write-Host "Size: $sizeMB MB"

# Create distribution package
Write-Host ""
Write-Host "[6/7] Creating distribution package..." -ForegroundColor Yellow
$packageDir = "dist\IHACPA_Package"
New-Item -Path $packageDir -ItemType Directory -Force | Out-Null

# Copy executable
Copy-Item "dist\IHACPA_Automation.exe" $packageDir

# Create README
$readmeContent = @"
IHACPA Python Package Review Automation v1.5.0
============================================

This is a standalone Windows executable that automates the cybersecurity 
vulnerability review process for Python packages.

FEATURES:
- Processes Excel files with 486 Python packages
- Checks PyPI for latest versions and updates
- Scans 5 vulnerability databases: NIST NVD, MITRE CVE, SNYK, Exploit DB, GitHub
- Optional AI-powered analysis with Azure OpenAI
- Automatic formatting and color-coding
- User-friendly GUI interface
- No installation required - everything is bundled in the .exe

HOW TO USE:
1. Double-click IHACPA_Automation.exe to start
2. Select your input Excel file (Browse button)
3. Choose where to save the output file
4. [Optional] Enter Azure OpenAI credentials for AI analysis:
   - API Key: Your Azure OpenAI key
   - Endpoint: https://your-resource-name.openai.azure.com/
   - Model: Your deployment name (e.g., gpt-4)
5. Click "Start Processing"
6. Monitor progress in the log window

SYSTEM REQUIREMENTS:
- Windows 7 or later (64-bit recommended)
- At least 4GB RAM
- Internet connection for API access
- Excel file with the standard IHACPA format (23 columns)

AZURE OPENAI SETUP (Optional):
To enable AI-powered vulnerability analysis:
1. Get an Azure OpenAI resource from Azure Portal
2. Deploy a GPT-4 model
3. Copy your API key and endpoint
4. Enter these in the application

TROUBLESHOOTING:
- If the application doesn't start: Install Visual C++ Redistributable
- If API calls fail: Check your internet connection
- If Excel errors occur: Ensure the file isn't open in Excel
- For AI errors: Verify your Azure OpenAI credentials

SUPPORT:
For issues or questions, contact your IT support team.

Version: 1.5.0
Build Date: $(Get-Date -Format "yyyy-MM-dd")
"@

$readmeContent | Out-File -FilePath "$packageDir\README.txt" -Encoding UTF8

# Copy sample settings if exists
if (Test-Path "05-Configuration-Templates\settings-template.yaml") {
    Copy-Item "05-Configuration-Templates\settings-template.yaml" "$packageDir\settings-template.yaml"
}

# Create a sample batch file to run the app
$batchContent = @"
@echo off
echo Starting IHACPA Python Package Review Automation...
start IHACPA_Automation.exe
"@
$batchContent | Out-File -FilePath "$packageDir\Run_IHACPA_Automation.bat" -Encoding ASCII

# Create ZIP archive
Write-Host ""
Write-Host "[7/7] Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "dist\IHACPA_Automation_v1.5.0_Windows.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $packageDir -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host ""
Write-Host "========================================"
Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Executable location: dist\IHACPA_Automation.exe ($sizeMB MB)" -ForegroundColor Cyan
Write-Host "Package location: $packageDir\" -ForegroundColor Cyan
Write-Host "ZIP archive: $zipPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "The executable can now be distributed and run on any Windows machine"
Write-Host "without Python or any dependencies installed."
Write-Host ""
Write-Host "Distribution options:"
Write-Host "1. Share the ZIP file for easy distribution"
Write-Host "2. Copy the IHACPA_Package folder to a USB drive"
Write-Host "3. Upload to a shared network location"
Write-Host ""

# Deactivate virtual environment
deactivate

Read-Host "Press Enter to exit"