@echo off
setlocal enabledelayedexpansion

rem --------------------------------------------------------
rem Storydoc Automation Framework - Cleanup Script
rem --------------------------------------------------------
rem This script cleans up test artifacts and temporary files
rem generated during test execution for the Storydoc automation framework.
rem --------------------------------------------------------

rem Set directory paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\.."
set "TEST_DIR=%PROJECT_ROOT%\src\test"
set "REPORTS_DIR=%PROJECT_ROOT%\reports"
set "SCREENSHOTS_DIR=%REPORTS_DIR%\screenshots"
set "LOGS_DIR=%PROJECT_ROOT%\logs"
set "HTML_REPORTS_DIR=%REPORTS_DIR%\html"
set "PERFORMANCE_REPORTS_DIR=%REPORTS_DIR%\performance"

rem Default retention periods (in days)
set "DAYS_TO_KEEP_REPORTS=7"
set "DAYS_TO_KEEP_SCREENSHOTS=3"
set "DAYS_TO_KEEP_LOGS=5"

rem Set SKIP_CONFIRM to false by default
set "SKIP_CONFIRM=false"

rem Check for help parameter
if "%1"=="--help" (
    call :print_help
    exit /b 0
)

rem Load environment variables from .env if it exists
if exist "%PROJECT_ROOT%\.env" (
    for /f "tokens=*" %%a in (%PROJECT_ROOT%\.env) do set %%a
)

rem Parse command line arguments
if "%1"=="--force" (
    set SKIP_CONFIRM=true
)

rem Change to project root directory
cd "%PROJECT_ROOT%"

rem Activate virtual environment if it exists
if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" call "%PROJECT_ROOT%\venv\Scripts\activate.bat"

rem Check if tests are running
call :check_running_tests

rem Create directories if they don't exist
if not exist "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"
if not exist "%SCREENSHOTS_DIR%" mkdir "%SCREENSHOTS_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%HTML_REPORTS_DIR%" mkdir "%HTML_REPORTS_DIR%"
if not exist "%PERFORMANCE_REPORTS_DIR%" mkdir "%PERFORMANCE_REPORTS_DIR%"

rem Perform cleanup operations
call :log_message "Starting cleanup operations..."

call :clean_old_reports
call :clean_old_screenshots
call :clean_old_logs
call :clean_performance_reports
call :clean_python_cache
call :clean_temp_files
call :clean_webdriver_binaries
call :run_python_cleanup

call :log_message "Cleanup completed successfully."

rem Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV call deactivate

exit /b 0

rem --------------------------------------------------------
rem Function Definitions
rem --------------------------------------------------------

:print_help
echo.
echo Storydoc Automation Framework - Cleanup Script
echo --------------------------------------------------------
echo This script cleans up test artifacts and temporary files
echo generated during test execution for the Storydoc automation framework.
echo.
echo Usage:
echo   cleanup.bat [options]
echo.
echo Options:
echo   --help    Display this help message
echo   --force   Skip confirmation prompts and force cleanup
echo.
echo Examples:
echo   cleanup.bat            Run normal cleanup with confirmations
echo   cleanup.bat --force    Run cleanup without confirmations
echo.
exit /b 0

:log_message
echo [%date% %time%] %~1
exit /b 0

:check_running_tests
call :log_message "Checking for running tests..."

rem Check for running test processes
tasklist /fi "imagename eq python.exe" | find /i "python.exe" > nul
if %errorlevel% equ 0 (
    tasklist /fi "imagename eq python.exe" /v | find /i "pytest" > nul
    if %errorlevel% equ 0 (
        call :log_message "WARNING: Test processes appear to be running!"
        
        if "%SKIP_CONFIRM%"=="true" (
            call :log_message "Continuing anyway due to --force option."
            exit /b 0
        )
        
        set /p CONTINUE="Continuing with cleanup may interrupt tests. Continue anyway? (y/n): "
        if /i "!CONTINUE!" neq "y" (
            call :log_message "Cleanup aborted by user."
            exit /b 1
        )
    )
)

rem Check for browser drivers
tasklist /fi "imagename eq chromedriver.exe" | find /i "chromedriver.exe" > nul
if %errorlevel% equ 0 (
    call :log_message "WARNING: ChromeDriver processes are running!"
    
    if "%SKIP_CONFIRM%"=="true" (
        call :log_message "Continuing anyway due to --force option."
        exit /b 0
    )
    
    set /p CONTINUE="Continuing with cleanup may interrupt tests. Continue anyway? (y/n): "
    if /i "!CONTINUE!" neq "y" (
        call :log_message "Cleanup aborted by user."
        exit /b 1
    )
)

tasklist /fi "imagename eq geckodriver.exe" | find /i "geckodriver.exe" > nul
if %errorlevel% equ 0 (
    call :log_message "WARNING: GeckoDriver processes are running!"
    
    if "%SKIP_CONFIRM%"=="true" (
        call :log_message "Continuing anyway due to --force option."
        exit /b 0
    )
    
    set /p CONTINUE="Continuing with cleanup may interrupt tests. Continue anyway? (y/n): "
    if /i "!CONTINUE!" neq "y" (
        call :log_message "Cleanup aborted by user."
        exit /b 1
    )
)

call :log_message "No test processes detected or user confirmed continuation."
exit /b 0

