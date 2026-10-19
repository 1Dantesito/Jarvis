@echo off
chcp 65001 >nul
title JARVIS v4.0 — Modo Celular e Internet
color 0B

cd /d "%~dp0"

echo ----------------------------------------------------
echo    ⚡ JARVIS v4.0 — MODO CELULAR E INTERNET
echo    [Acceso Remoto Seguro con Codigo QR y HTTPS]
echo ----------------------------------------------------
echo.

:: 1. Verificar entorno virtual local
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [CONFIGURACION INICIAL] Creando entorno virtual local...
    python -m venv "%~dp0venv" 2>nul || py -m venv "%~dp0venv" 2>nul
    if exist "%~dp0venv\Scripts\python.exe" (
        echo [OK] Instalando dependencias de JARVIS...
        "%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
    ) else (
        echo [ERROR] No se encontro Python para iniciar el servidor.
        echo Instala Python 3.10+ marcando "Add python.exe to PATH" desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: 2. Asegurar archivo .env
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env" >nul
    )
)

:: 3. Lanzar el orquestador de modo celular con túnel seguro y QR
"%~dp0venv\Scripts\python.exe" "%~dp0scripts\start_mobile_mode.py"

pause
