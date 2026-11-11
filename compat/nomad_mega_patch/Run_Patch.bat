@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\NomadPatch.ps1"
pause
