#!/bin/bash
# cleanup.sh
# Shell script that cleans up test artifacts and temporary files generated 
# during test execution for the Storydoc automation framework

# Set up error handling
set -e
trap 'echo "Error on line $LINENO"; exit 1' ERR

# Function to output timestamped log messages
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Get script directory and set project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
TEST_DIR="$PROJECT_ROOT/src/test"
REPORTS_DIR="$PROJECT_ROOT/reports"
SCREENSHOTS_DIR="$REPORTS_DIR/screenshots"
LOGS_DIR="$PROJECT_ROOT/logs"
HTML_REPORTS_DIR="$REPORTS_DIR/html"
PERFORMANCE_REPORTS_DIR="$REPORTS_DIR/performance"

# Load environment variables from .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    log_message "Loading environment variables from .env file"
    # Using grep and sed to extract variable values
    DAYS_TO_KEEP_REPORTS=$(grep -E "^DAYS_TO_KEEP_REPORTS=" "$PROJECT_ROOT/.env" | sed 's/^DAYS_TO_KEEP_REPORTS=//')
    DAYS_TO_KEEP_SCREENSHOTS=$(grep -E "^DAYS_TO_KEEP_SCREENSHOTS=" "$PROJECT_ROOT/.env" | sed 's/^DAYS_TO_KEEP_SCREENSHOTS=//')
    DAYS_TO_KEEP_LOGS=$(grep -E "^DAYS_TO_KEEP_LOGS=" "$PROJECT_ROOT/.env" | sed 's/^DAYS_TO_KEEP_LOGS=//')
fi

# Set default values if not defined in .env file
DAYS_TO_KEEP_REPORTS=${DAYS_TO_KEEP_REPORTS:-30}
DAYS_TO_KEEP_SCREENSHOTS=${DAYS_TO_KEEP_SCREENSHOTS:-14}
DAYS_TO_KEEP_LOGS=${DAYS_TO_KEEP_LOGS:-7}

log_message "Starting cleanup process"
log_message "Project root: $PROJECT_ROOT"
log_message "Retention periods: Reports=$DAYS_TO_KEEP_REPORTS days, Screenshots=$DAYS_TO_KEEP_SCREENSHOTS days, Logs=$DAYS_TO_KEEP_LOGS days"

# Determine OS type for OS-specific operations
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
fi
log_message "Detected OS: $OS_TYPE"

# Check if Python virtual environment exists and activate it
VENV_ACTIVATED=false
if [ -d "$PROJECT_ROOT/venv" ]; then
    log_message "Activating Python virtual environment"
    if [ "$OS_TYPE" == "windows" ]; then
        source "$PROJECT_ROOT/venv/Scripts/activate"
    else
        source "$PROJECT_ROOT/venv/bin/activate"
    fi
    VENV_ACTIVATED=true
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    log_message "Activating Python virtual environment (.venv)"
    if [ "$OS_TYPE" == "windows" ]; then
        source "$PROJECT_ROOT/.venv/Scripts/activate"
    else
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    VENV_ACTIVATED=true
fi

# Check if any test processes are currently running
check_running_tests() {
    local test_processes
    
    log_message "Checking for running test processes"
    
    # Check for pytest, chromedriver, geckodriver processes
    if [ "$OS_TYPE" == "windows" ]; then
        # For Windows (using tasklist)
        test_processes=$(tasklist | findstr -i "pytest python chromedriver geckodriver" | wc -l)
    else
        # For Linux and macOS
        test_processes=$(ps aux | grep -E 'pytest|chromedriver|geckodriver' | grep -v grep | wc -l)
    fi
    
    if [ "$test_processes" -gt 0 ]; then
        log_message "WARNING: There appear to be test processes running"
        if [ "$OS_TYPE" == "windows" ]; then
            tasklist | findstr -i "pytest python chromedriver geckodriver"
        else
            ps aux | grep -E 'pytest|chromedriver|geckodriver' | grep -v grep
        fi
        
        read -p "Continue with cleanup anyway? (y/n): " response
        if [[ "$response" != "y" && "$response" != "Y" ]]; then
            log_message "Cleanup aborted by user"
            exit 0
        fi
    fi
}

