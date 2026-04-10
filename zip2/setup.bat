@echo off
REM TIS Hardware Gap Analysis - Windows Batch Setup
REM Double-click this file OR run from Command Prompt

echo.
echo ========================================
echo   TIS Hardware Gap Analysis - Setup
echo ========================================
echo.

REM ── Check zip exists ─────────────────────────────────────────────────────────
if not exist "tis_gap_app.zip" (
    echo ERROR: tis_gap_app.zip not found in this folder.
    echo Make sure setup.bat is in the same folder as tis_gap_app.zip
    pause
    exit /b 1
)
echo [1/4] Found tis_gap_app.zip
echo.

REM ── Extract zip using PowerShell ─────────────────────────────────────────────
echo [2/4] Extracting tis_gap_app.zip...
if exist "tis_gap_app\" (
    echo       Folder already exists - skipping extraction.
) else (
    powershell -Command "Expand-Archive -Path 'tis_gap_app.zip' -DestinationPath '.' -Force"
    if errorlevel 1 (
        echo ERROR: Extraction failed. Make sure PowerShell is available.
        pause
        exit /b 1
    )
    echo       Extracted successfully.
)
echo.

REM ── Install dependencies ──────────────────────────────────────────────────────
echo [3/4] Installing Python dependencies...
if not exist "tis_gap_app\requirements.txt" (
    echo ERROR: requirements.txt not found inside tis_gap_app folder.
    pause
    exit /b 1
)

pip install -r tis_gap_app\requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)
echo       Dependencies installed.
echo.

REM ── Create run.bat ────────────────────────────────────────────────────────────
echo [4/4] Creating run.bat launcher...

(
echo @echo off
echo cd /d "%%~dp0"
echo echo.
echo echo ========================================
echo echo   TIS Hardware Gap Analysis
echo echo ========================================
echo echo.
echo echo Open browser at: http://localhost:5000
echo echo Press Ctrl+C to stop.
echo echo.
echo set /p OPENAI_API_KEY=Paste OpenAI key ^(or press Enter to use app UI^): 
echo python app.py
echo pause
) > "tis_gap_app\run.bat"

echo       Created tis_gap_app\run.bat
echo.

echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo To start the app:
echo   1. Open the tis_gap_app folder
echo   2. Double-click run.bat
echo      OR open http://localhost:5000
echo.

set /p LAUNCH=Launch the app now? (y/n): 
if /i "%LAUNCH%"=="y" (
    cd tis_gap_app
    call run.bat
)
