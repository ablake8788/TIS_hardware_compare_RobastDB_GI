# ============================================================
#  TIS Hardware Gap Analysis — Compile to EXE
#  FILE LOCATION: tis_gap_app\compile.ps1
#
#  HOW TO RUN:
#    1. Open PowerShell
#    2. cd to your project:
#       cd "C:\Ara\Python\Titanium Inteligent Soultions\TIS_hardware_compare_RobastDB_GIT\tis_gap_app"
#    3. Run:
#       .\compile.ps1
# ============================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TIS Gap Analysis — Build EXE"             -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Script location : tis_gap_app\compile.ps1"  -ForegroundColor DarkGray
Write-Host "  Working dir     : $(Get-Location)"           -ForegroundColor DarkGray
Write-Host ""

# ── Guard: must be run from inside tis_gap_app\ ──────────────────────────────
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "You must run this script from INSIDE the tis_gap_app folder." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  cd tis_gap_app" -ForegroundColor Yellow
    Write-Host "  .\compile.ps1"  -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "tis_gap_app.spec")) {
    Write-Host "ERROR: tis_gap_app.spec not found." -ForegroundColor Red
    Write-Host "Make sure tis_gap_app.spec is in the same folder as app.py" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# ── Step 1: Install PyInstaller ───────────────────────────────────────────────
Write-Host "[1/4] Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install pyinstaller failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "      OK" -ForegroundColor Green

# ── Step 2: Install all app requirements ─────────────────────────────────────
Write-Host "[2/4] Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install requirements failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "      OK" -ForegroundColor Green

# ── Step 3: Clean previous build ─────────────────────────────────────────────
Write-Host "[3/4] Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "dist")  { Remove-Item -Recurse -Force "dist"  }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Write-Host "      OK" -ForegroundColor Green

# ── Step 4: PyInstaller compile ───────────────────────────────────────────────
Write-Host "[4/4] Compiling EXE (1-3 minutes)..." -ForegroundColor Yellow
Write-Host ""

pyinstaller tis_gap_app.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed. Check output above for details." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ── Done ──────────────────────────────────────────────────────────────────────
$exePath = Join-Path (Get-Location) "dist\TIS_GapAnalysis.exe"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Build complete!"                           -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  EXE location:" -ForegroundColor White
Write-Host "  $exePath"      -ForegroundColor Yellow
Write-Host ""
Write-Host "  Before running the EXE:" -ForegroundColor White
Write-Host "  Copy tis_gap_app.ini into the dist\ folder" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Folder structure should be:"   -ForegroundColor White
Write-Host "    dist\"                        -ForegroundColor DarkYellow
Write-Host "      TIS_GapAnalysis.exe"        -ForegroundColor DarkYellow
Write-Host "      tis_gap_app.ini"            -ForegroundColor DarkYellow
Write-Host "      reports\"                   -ForegroundColor DarkYellow
Write-Host ""

$open = Read-Host "Open dist\ folder now? (y/n)"
if ($open -eq "y" -or $open -eq "Y") {
    explorer "dist"
}
