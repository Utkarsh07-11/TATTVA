@echo off
setlocal
cd /d "%~dp0"

echo Building frontend...
pushd frontend
call npm install
if errorlevel 1 exit /b 1
call npm run build
if errorlevel 1 exit /b 1
popd

echo Building Windows executable...
".venv\Scripts\python.exe" -m pip install pyinstaller
".venv\Scripts\python.exe" -m PyInstaller --noconfirm GeoProductionAI.spec
if errorlevel 1 exit /b 1

echo.
echo Done. Launch: dist\GeoProductionAI\GeoProductionAI.exe
endlocal