# Clean up old HTML reports
clean_old_reports() {
    if [ -d "$HTML_REPORTS_DIR" ]; then
        log_message "Cleaning up HTML reports older than $DAYS_TO_KEEP_REPORTS days"
        if [ "$OS_TYPE" == "windows" ]; then
            # For Windows, use PowerShell
            powershell "Get-ChildItem -Path '$HTML_REPORTS_DIR' -Filter '*.html' | Where-Object { \$_.LastWriteTime -lt (Get-Date).AddDays(-$DAYS_TO_KEEP_REPORTS) } | Remove-Item -Force"
        else
            # For Linux and macOS
            find "$HTML_REPORTS_DIR" -type f -name "*.html" -mtime +$DAYS_TO_KEEP_REPORTS -delete
        fi
    else
        log_message "HTML reports directory does not exist: $HTML_REPORTS_DIR"
    fi
}

# Clean up old screenshots
clean_old_screenshots() {
    if [ -d "$SCREENSHOTS_DIR" ]; then
        log_message "Cleaning up screenshots older than $DAYS_TO_KEEP_SCREENSHOTS days"
        if [ "$OS_TYPE" == "windows" ]; then
            # For Windows, use PowerShell
            powershell "Get-ChildItem -Path '$SCREENSHOTS_DIR' -Filter '*.png' | Where-Object { \$_.LastWriteTime -lt (Get-Date).AddDays(-$DAYS_TO_KEEP_SCREENSHOTS) } | Remove-Item -Force"
        else
            # For Linux and macOS
            find "$SCREENSHOTS_DIR" -type f -name "*.png" -mtime +$DAYS_TO_KEEP_SCREENSHOTS -delete
        fi
    else
        log_message "Screenshots directory does not exist: $SCREENSHOTS_DIR"
    fi
}

# Clean up old log files
clean_old_logs() {
    if [ -d "$LOGS_DIR" ]; then
        log_message "Cleaning up log files older than $DAYS_TO_KEEP_LOGS days"
        if [ "$OS_TYPE" == "windows" ]; then
            # For Windows, use PowerShell
            powershell "Get-ChildItem -Path '$LOGS_DIR' -Filter '*.log' | Where-Object { \$_.LastWriteTime -lt (Get-Date).AddDays(-$DAYS_TO_KEEP_LOGS) } | Remove-Item -Force"
        else
            # For Linux and macOS
            find "$LOGS_DIR" -type f -name "*.log" -mtime +$DAYS_TO_KEEP_LOGS -delete
        fi
    else
        log_message "Logs directory does not exist: $LOGS_DIR"
    fi
}

# Clean up old performance reports
clean_performance_reports() {
    if [ -d "$PERFORMANCE_REPORTS_DIR" ]; then
        log_message "Cleaning up performance reports older than $DAYS_TO_KEEP_REPORTS days"
        if [ "$OS_TYPE" == "windows" ]; then
            # For Windows, use PowerShell
            powershell "Get-ChildItem -Path '$PERFORMANCE_REPORTS_DIR' | Where-Object { \$_.LastWriteTime -lt (Get-Date).AddDays(-$DAYS_TO_KEEP_REPORTS) } | Remove-Item -Force"
        else
            # For Linux and macOS
            find "$PERFORMANCE_REPORTS_DIR" -type f -mtime +$DAYS_TO_KEEP_REPORTS -delete
        fi
    else
        log_message "Performance reports directory does not exist: $PERFORMANCE_REPORTS_DIR"
    fi
}

# Clean up Python cache files and directories
clean_python_cache() {
    log_message "Cleaning up Python cache files and directories"
    
    if [ "$OS_TYPE" == "windows" ]; then
        # For Windows, use PowerShell
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -Directory -Filter '.pytest_cache' | Remove-Item -Recurse -Force"
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -File -Filter '*.pyc' | Remove-Item -Force"
    else
        # For Linux and macOS
        find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} +
        find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} +
        find "$PROJECT_ROOT" -type f -name "*.pyc" -delete
    fi
}

