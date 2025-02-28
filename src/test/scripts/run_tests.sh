#!/bin/bash
# run_tests.sh
# Script for executing Storydoc automation tests using pytest

# Exit immediately if a command exits with a non-zero status
set -e

# Import required scripts
source ./setup_environment.sh

# Global variables
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(dirname "$(dirname "$SCRIPT_DIR")")
TEST_DIR=$PROJECT_ROOT/src/test
REPORTS_DIR=$TEST_DIR/reports
HTML_REPORT_PATH=$REPORTS_DIR/html/report.html
SCREENSHOTS_DIR=$REPORTS_DIR/screenshots
LOGS_DIR=$REPORTS_DIR/logs

# Default settings
DEFAULT_BROWSER="chrome"
DEFAULT_ENV="staging"
DEFAULT_PARALLEL="0"
DEFAULT_HEADLESS="false"
DEFAULT_VERBOSITY="2"
DEFAULT_REPORT="true"
DEFAULT_XML_REPORT="false"

# Test categories
TEST_CATEGORIES="user_registration user_authentication story_creation story_sharing end_to_end"

# Function to display a formatted header for the script
print_header() {
    echo "============================================================"
    echo "        Storydoc Automation Tests Runner"
    echo "============================================================"
    echo "This script runs automated tests for the Storydoc application"
    echo "with configurable options for browser, environment, and more."
    echo "============================================================"
}

# Function to display usage instructions
print_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -b, --browser BROWSER     Browser to use (chrome, firefox, edge) [default: $DEFAULT_BROWSER]"
    echo "  -e, --env ENV             Environment to test against (staging, etc.) [default: $DEFAULT_ENV]"
    echo "  -p, --parallel N          Run tests in parallel with N processes [default: $DEFAULT_PARALLEL]"
    echo "  -m, --markers MARKERS     Specify pytest markers to run"
    echo "  -c, --category CATEGORY   Test category to run ($(echo $TEST_CATEGORIES | sed 's/ /, /g'), all) [default: all]"
    echo "  -t, --test-path PATH      Specific test path or file to run"
    echo "  -l, --headless            Run in headless mode [default: $DEFAULT_HEADLESS]"
    echo "  -v, --verbose LEVEL       Set verbosity level (0-3) [default: $DEFAULT_VERBOSITY]"
    echo "  -r, --report BOOL         Generate HTML report [default: $DEFAULT_REPORT]"
    echo "  -x, --xml BOOL            Generate JUnit XML report [default: $DEFAULT_XML_REPORT]"
    echo "  -s, --screenshots BOOL    Enable screenshots on failure [default: true]"
    echo ""
    echo "Examples:"
    echo "  $0 -b chrome -e staging -c user_registration  # Run registration tests with Chrome on staging"
    echo "  $0 -p 4 -l -c all                             # Run all tests in parallel with 4 processes in headless mode"
    echo "  $0 -t src/test/tests/test_story_creation.py   # Run a specific test file"
    echo ""
}

# Function to set up the test environment
setup_environment() {
    local env_name=$1
    
    # Call the setup_environment_variables function from setup_environment.sh
    setup_environment_variables "$env_name"
    
    # Create necessary directories using function from setup_environment.sh
    create_directories
    
    # Set Python path
    export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH
    
    return 0
}

# Function to resolve test path based on category or specific path
resolve_test_path() {
    local category=$1
    local test_path=$2
    
    # If a specific test path is provided, use it
    if [ -n "$test_path" ]; then
        echo "$test_path"
        return
    fi
    
    # If category is "all", run all tests
    if [ "$category" = "all" ]; then
        echo "$TEST_DIR/tests"
        return
    fi
    
    # Map category to specific test path
    case "$category" in
        user_registration)
            echo "$TEST_DIR/tests/test_user_registration.py"
            ;;
        user_authentication)
            echo "$TEST_DIR/tests/test_user_authentication.py"
            ;;
        story_creation)
            echo "$TEST_DIR/tests/test_story_creation.py"
            ;;
        story_sharing)
            echo "$TEST_DIR/tests/test_story_sharing.py"
            ;;
        end_to_end)
            echo "$TEST_DIR/tests/test_end_to_end.py"
            ;;
        *)
            # Default to all tests if category is not recognized
            echo "$TEST_DIR/tests"
            ;;
    esac
}

