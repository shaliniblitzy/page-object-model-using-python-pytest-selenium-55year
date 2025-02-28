@echo off
REM ===================================================================
REM Storydoc Automation Framework - Dependency Installation Script
REM ===================================================================
REM This script installs all required dependencies for the Storydoc
REM automation framework, including Python packages and WebDriver binaries.
REM It also sets up a virtual environment for isolated execution.
REM
REM Version: 1.0
REM ===================================================================

echo.
echo ===================================================================
echo Storydoc Automation Framework - Installing Dependencies
echo ===================================================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo and make sure it's added to your PATH environment variable.
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%V"
echo [INFO] Detected Python version: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
set "VENV_DIR=.venv"
if not exist %VENV_DIR%\ (
    echo [INFO] Creating virtual environment in %VENV_DIR%...
    python -m pip install --upgrade virtualenv
    python -m virtualenv %VENV_DIR%
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
) else (
    echo [INFO] Using existing virtual environment in %VENV_DIR%.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call %VENV_DIR%\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo [INFO] Upgrading pip to latest version...
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to upgrade pip, but continuing with installation.
)

REM Install dependencies from requirements.txt
echo [INFO] Installing Python dependencies from requirements.txt...
pip install -r ..\requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Setup WebDriver binaries
echo [INFO] Setting up WebDriver binaries...
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
python -c "from webdriver_manager.firefox import GeckoDriverManager; GeckoDriverManager().install()"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to setup WebDriver binaries automatically.
    echo You may need to download and configure WebDriver manually.
)

REM Create .env file from .env.example if it doesn't exist
if not exist "..\..\.env" (
    if exist "..\..\.env.example" (
        echo [INFO] Creating .env file from .env.example...
        copy "..\..\.env.example" "..\..\.env"
        echo [INFO] Created .env file. Please update it with your specific configuration.
    ) else (
        echo [WARNING] .env.example file not found. You'll need to create .env file manually.
    )
) else (
    echo [INFO] .env file already exists.
)

REM Notify completion
echo.
echo ===================================================================
echo Installation Complete!
echo ===================================================================
echo.
echo The Storydoc Automation Framework dependencies have been installed successfully.
echo.
echo To run tests:
echo 1. Ensure your virtual environment is activated:
echo    call %VENV_DIR%\Scripts\activate
echo 2. Run tests using pytest:
echo    pytest ..\tests
echo.
echo To deactivate the virtual environment when finished:
echo    deactivate
echo.

pause
exit /b 0