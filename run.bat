@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ========================================
echo SSD Tradeoff Lab - Auto Setup + Run
echo ========================================

REM === SET PROJECT ROOT ===
cd /d "%~dp0"

REM === STEP 1: CREATE VENV IF NOT EXIST ===
if not exist ".venv\Scripts\activate.bat" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment already exists
)

REM === STEP 2: ACTIVATE VENV ===
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM === STEP 3: UPGRADE PIP ===
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

REM === STEP 4: INSTALL REQUIREMENTS ===
if exist requirements.txt (
    echo [4/5] Installing dependencies...
    pip install -r requirements.txt
) else (
    echo [4/5] No requirements.txt found, skipping install
)

REM === OPTIONAL: INSTALL OLLAMA PY CLIENT (SAFE) ===
pip install requests >nul 2>&1

REM === STEP 5: RUN TESTS ===
echo [5/5] Running tests...
python -m unittest

echo ========================================
echo Starting SSD Dashboard...
echo ========================================

REM === RUN SERVER ===
python server.py

echo.
echo Server stopped.
pause

endlocal

