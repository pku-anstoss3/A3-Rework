@echo off
rem ANSTOSS 3 - Inoffizieller Patch 1.47: startet das Installationsprogramm
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Anstoss3-Patch-1.47.ps1" %*
if errorlevel 1 pause
