@echo off
echo ==========================================================
echo Starting SIH 2026 PS 26009 Manganese Decision Support System
echo ==========================================================

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    echo [OK] Using virtual environment python...
    ".venv\Scripts\python.exe" scripts\run_all.py
) ELSE (
    echo [OK] Using system python...
    python scripts\run_all.py
)

pause
