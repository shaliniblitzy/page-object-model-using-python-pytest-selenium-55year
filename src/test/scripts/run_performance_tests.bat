@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..
set PYTHON_EXE=python
set RUN_PAGE_LOAD_TESTS=true
set RUN_RESPONSE_TIME_TESTS=true
set RUN_SLA_COMPLIANCE_TESTS=true
set HEADLESS=true
set VERBOSE=false
set PERFORMANCE_REPORT_DIR=%PROJECT_ROOT%\src\test\reports\performance
set TEST_ARGS=

if "%1"=="--help" (
    call :print_help
    exit /b 0
)
if "%1"=="-h" (
    call :print_help
    exit /b 0
)

:parse_args
if "%~1"=="" goto :after_parse_args
if "%~1"=="-p" (
    set RUN_PAGE_LOAD_TESTS=%~2
    shift
)
if "%~1"=="--page-load" (
    set RUN_PAGE_LOAD_TESTS=%~2
    shift
)
if "%~1"=="-r" (
    set RUN_RESPONSE_TIME_TESTS=%~2
    shift
)
if "%~1"=="--response-time" (
    set RUN_RESPONSE_TIME_TESTS=%~2
    shift
)
if "%~1"=="-s" (
    set RUN_SLA_COMPLIANCE_TESTS=%~2
    shift
)
if "%~1"=="--sla" (
    set RUN_SLA_COMPLIANCE_TESTS=%~2
    shift
)
if "%~1"=="--headless" (
    set HEADLESS=%~2
    shift
)
if "%~1"=="-v" (
    set VERBOSE=true
)
if "%~1"=="--verbose" (
    set VERBOSE=true
)
if "%~1"=="--all" (
    set RUN_PAGE_LOAD_TESTS=true
    set RUN_RESPONSE_TIME_TESTS=true
    set RUN_SLA_COMPLIANCE_TESTS=true
)
if "%~1"=="--report-name" (
    set REPORT_NAME=%~2
    shift
)
shift
goto :parse_args
:after_parse_args

cd %PROJECT_ROOT%

if exist %PROJECT_ROOT%\venv\Scripts\activate.bat call %PROJECT_ROOT%\venv\Scripts\activate.bat

if not exist %PERFORMANCE_REPORT_DIR% mkdir %PERFORMANCE_REPORT_DIR%

set TEST_ARGS=-v

if "%RUN_PAGE_LOAD_TESTS%"=="true" set TEST_ARGS=%TEST_ARGS% src/test/tests/performance/test_page_load_time.py
if "%RUN_RESPONSE_TIME_TESTS%"=="true" set TEST_ARGS=%TEST_ARGS% src/test/tests/performance/test_response_time.py
if "%RUN_SLA_COMPLIANCE_TESTS%"=="true" set TEST_ARGS=%TEST_ARGS% src/test/tests/performance/test_sla_compliance.py

if "%HEADLESS%"=="true" set TEST_ARGS=%TEST_ARGS% --headless

if "%VERBOSE%"=="true" set TEST_ARGS=%TEST_ARGS% -v

set TEST_ARGS=%TEST_ARGS% --html=%PERFORMANCE_REPORT_DIR%/report.html --self-contained-html

%PYTHON_EXE% -m pytest %TEST_ARGS%
exit /b %errorlevel%

:print_help
echo.
echo run_performance_tests.bat - Execute performance tests for Storydoc application
echo.
echo Usage: run_performance_tests.bat [options]
echo.
echo Options:
echo   -h, --help                 Display this help message
echo   -p, --page-load VALUE      Enable/disable page load tests (true/false)
echo   -r, --response-time VALUE  Enable/disable response time tests (true/false)
echo   -s, --sla VALUE            Enable/disable SLA compliance tests (true/false)
echo   --headless VALUE           Run tests in headless mode (true/false)
echo   -v, --verbose              Enable verbose output
echo   --all                      Run all test types
echo   --report-name NAME         Specify custom report name
echo.
echo Examples:
echo   run_performance_tests.bat --all
echo   run_performance_tests.bat -p true -r false -s true --headless true
echo   run_performance_tests.bat --page-load true --verbose
echo.
exit /b 0