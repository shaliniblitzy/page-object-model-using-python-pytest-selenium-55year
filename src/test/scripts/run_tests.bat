@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..
set TEST_ARGS=
set BROWSER=chrome
set HEADLESS=false
set BASE_URL=https://editor-staging.storydoc.com

if "%1"=="--help" (
    call :print_help
    exit /b 0
)

call :parse_args %*
call :setup_environment
call :run_tests
exit /b %errorlevel%

:print_help
    echo.
    echo Storydoc Test Automation Runner
    echo -------------------------------
    echo This script runs automated tests for the Storydoc application.
    echo.
    echo Usage:
    echo   run_tests.bat [options]
    echo.
    echo Options:
    echo   --help                 Show this help message
    echo   --browser BROWSER      Specify browser (chrome, firefox, edge)
    echo   --headless             Run in headless mode
    echo   --marker MARKER        Run only tests with specific pytest marker
    echo   --parallel N           Run tests in parallel with N workers
    echo   --test PATH            Run specific test or test directory
    echo.
    echo Examples:
    echo   run_tests.bat --browser chrome --headless
    echo   run_tests.bat --marker signup
    echo   run_tests.bat --parallel 4
    echo   run_tests.bat --test tests/test_signup.py
    echo.
    exit /b 0

:parse_args
    :arg_loop
    if "%1"=="" goto :arg_loop_end
    
    if "%1"=="--browser" (
        set BROWSER=%2
        shift
        goto :next_arg
    )
    
    if "%1"=="--headless" (
        set HEADLESS=true
        goto :next_arg
    )
    
    if "%1"=="--marker" (
        set MARKER=%2
        set TEST_ARGS=%TEST_ARGS% -m %MARKER%
        shift
        goto :next_arg
    )
    
    if "%1"=="--parallel" (
        set PARALLEL=%2
        set TEST_ARGS=%TEST_ARGS% -n %PARALLEL%
        shift
        goto :next_arg
    )
    
    if "%1"=="--test" (
        set TEST_PATH=%2
        set TEST_ARGS=%TEST_ARGS% %TEST_PATH%
        shift
        goto :next_arg
    )
    
    :next_arg
    shift
    goto :arg_loop
    
    :arg_loop_end
    exit /b 0

:setup_environment
    cd %PROJECT_ROOT%
    
    if exist %PROJECT_ROOT%\venv\Scripts\activate.bat call %PROJECT_ROOT%\venv\Scripts\activate.bat
    
    set TEST_BROWSER=%BROWSER%
    set TEST_HEADLESS=%HEADLESS%
    set TEST_BASE_URL=%BASE_URL%
    
    if not exist %PROJECT_ROOT%\src\test\reports\html mkdir %PROJECT_ROOT%\src\test\reports\html
    if not exist %PROJECT_ROOT%\src\test\reports\screenshots mkdir %PROJECT_ROOT%\src\test\reports\screenshots
    
    exit /b 0

:run_tests
    if "%HEADLESS%"=="true" (
        set TEST_ARGS=%TEST_ARGS% --headless
    )
    
    python -m pytest %TEST_ARGS% --html=%PROJECT_ROOT%\src\test\reports\html\report.html --self-contained-html
    
    exit /b %errorlevel%