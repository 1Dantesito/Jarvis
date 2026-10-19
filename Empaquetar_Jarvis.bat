@echo off
chcp 65001 >nul
title JARVIS — Empaquetador Portable
color 0A

cd /d "%~dp0"

set "PY_BIN=%~dp0venv\Scripts\python.exe"
if not exist "%PY_BIN%" set "PY_BIN=python"

"%PY_BIN%" "%~dp0scripts\pack_project.py"

echo.
pause