# Function to run the tests
run_tests() {
    # Construct the pytest command
    local cmd="python -m pytest"
    
    # Add the test path
    local test_path=$(resolve_test_path "$TEST_CATEGORY" "$TEST_PATH")
    cmd="$cmd $test_path"
    
    # Add HTML report option if enabled
    if [ "$REPORT" = "true" ]; then
        cmd="$cmd --html=$HTML_REPORT_PATH --self-contained-html"
    fi
    
    # Add JUnit XML report option if enabled
    if [ "$XML_REPORT" = "true" ]; then
        cmd="$cmd --junitxml=$REPORTS_DIR/junit.xml"
    fi
    
    # Add verbosity option
    cmd="$cmd -v" # Always include at least one level of verbosity
    
    # Add additional verbosity levels
    if [ "$VERBOSITY" -gt 1 ]; then
        for ((i=1; i<VERBOSITY; i++)); do
            cmd="$cmd -v"
        done
    fi
    
    # Add parallel execution option if enabled
    if [ "$PARALLEL" -gt 0 ]; then
        cmd="$cmd -n $PARALLEL"
    fi
    
    # Add markers if specified
    if [ -n "$MARKERS" ]; then
        cmd="$cmd -m \"$MARKERS\""
    fi
    
    # Pass environment variables for configuration
    export TEST_BROWSER="$BROWSER"
    export TEST_ENVIRONMENT="$ENVIRONMENT"
    export TEST_HEADLESS="$HEADLESS"
    export TEST_SCREENSHOTS="$SCREENSHOTS"
    
    # Print the command if verbose mode is enabled
    if [ "$VERBOSITY" -gt 1 ]; then
        echo "Executing: $cmd"
    fi
    
    # Execute the command
    eval "$cmd"
    return $?
}

