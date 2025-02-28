@echo off
REM =====================================================================
REM Storydoc Automation Framework - Environment Setup Script
REM =====================================================================
REM This script automates the setup process for the Storydoc test 
REM automation framework environment. It creates a virtual environment,
REM installs dependencies, configures environment variables, sets up
REM WebDriver, and creates necessary directories for test execution.
REM
REM Version: 1.0
REM =====================================================================

echo.
echo =====================================================================
echo Storydoc Automation Framework - Environment Setup
echo =====================================================================
echo.

REM Set script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."
cd %PROJECT_ROOT%

echo [INFO] Working directory: %PROJECT_ROOT%

REM Step 1: Call the dependency installation script
echo [INFO] Installing dependencies...
call "%SCRIPT_DIR%install_dependencies.bat"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

REM Step 2: Create necessary directories
echo [INFO] Creating necessary directories...

REM Create reports directory structure
if not exist "reports" (
    mkdir "reports"
    echo [INFO] Created reports directory.
)
if not exist "reports\screenshots" (
    mkdir "reports\screenshots"
    echo [INFO] Created screenshots directory.
)
if not exist "reports\html" (
    mkdir "reports\html"
    echo [INFO] Created HTML reports directory.
)
if not exist "reports\logs" (
    mkdir "reports\logs"
    echo [INFO] Created logs directory.
)

REM Step 3: Verify environment setup is complete
echo [INFO] Verifying environment setup...
call .venv\Scripts\activate
python -c "import pytest, selenium, requests, dotenv, webdriver_manager; print('All core dependencies are installed correctly.')"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Verification test failed. Some dependencies may not be installed correctly.
) else (
    echo [INFO] Core dependencies verified successfully.
)

REM Step 4: Verify WebDriver setup
echo [INFO] Setting up WebDriver binaries...
python -c "from webdriver_manager.chrome import ChromeDriverManager; print(f'Chrome WebDriver path: {ChromeDriverManager().install()}')"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to setup Chrome WebDriver. You may need to download and configure it manually.
) else (
    echo [INFO] Chrome WebDriver setup successful.
)

python -c "from webdriver_manager.firefox import GeckoDriverManager; print(f'Firefox WebDriver path: {GeckoDriverManager().install()}')"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to setup Firefox WebDriver. You may need to download and configure it manually.
) else (
    echo [INFO] Firefox WebDriver setup successful.
)

REM Deactivate virtual environment
call deactivate

REM Notify completion
echo.
echo =====================================================================
echo Environment Setup Complete!
echo =====================================================================
echo.
echo The Storydoc Automation Framework environment has been set up successfully.
echo.
echo To run tests:
echo 1. Ensure your virtual environment is activated:
echo    call .venv\Scripts\activate
echo 2. Run tests using pytest:
echo    pytest test\tests
echo.
echo To deactivate the virtual environment when finished:
echo    deactivate
echo.

pause
exit /b 0