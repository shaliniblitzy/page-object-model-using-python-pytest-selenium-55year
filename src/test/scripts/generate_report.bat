@echo off
setlocal enabledelayedexpansion

:: Set directory paths
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..\
set TEST_DIR=%PROJECT_ROOT%\src\test
set REPORTS_DIR=%TEST_DIR%\reports
set HTML_REPORTS_DIR=%REPORTS_DIR%\html
set SCREENSHOTS_DIR=%REPORTS_DIR%\screenshots
set PERFORMANCE_DIR=%REPORTS_DIR%\performance
set LOG_DIR=%REPORTS_DIR%\logs

:: Generate timestamp for unique report names
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

:: Set default values
set DEFAULT_REPORT_NAME=report_%TIMESTAMP%.html
set DEFAULT_JSON_NAME=report_%TIMESTAMP%.json
set DEFAULT_SUMMARY_NAME=summary_%TIMESTAMP%.txt
set DEFAULT_REPORT_FORMAT=html
set DEFAULT_TEST_RESULTS_PATH=%TEST_DIR%\reports\results.json

:: Initialize variables
set REPORT_NAME=
set REPORT_FORMAT=%DEFAULT_REPORT_FORMAT%
set TEST_RESULTS_PATH=%DEFAULT_TEST_RESULTS_PATH%
set INCLUDE_PERFORMANCE=false
set INCLUDE_LOGS=false

:: Check for help option
if "%1"=="--help" (
    call :print_usage
    exit /b 0
)

if "%1"=="-h" (
    call :print_usage
    exit /b 0
)

:: Parse command line arguments
call :parse_arguments %*

:: Check if test results file exists
if not exist "%TEST_RESULTS_PATH%" (
    echo Error: Test results file not found at %TEST_RESULTS_PATH%
    exit /b 1
)

:: Generate appropriate report based on format
if "%REPORT_FORMAT%"=="html" (
    if "%REPORT_NAME%"=="" set REPORT_NAME=%DEFAULT_REPORT_NAME%
    set REPORT_PATH=%HTML_REPORTS_DIR%\%REPORT_NAME%
    call :generate_html_report "%TEST_RESULTS_PATH%" "%REPORT_PATH%"
)

if "%REPORT_FORMAT%"=="json" (
    if "%REPORT_NAME%"=="" set REPORT_NAME=%DEFAULT_JSON_NAME%
    set REPORT_PATH=%REPORTS_DIR%\%REPORT_NAME%
    call :generate_json_report "%TEST_RESULTS_PATH%" "%REPORT_PATH%"
)

if "%REPORT_FORMAT%"=="summary" (
    if "%REPORT_NAME%"=="" set REPORT_NAME=%DEFAULT_SUMMARY_NAME%
    set REPORT_PATH=%REPORTS_DIR%\%REPORT_NAME%
    call :generate_summary_report "%TEST_RESULTS_PATH%" "%REPORT_PATH%"
)

echo Report generation completed.
exit /b %errorlevel%

:: =====================================================================
:: Functions
:: =====================================================================

:print_usage
    echo Storydoc Automation Framework - Test Report Generator
    echo Generates HTML, JSON, or summary reports from test execution results.
    echo.
    echo Usage: 
    echo   generate_report.bat [options]
    echo.
    echo Options:
    echo   -f, --format FORMAT   Report format (html, json, summary)
    echo   -o, --output NAME     Output file name
    echo   -r, --results PATH    Path to test results JSON file
    echo   -p, --performance     Include performance metrics
    echo   -l, --logs            Include test logs (HTML format only)
    echo   -h, --help            Display this help message
    echo.
    echo Examples:
    echo   generate_report.bat
    echo   generate_report.bat --format html --output my_report.html
    echo   generate_report.bat -f json -o test_report.json -p
    echo   generate_report.bat -f summary -r custom_results.json
    echo.
    echo Report Formats:
    echo   html     - HTML report with test results, screenshots, and statistics
    echo   json     - JSON format report for programmatic processing
    echo   summary  - Simple text summary with key test execution statistics
    echo.
    exit /b 0

