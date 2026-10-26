@echo off
setlocal
cd /d "%~dp0"
title Code-Pro Bot Launcher [Guardian Mode]

echo ============================================================
echo            CODE-PRO BOT LAUNCHER [GUARDIAN MODE]
echo ============================================================

:: 1. OPTION C: Check for Administrator Privileges (High Integrity Level)
net session >nul 2>&1
if %errorlevel% equ 0 goto :CHECK_PYTHON

:: Check if already attempted elevation to prevent infinite loop
if "%~1"=="--no-elevate" goto :RUN_STANDARD
echo [Guardian] Attempting elevation to Administrator [High Integrity Level]...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c cd /d \"%~dp0\" && \"%~nx0\" --no-elevate' -Verb RunAs" 2>nul
if %errorlevel% equ 0 exit /b

:RUN_STANDARD
echo [Notice] Running in standard user mode...

:CHECK_PYTHON
:: 2. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 goto :PYTHON_NOT_FOUND
goto :CHECK_VENV

:PYTHON_NOT_FOUND
echo [ERROR] Python is not installed or not added to PATH!
echo Please download and install Python 3.10+ from https://www.python.org/
echo Make sure to check [Add Python to PATH] during installation.
echo.
pause
exit /b 1

:CHECK_VENV
:: 3. Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" goto :CREATE_VENV
goto :WATCHDOG_LOOP

:CREATE_VENV
echo [Setup] First-time setup detected.
echo [Setup] Creating virtual environment [.venv]...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)
echo [Setup] Virtual environment created successfully.
echo.
echo [Setup] Installing required packages from requirements.txt...
echo [Setup] Please wait while packages download...
echo.
.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo.
echo [Setup] All dependencies installed successfully!
echo ============================================================
echo.

:WATCHDOG_LOOP
:: 4. OPTION B: Watchdog / Auto-Respawn Loop
echo.
echo [Guardian] Code-Bot is active.
echo [Guardian] Auto-Respawn Watchdog is ACTIVE.
echo [Guardian] To exit completely, choose [0] Exit in the bot menu.
echo.

.venv\Scripts\python.exe bot.py
set EXIT_CODE=%ERRORLEVEL%

:: If user selected [0] Exit normally from the menu
if %EXIT_CODE% equ 0 goto :CLEAN_EXIT

:: If process was forcefully terminated, killed, or crashed
echo.
echo ============================================================
echo [ALERT] Bot process was terminated! Exit Code: %EXIT_CODE%
echo [Guardian] Shielding and respawning Code-Bot in 1 second...
echo ============================================================
timeout /t 1 /nobreak >nul
goto :WATCHDOG_LOOP

:CLEAN_EXIT
echo.
echo [Guardian] Bot stopped normally by user. Goodbye!
pause
