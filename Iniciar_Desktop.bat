@echo off
title JARVIS v3.1 — Native Desktop Assistant (PyQt6)
color 0A

cd /d "%~dp0"

echo =====================================================
echo    JARVIS v3.1 - Native Desktop Assistant (PyQt6)
echo    Bandeja del Sistema + Barra Flotante (Alt + Espacio)
echo =====================================================
echo.

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado en: %~dp0venv
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    echo [ERROR] No se encontro el archivo .env en: %~dp0
    pause
    exit /b 1
)

echo [INFO] Iniciando JARVIS Nativo (PyQt6)...
"%~dp0venv\Scripts\python.exe" desktop_app.py

pause
