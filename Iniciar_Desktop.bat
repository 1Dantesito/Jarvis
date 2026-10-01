@echo off
chcp 65001 >nul
title JARVIS v3.1 — Native Desktop Assistant (PyQt6)
color 0B

cd /d "%~dp0"

echo ----------------------------------------------------
echo    ⚡ JARVIS v3.1 — Native Desktop Assistant (PyQt6)
echo    Bandeja del Sistema + Barra Flotante (Alt + Espacio)
echo ----------------------------------------------------
echo.

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado en: %~dp0venv
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    echo [ERROR] Archivo de configuracion .env no encontrado en: %~dp0
    pause
    exit /b 1
)

echo [INFO] Iniciando JARVIS Nativo (PyQt6)...
"%~dp0venv\Scripts\python.exe" desktop_app.py

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] La aplicacion se cerro con codigo de salida %errorlevel%.
    pause
)
