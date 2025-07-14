# PowerShell script to clean and build IHACPA Automation

Write-Host "Cleaning up before build..." -ForegroundColor Yellow

# Kill any running IHACPA_Automation processes
$processes = Get-Process -Name "IHACPA_Automation" -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "Terminating running IHACPA_Automation processes..." -ForegroundColor Red
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Remove existing executable if it exists
$exePath = "dist\IHACPA_Automation.exe"
if (Test-Path $exePath) {
    Write-Host "Removing existing executable..." -ForegroundColor Yellow
    try {
        Remove-Item $exePath -Force
        Write-Host "Existing executable removed." -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Could not remove existing executable. Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please close the application manually and run this script again." -ForegroundColor Yellow
        Read-Host "Press Enter to continue anyway or Ctrl+C to abort"
    }
}

# Clean build directories
Write-Host "Cleaning build directories..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue }

# Activate virtual environment and build
Write-Host "Starting PyInstaller build..." -ForegroundColor Green
try {
    & "build_env\Scripts\Activate.ps1"
    & pyinstaller ihacpa_automation.spec
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build completed successfully!" -ForegroundColor Green
        
        # Find the timestamped executable and rename it
        $timestampedExe = Get-ChildItem "dist\IHACPA_Automation_*.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($timestampedExe) {
            $finalExePath = "dist\IHACPA_Automation.exe"
            Write-Host "Renaming $($timestampedExe.Name) to IHACPA_Automation.exe..." -ForegroundColor Yellow
            Move-Item $timestampedExe.FullName $finalExePath -Force
            
            if (Test-Path $finalExePath) {
                $fileSize = (Get-Item $finalExePath).Length / 1MB
                Write-Host "Executable location: $finalExePath" -ForegroundColor Green
                Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
            }
        } else {
            Write-Host "Warning: Could not find timestamped executable in dist folder" -ForegroundColor Yellow
            Get-ChildItem "dist\" | ForEach-Object { Write-Host "Found: $($_.Name)" }
        }
    } else {
        Write-Host "Build failed with error code $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error during build: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "Press Enter to continue"