@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
set "SCRIPT=%~dp0Lora_Keyword_finder_renamer.py"

where python >nul 2>&1 || (echo [!] Python not found. && pause && exit /b 1)
if not exist "%SCRIPT%" (echo [!] Missing script: %SCRIPT% && pause && exit /b 1)

if "%~1"=="" (
  set /p "TARGET=Enter full path to your LoRA folder: "
) else (
  set "TARGET=%~1"
)

if not defined TARGET (echo [i] No folder provided. && pause && exit /b 0)
if not exist "%TARGET%" (echo [!] Folder not found: "%TARGET%" && pause && exit /b 1)

echo Selected: "%TARGET%"
choice /C YN /M "Apply renames now? (Y = --apply, N = preview only)"
if errorlevel 2 (set "APPLY=" & echo Preview mode...) else (set "APPLY=--apply" & echo Applying...)

echo.
python "%SCRIPT%" "%TARGET%" %APPLY%
echo.
pause