:parse_arguments
    :loop
    if "%~1"=="" goto :endloop
    
    if "%~1"=="-f" (
        set REPORT_FORMAT=%~2
        shift
    ) else if "%~1"=="--format" (
        set REPORT_FORMAT=%~2
        shift
    ) else if "%~1"=="-o" (
        set REPORT_NAME=%~2
        shift
    ) else if "%~1"=="--output" (
        set REPORT_NAME=%~2
        shift
    ) else if "%~1"=="-r" (
        set TEST_RESULTS_PATH=%~2
        shift
    ) else if "%~1"=="--results" (
        set TEST_RESULTS_PATH=%~2
        shift
    ) else if "%~1"=="-p" (
        set INCLUDE_PERFORMANCE=true
    ) else if "%~1"=="--performance" (
        set INCLUDE_PERFORMANCE=true
    ) else if "%~1"=="-l" (
        set INCLUDE_LOGS=true
    ) else if "%~1"=="--logs" (
        set INCLUDE_LOGS=true
    )
    
    shift
    goto :loop
    :endloop
    
    exit /b 0

:setup_directories
    if not exist "%HTML_REPORTS_DIR%" (
        mkdir "%HTML_REPORTS_DIR%"
        if errorlevel 1 (
            echo Error: Failed to create HTML reports directory
            exit /b 1
        )
    )
    
    if not exist "%SCREENSHOTS_DIR%" (
        mkdir "%SCREENSHOTS_DIR%"
        if errorlevel 1 (
            echo Error: Failed to create screenshots directory
            exit /b 1
        )
    )
    
    if not exist "%PERFORMANCE_DIR%" (
        mkdir "%PERFORMANCE_DIR%"
        if errorlevel 1 (
            echo Error: Failed to create performance directory
            exit /b 1
        )
    )
    
    if not exist "%LOG_DIR%" (
        mkdir "%LOG_DIR%"
        if errorlevel 1 (
            echo Error: Failed to create logs directory
            exit /b 1
        )
    )
    
    exit /b 0

:generate_html_report
    set test_results_path=%~1
    set report_path=%~2
    
    call :setup_directories
    if errorlevel 1 exit /b 1
    
    echo Generating HTML report from %test_results_path% to %report_path%...
    
    python -c "import sys; sys.path.append('%PROJECT_ROOT%'); from src.test.utilities.reporting_helper import generate_html_report; print(generate_html_report('%test_results_path%', '%report_path%', include_performance=%INCLUDE_PERFORMANCE%, include_logs=%INCLUDE_LOGS%))"
    
    if errorlevel 1 (
        echo Error: Failed to generate HTML report
        exit /b 1
    ) else (
        echo HTML report successfully generated at %report_path%
    )
    
    exit /b 0

:generate_json_report
    set test_results_path=%~1
    set report_path=%~2
    
    echo Generating JSON report from %test_results_path% to %report_path%...
    
    python -c "import sys; sys.path.append('%PROJECT_ROOT%'); from src.test.utilities.reporting_helper import generate_json_report; print(generate_json_report('%test_results_path%', '%report_path%', include_performance=%INCLUDE_PERFORMANCE%))"
    
    if errorlevel 1 (
        echo Error: Failed to generate JSON report
        exit /b 1
    ) else (
        echo JSON report successfully generated at %report_path%
    )
    
    exit /b 0

:generate_summary_report
    set test_results_path=%~1
    set report_path=%~2
    
    echo Generating summary report from %test_results_path% to %report_path%...
    
    python -c "import sys; sys.path.append('%PROJECT_ROOT%'); from src.test.utilities.reporting_helper import generate_test_report_summary; import json; with open('%test_results_path%') as f: print(generate_test_report_summary(json.load(f)))" > "%report_path%"
    
    if errorlevel 1 (
        echo Error: Failed to generate summary report
        exit /b 1
    ) else (
        echo Summary report successfully generated at %report_path%
        echo.
        type "%report_path%"
    )
    
    exit /b 0