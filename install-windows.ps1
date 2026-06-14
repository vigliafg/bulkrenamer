# =============================================================================
# Bulk File Renamer PRO — Windows Installer & Launcher (PowerShell)
# =============================================================================
# Usage:
#   1. Clone the repository:  git clone <repo-url>; cd bulkrenamer
#   2. Open PowerShell as the current user (NOT as Administrator):
#      Press Win+R, type "powershell", press Enter
#   3. If needed, allow script execution (one time only):
#      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   4. Run this script:       .\install-windows.ps1
#   5. Launch from anywhere:  bulk-renamer
#
# The script:
#   • Checks for Python 3.10+
#   • Creates a virtual environment inside %LOCALAPPDATA%\bulk-renamer\
#   • Installs PyQt6 and project dependencies
#   • Creates a global launcher cmd file in %LOCALAPPDATA%\Microsoft\WindowsApps\
#     (which is already in the system PATH on Windows 10/11)
# =============================================================================

$ErrorActionPreference = "Stop"

# ── Helper functions ──────────────────────────────────────────────────────────

function Write-Info  { Write-Host "[INFO]  $args" -ForegroundColor Blue }
function Write-Ok    { Write-Host "[OK]    $args" -ForegroundColor Green }
function Write-Warn  { Write-Host "[WARN]  $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# ── Paths ─────────────────────────────────────────────────────────────────────

$InstallDir = "$env:LOCALAPPDATA\bulk-renamer"
$BinDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
$Launcher = "$BinDir\bulk-renamer.cmd"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗"
Write-Host "║   Bulk File Renamer PRO — Windows Installer       ║"
Write-Host "╚═══════════════════════════════════════════════════╝"
Write-Host ""

# ── 1. Check prerequisites ────────────────────────────────────────────────────

Write-Info "Checking prerequisites..."

try {
    $pyVersion = python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "python not found"
    }
} catch {
    Write-Error "Python not found."
    Write-Host "       Download Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "       IMPORTANT: check 'Add Python to PATH' during installation."
    exit 1
}

# Parse version numbers
$parts = $pyVersion -split '\s+'
$major = [int]$parts[0]
$minor = [int]$parts[1]
$fullVersion = "Python $major.$minor"

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
    Write-Error "Python 3.10+ is required. Found: $fullVersion"
    exit 1
}
Write-Ok "$fullVersion detected."

# Check pip
try {
    $null = python -m pip --version 2>&1
} catch {
    Write-Error "pip not available. Please reinstall Python with pip included."
    exit 1
}

# ── 2. Install project files ──────────────────────────────────────────────────

Write-Info "Installing to $InstallDir ..."
if (Test-Path $InstallDir) {
    Write-Warn "Removing previous installation at $InstallDir ..."
    Remove-Item -Recurse -Force $InstallDir
}
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Copy project files
$excludeDirs = @('.git', '.venv', '__pycache__', 'dist', 'build')
$excludeFiles = @('install-linux.sh', 'install-macos.sh')

Get-ChildItem -Path $ProjectDir -Exclude $excludeDirs | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $InstallDir -Recurse -Force
}

# Remove excluded files from the copy
foreach ($f in $excludeFiles) {
    $fp = Join-Path $InstallDir $f
    if (Test-Path $fp) { Remove-Item -Force $fp }
}

# ── 3. Create and populate virtual environment ────────────────────────────────

Write-Info "Creating virtual environment..."
python -m venv "$InstallDir\.venv"

$venvPython = "$InstallDir\.venv\Scripts\python.exe"
$venvPip = "$InstallDir\.venv\Scripts\pip.exe"

Write-Info "Installing dependencies..."
& $venvPython -m pip install --upgrade pip -q
& $venvPython -m pip install -r "$InstallDir\requirements.txt" -q

Write-Ok "Dependencies installed."

# ── 4. Create global launcher ─────────────────────────────────────────────────

Write-Info "Creating global launcher at $Launcher ..."

# Ensure WindowsApps directory exists
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
}

# Create the launcher .cmd file
@"
@echo off
REM Bulk File Renamer PRO — Global Launcher
set "INSTALL_DIR=%LOCALAPPDATA%\bulk-renamer"
"%INSTALL_DIR%\.venv\Scripts\python.exe" "%INSTALL_DIR%\main.py" %*
"@ | Out-File -FilePath $Launcher -Encoding ASCII

Write-Ok "Launcher created."

# ── 5. Verify WindowsApps is in PATH ─────────────────────────────────────────

$inPath = ($env:PATH -split ';') | Where-Object { $_ -eq $BinDir }
if (-not $inPath) {
    Write-Warn "$BinDir is not in your PATH."
    Write-Warn "Adding it to the user PATH..."

    $currentUserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentUserPath -notlike "*$BinDir*") {
        [Environment]::SetEnvironmentVariable(
            "PATH",
            "$BinDir;$currentUserPath",
            "User"
        )
        # Also update current session
        $env:PATH = "$BinDir;$env:PATH"
        Write-Ok "Added to user PATH. The change takes effect in new terminal windows."
    }
}

# ── 6. Done ────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗"
Write-Host "║   ✅ Installation complete!                       ║"
Write-Host "║                                                   ║"
Write-Host "║   Launch from anywhere with:                      ║"
Write-Host "║       bulk-renamer                                ║"
Write-Host "║                                                   ║"
Write-Host "║   Install dir: $InstallDir"
Write-Host "║   Launcher:    $Launcher"
Write-Host "║                                                   ║"
Write-Host "║   NOTE: Restart your terminal or open a new one   ║"
Write-Host "║         for the PATH change to take effect.       ║"
Write-Host "╚═══════════════════════════════════════════════════╝"
Write-Host ""
