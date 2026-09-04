@echo off
REM ============================================================
REM MarketVoice SEA — Launch n8n Locally (Windows Batch Launcher)
REM ============================================================

title MarketVoice SEA - n8n Workflow Orchestrator
cd /d "%~dp0\.."

echo ============================================================
echo   MarketVoice SEA - n8n Local Workflow Orchestrator
echo ============================================================
echo.

REM Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not found in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js is available.
echo [OK] Using dedicated workspace: %CD%
echo.

REM Launch via PowerShell runner with environment loaded
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\start_n8n.ps1"

pause