# Clean browser data using Python helper if available
clean_browser_data() {
    log_message "Attempting to clean browser data"
    
    HELPER_SCRIPT="$SCRIPT_DIR/cleanup_helper.py"
    if [ -f "$HELPER_SCRIPT" ]; then
        log_message "Executing browser data cleanup via Python helper"
        python "$HELPER_SCRIPT" --clean-browser-data
    else
        log_message "Browser data cleanup helper not found: $HELPER_SCRIPT"
    fi
}

# Clean up temporary files
clean_temp_files() {
    log_message "Cleaning up temporary files"
    
    if [ "$OS_TYPE" == "windows" ]; then
        # For Windows, use PowerShell
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -File -Filter '*.tmp' | Remove-Item -Force"
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -File -Filter '*.bak' | Remove-Item -Force"
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -File -Filter 'geckodriver.log' | Remove-Item -Force"
        powershell "Get-ChildItem -Path '$PROJECT_ROOT' -Recurse -File -Filter 'chromedriver.log' | Remove-Item -Force"
    else
        # For Linux and macOS
        find "$PROJECT_ROOT" -type f -name "*.tmp" -delete
        find "$PROJECT_ROOT" -type f -name "*.bak" -delete
        find "$PROJECT_ROOT" -type f -name "geckodriver.log" -delete
        find "$PROJECT_ROOT" -type f -name "chromedriver.log" -delete
        
        # Clean .DS_Store files on macOS
        if [ "$OS_TYPE" == "macos" ]; then
            find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete
        fi
    fi
}

# Clean WebDriver binaries
clean_webdriver_binaries() {
    log_message "Cleaning cached WebDriver binaries"
    
    # Find WebDriver cache directory based on OS
    if [ "$OS_TYPE" == "macos" ]; then
        WEBDRIVER_CACHE="$HOME/.wdm"
    elif [ "$OS_TYPE" == "linux" ]; then
        WEBDRIVER_CACHE="$HOME/.wdm"
    elif [ "$OS_TYPE" == "windows" ]; then
        WEBDRIVER_CACHE="$HOME/.wdm"
    else
        log_message "Unknown OS type: $OS_TYPE. Skipping WebDriver binary cleanup."
        return
    fi
    
    if [ -d "$WEBDRIVER_CACHE" ]; then
        log_message "Found WebDriver cache directory: $WEBDRIVER_CACHE"
        if [ "$OS_TYPE" == "windows" ]; then
            # For Windows, use PowerShell
            powershell "Get-ChildItem -Path '$WEBDRIVER_CACHE' -Recurse -File | Where-Object { \$_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force"
        else
            # For Linux and macOS
            find "$WEBDRIVER_CACHE" -type f -mtime +30 -delete
        fi
    else
        log_message "WebDriver cache directory not found: $WEBDRIVER_CACHE"
    fi
}

# Run additional cleanup operations using Python helper
run_python_cleanup() {
    log_message "Running comprehensive Python cleanup"
    
    HELPER_SCRIPT="$SCRIPT_DIR/cleanup_helper.py"
    if [ -f "$HELPER_SCRIPT" ]; then
        log_message "Executing comprehensive cleanup via Python helper"
        python "$HELPER_SCRIPT" --comprehensive-cleanup
    else
        log_message "Python cleanup helper not found: $HELPER_SCRIPT"
    fi
}

# Create required directories if they don't exist
mkdir -p "$REPORTS_DIR" "$SCREENSHOTS_DIR" "$LOGS_DIR" "$HTML_REPORTS_DIR" "$PERFORMANCE_REPORTS_DIR"

# Run all cleanup functions
check_running_tests
clean_old_reports
clean_old_screenshots
clean_old_logs
clean_performance_reports
clean_python_cache
clean_browser_data
clean_temp_files
clean_webdriver_binaries
run_python_cleanup

# Deactivate virtual environment if it was activated
if [ "$VENV_ACTIVATED" = true ]; then
    log_message "Deactivating Python virtual environment"
    deactivate
fi

log_message "Cleanup completed successfully"
exit 0