# Function to parse command-line arguments
parse_arguments() {
    # Initialize variables with default values
    BROWSER=$DEFAULT_BROWSER
    ENVIRONMENT=$DEFAULT_ENV
    PARALLEL=$DEFAULT_PARALLEL
    MARKERS=""
    TEST_CATEGORY="all"
    TEST_PATH=""
    HEADLESS=$DEFAULT_HEADLESS
    VERBOSITY=$DEFAULT_VERBOSITY
    REPORT=$DEFAULT_REPORT
    XML_REPORT=$DEFAULT_XML_REPORT
    SCREENSHOTS="true"
    
    # Process command-line options
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                print_usage
                exit 0
                ;;
            -b|--browser)
                BROWSER="$2"
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -p|--parallel)
                PARALLEL="$2"
                shift 2
                ;;
            -m|--markers)
                MARKERS="$2"
                shift 2
                ;;
            -c|--category)
                TEST_CATEGORY="$2"
                shift 2
                ;;
            -t|--test-path)
                TEST_PATH="$2"
                shift 2
                ;;
            -l|--headless)
                HEADLESS="true"
                shift
                ;;
            -v|--verbose)
                VERBOSITY="$2"
                shift 2
                ;;
            -r|--report)
                REPORT="$2"
                shift 2
                ;;
            -x|--xml)
                XML_REPORT="$2"
                shift 2
                ;;
            -s|--screenshots)
                SCREENSHOTS="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Validate arguments
    # Check browser
    case "$BROWSER" in
        chrome|firefox|edge)
            # Valid browser
            ;;
        *)
            echo "Error: Invalid browser specified: $BROWSER. Valid options are: chrome, firefox, edge."
            exit 1
            ;;
    esac
    
    # Check environment
    case "$ENVIRONMENT" in
        staging|development|production|test)
            # Valid environment
            ;;
        *)
            echo "Warning: Non-standard environment specified: $ENVIRONMENT."
            ;;
    esac
    
    # Check parallel value is a number
    if ! [[ "$PARALLEL" =~ ^[0-9]+$ ]]; then
        echo "Error: Parallel option must be a number: $PARALLEL"
        exit 1
    fi
    
    # Check verbosity level is a number between 0 and 3
    if ! [[ "$VERBOSITY" =~ ^[0-3]$ ]]; then
        echo "Error: Verbosity level must be between 0 and 3: $VERBOSITY"
        exit 1
    fi
    
    # Check boolean values
    for param in HEADLESS REPORT XML_REPORT SCREENSHOTS; do
        value="${!param}"
        if [ "$value" != "true" ] && [ "$value" != "false" ]; then
            echo "Error: $param must be 'true' or 'false': $value"
            exit 1
        fi
    done
    
    # Print configuration if verbose mode is enabled
    if [ "$VERBOSITY" -gt 1 ]; then
        echo "Configuration:"
        echo "  Browser: $BROWSER"
        echo "  Environment: $ENVIRONMENT"
        echo "  Parallel: $PARALLEL"
        echo "  Markers: $MARKERS"
        echo "  Test Category: $TEST_CATEGORY"
        echo "  Test Path: $TEST_PATH"
        echo "  Headless: $HEADLESS"
        echo "  Verbosity: $VERBOSITY"
        echo "  HTML Report: $REPORT"
        echo "  XML Report: $XML_REPORT"
        echo "  Screenshots: $SCREENSHOTS"
    fi
}

# Function to validate the environment
validate_environment() {
    # Check Python version
    python_version=$(python --version 2>&1 | cut -d " " -f 2)
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 9 ]); then
        echo "Error: Python 3.9+ is required. Found version $python_version"
        return 1
    fi
    
    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        echo "Error: pytest is not installed"
        return 1
    fi
    
    # Check if selenium is installed
    if ! python -c "import selenium" &> /dev/null; then
        echo "Error: selenium is not installed"
        return 1
    fi
    
    # Check if webdriver-manager is installed
    if ! python -c "import webdriver_manager" &> /dev/null; then
        echo "Error: webdriver_manager is not installed"
        return 1
    fi
    
    # Check directories
    for dir in "$TEST_DIR" "$REPORTS_DIR" "$SCREENSHOTS_DIR" "$LOGS_DIR"; do
        if [ ! -d "$dir" ]; then
            echo "Warning: Directory not found: $dir"
        fi
    done
    
    return 0
}

# Function to print summary
print_summary() {
    local exit_code=$1
    
    echo "============================================================"
    if [ $exit_code -eq 0 ]; then
        echo "Test execution completed successfully."
    else
        echo "Test execution completed with failures. Exit code: $exit_code"
    fi
    
    # Show report paths
    if [ "$REPORT" = "true" ]; then
        echo "HTML Report: $HTML_REPORT_PATH"
    fi
    
    if [ "$XML_REPORT" = "true" ]; then
        echo "JUnit XML Report: $REPORTS_DIR/junit.xml"
    fi
    
    echo "Screenshots: $SCREENSHOTS_DIR"
    echo "Logs: $LOGS_DIR"
    echo "============================================================"
}

# Main script execution
parse_arguments "$@"
print_header

# Validate environment
if ! validate_environment; then
    echo "Environment validation failed. Please fix the issues and try again."
    exit 1
fi

# Set up environment
if ! setup_environment "$ENVIRONMENT"; then
    echo "Environment setup failed. Please check the logs for details."
    exit 1
fi

# Run tests
run_tests
exit_code=$?

# Print summary
print_summary $exit_code

# Exit with the same code as pytest
exit $exit_code