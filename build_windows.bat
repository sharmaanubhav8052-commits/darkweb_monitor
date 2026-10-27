@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo DarkWeb Threat Monitoring - Windows Build
echo ==========================================
echo.
echo IMPORTANT: Put this file in the project root,
echo alongside app.py, desktop_app.py, templates and static.
echo.

if not exist "app.py" (
  echo ERROR: app.py not found in this folder.
  pause
  exit /b 1
)
if not exist "templates\index.html" (
  echo ERROR: templates\index.html not found.
  pause
  exit /b 1
)
if not exist "templates\analyzer.html" (
  echo ERROR: templates\analyzer.html not found.
  pause
  exit /b 1
)
if not exist "templates\reports.html" (
  echo ERROR: templates\reports.html not found.
  pause
  exit /b 1
)
if not exist "static" (
  echo ERROR: static folder not found.
  pause
  exit /b 1
)

echo [1/4] Creating build environment if needed...
if not exist ".desktop_venv\Scripts\python.exe" (
  py -3 -m venv .desktop_venv
  if errorlevel 1 goto failed
)

echo [2/4] Installing packaging dependencies...
".desktop_venv\Scripts\python.exe" -m pip install --upgrade pip
".desktop_venv\Scripts\python.exe" -m pip install -r requirements-desktop.txt
if errorlevel 1 goto failed

echo [3/4] Building Windows desktop application...
".desktop_venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name DarkWebThreatMonitor --add-data "templates;templates" --add-data "static;static" --collect-all webview --collect-all clr_loader --collect-all pythonnet desktop_app.py
if errorlevel 1 goto failed

echo [4/4] Creating portable ZIP...
echo portable > "dist\DarkWebThreatMonitor\portable.mode"
if not exist "dist\DarkWebThreatMonitor\data" mkdir "dist\DarkWebThreatMonitor\data"
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path 'DarkWebThreatMonitor_Portable.zip') { Remove-Item 'DarkWebThreatMonitor_Portable.zip' -Force }; Compress-Archive -Path 'dist\DarkWebThreatMonitor\*' -DestinationPath 'DarkWebThreatMonitor_Portable.zip' -Force"
if errorlevel 1 goto failed

del /q "dist\DarkWebThreatMonitor\portable.mode"

echo.
echo BUILD COMPLETE.
echo Portable ZIP: %CD%\DarkWebThreatMonitor_Portable.zip
echo Installer preparation folder: %CD%\dist\DarkWebThreatMonitor
echo.
echo Next: Install Inno Setup and open DarkWebThreatMonitor.iss to compile the installer.
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Read the error shown above and send a screenshot.
pause
exit /b 1