:clean_old_reports
call :log_message "Cleaning HTML reports older than %DAYS_TO_KEEP_REPORTS% days..."
if exist "%HTML_REPORTS_DIR%" (
    forfiles /p "%HTML_REPORTS_DIR%" /s /m "*.html" /d -%DAYS_TO_KEEP_REPORTS% /c "cmd /c del @path" 2>nul
    if %errorlevel% equ 0 (
        call :log_message "Old HTML reports removed successfully."
    ) else (
        call :log_message "No HTML reports found to remove or command failed."
    )
) else (
    call :log_message "HTML reports directory does not exist."
)
exit /b 0

:clean_old_screenshots
call :log_message "Cleaning screenshots older than %DAYS_TO_KEEP_SCREENSHOTS% days..."
if exist "%SCREENSHOTS_DIR%" (
    forfiles /p "%SCREENSHOTS_DIR%" /s /m "*.png" /d -%DAYS_TO_KEEP_SCREENSHOTS% /c "cmd /c del @path" 2>nul
    if %errorlevel% equ 0 (
        call :log_message "Old screenshots removed successfully."
    ) else (
        call :log_message "No screenshots found to remove or command failed."
    )
) else (
    call :log_message "Screenshots directory does not exist."
)
exit /b 0

:clean_old_logs
call :log_message "Cleaning log files older than %DAYS_TO_KEEP_LOGS% days..."
if exist "%LOGS_DIR%" (
    forfiles /p "%LOGS_DIR%" /s /m "*.log" /d -%DAYS_TO_KEEP_LOGS% /c "cmd /c del @path" 2>nul
    if %errorlevel% equ 0 (
        call :log_message "Old log files removed successfully."
    ) else (
        call :log_message "No log files found to remove or command failed."
    )
) else (
    call :log_message "Logs directory does not exist."
)
exit /b 0

:clean_performance_reports
call :log_message "Cleaning performance reports older than %DAYS_TO_KEEP_REPORTS% days..."
if exist "%PERFORMANCE_REPORTS_DIR%" (
    forfiles /p "%PERFORMANCE_REPORTS_DIR%" /s /m "*.json" /d -%DAYS_TO_KEEP_REPORTS% /c "cmd /c del @path" 2>nul
    forfiles /p "%PERFORMANCE_REPORTS_DIR%" /s /m "*.html" /d -%DAYS_TO_KEEP_REPORTS% /c "cmd /c del @path" 2>nul
    forfiles /p "%PERFORMANCE_REPORTS_DIR%" /s /m "*.csv" /d -%DAYS_TO_KEEP_REPORTS% /c "cmd /c del @path" 2>nul
    call :log_message "Old performance reports processed."
) else (
    call :log_message "Performance reports directory does not exist."
)
exit /b 0

:clean_python_cache
call :log_message "Cleaning Python cache files..."
if exist "%TEST_DIR%" (
    rem Remove __pycache__ directories
    for /d /r "%TEST_DIR%" %%d in (__pycache__) do (
        if exist "%%d" (
            rmdir /s /q "%%d"
            call :log_message "Removed: %%d"
        )
    )
    
    rem Remove .pyc files
    del /s /q "%TEST_DIR%\*.pyc" 2>nul
    
    rem Remove .pytest_cache directories
    for /d /r "%TEST_DIR%" %%d in (.pytest_cache) do (
        if exist "%%d" (
            rmdir /s /q "%%d"
            call :log_message "Removed: %%d"
        )
    )
    
    call :log_message "Python cache files cleaned."
) else (
    call :log_message "Test directory does not exist."
)
exit /b 0

:clean_temp_files
call :log_message "Cleaning temporary files..."
if exist "%TEST_DIR%" (
    rem Remove .tmp files
    del /s /q "%TEST_DIR%\*.tmp" 2>nul
    
    rem Remove .bak files
    del /s /q "%TEST_DIR%\*.bak" 2>nul
    
    rem Remove WebDriver log files
    del /s /q "%TEST_DIR%\geckodriver.log" 2>nul
    del /s /q "%TEST_DIR%\chromedriver.log" 2>nul
    
    call :log_message "Temporary files cleaned."
) else (
    call :log_message "Test directory does not exist."
)
exit /b 0

:clean_webdriver_binaries
call :log_message "Cleaning WebDriver binaries older than 30 days..."
rem Find WebDriver cache directory in user profile
set "WEBDRIVER_CACHE=%USERPROFILE%\.wdm"
if exist "%WEBDRIVER_CACHE%" (
    forfiles /p "%WEBDRIVER_CACHE%" /s /d -30 /c "cmd /c if @isdir==TRUE rmdir /s /q @path" 2>nul
    call :log_message "WebDriver binaries cleaned."
) else (
    call :log_message "WebDriver cache not found."
)
exit /b 0

:run_python_cleanup
call :log_message "Running additional Python cleanup operations..."
if exist "%PROJECT_ROOT%\src\test\utilities\cleanup_helper.py" (
    python -c "from src.test.utilities.cleanup_helper import CleanupHelper; CleanupHelper.cleanup_after_test()"
    if %errorlevel% equ 0 (
        call :log_message "Python cleanup completed successfully."
    ) else (
        call :log_message "Python cleanup failed with error code: %errorlevel%"
    )
) else (
    call :log_message "Python cleanup helper not found. Skipping."
)
exit /b 0