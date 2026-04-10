# TIS Hardware Gap Analysis - Windows Setup Script
# Run this in PowerShell from the ZIP folder:
# Right-click this file → "Run with PowerShell"
# OR in PowerShell terminal: .\setup.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TIS Hardware Gap Analysis - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Find the zip ──────────────────────────────────────────────────────
$zipFile = Get-ChildItem -Filter "tis_gap_app.zip" -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $zipFile) {
    Write-Host "ERROR: tis_gap_app.zip not found in current folder." -ForegroundColor Red
    Write-Host "Make sure setup.ps1 is in the same folder as tis_gap_app.zip" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/4] Found: $($zipFile.FullName)" -ForegroundColor Green

# ── Step 2: Extract zip ───────────────────────────────────────────────────────
Write-Host "[2/4] Extracting tis_gap_app.zip..." -ForegroundColor Yellow

$destPath = Join-Path (Get-Location) "tis_gap_app"

if (Test-Path $destPath) {
    Write-Host "      Folder 'tis_gap_app' already exists - skipping extraction." -ForegroundColor DarkYellow
} else {
    try {
        Expand-Archive -Path $zipFile.FullName -DestinationPath (Get-Location) -Force
        Write-Host "      Extracted to: $destPath" -ForegroundColor Green
    } catch {
        Write-Host "ERROR extracting zip: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ── Step 3: Install Python dependencies ──────────────────────────────────────
Write-Host "[3/4] Installing Python dependencies..." -ForegroundColor Yellow

$requirementsPath = Join-Path $destPath "requirements.txt"

if (-not (Test-Path $requirementsPath)) {
    Write-Host "ERROR: requirements.txt not found inside tis_gap_app folder." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    pip install -r $requirementsPath
    Write-Host "      Dependencies installed successfully." -ForegroundColor Green
} catch {
    Write-Host "ERROR installing dependencies: $_" -ForegroundColor Red
    Write-Host "Make sure Python and pip are installed and on your PATH." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# ── Step 4: Create run.ps1 launcher ──────────────────────────────────────────
Write-Host "[4/4] Creating run.ps1 launcher..." -ForegroundColor Yellow

$runScript = Join-Path $destPath "run.ps1"

@'
# TIS Hardware Gap Analysis - Launcher
# Run this script to start the app

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TIS Hardware Gap Analysis - Starting" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ask for API key if not already set
if (-not $env:OPENAI_API_KEY -and -not $env:ANTHROPIC_API_KEY) {
    Write-Host "No API key found in environment." -ForegroundColor Yellow
    Write-Host "You can set it here OR paste it inside the app on Step 1." -ForegroundColor Yellow
    Write-Host ""
    $provider = Read-Host "Which provider? Enter 'openai' or 'anthropic' (or press Enter to skip)"

    if ($provider -eq "openai") {
        $key = Read-Host "Paste your OpenAI API key (sk-...)"
        if ($key) { $env:OPENAI_API_KEY = $key }
    } elseif ($provider -eq "anthropic") {
        $key = Read-Host "Paste your Anthropic API key (sk-ant-...)"
        if ($key) { $env:ANTHROPIC_API_KEY = $key }
    } else {
        Write-Host "Skipped - you can enter the key in the app UI." -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "Starting Flask app..." -ForegroundColor Green
Write-Host "Open your browser at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor DarkYellow
Write-Host ""

# Change to the app directory and run
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
python app.py
'@ | Set-Content -Path $runScript -Encoding UTF8

Write-Host "      Created: $runScript" -ForegroundColor Green

# ── Done ─────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the app, run:" -ForegroundColor White
Write-Host "  cd tis_gap_app" -ForegroundColor Yellow
Write-Host "  .\run.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or double-click 'run.ps1' inside the tis_gap_app folder." -ForegroundColor White
Write-Host ""

$launch = Read-Host "Launch the app now? (y/n)"
if ($launch -eq "y" -or $launch -eq "Y") {
    Set-Location $destPath
    & .\run.ps1
}
