#!/bin/bash
# run_performance_tests.sh
# Shell script for running performance tests of the Storydoc application to verify SLA compliance

set -e  # Exit on error

# Global variables
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(dirname "$(dirname "$SCRIPT_DIR")")
PERFORMANCE_REPORT_DIR="$PROJECT_ROOT/test/reports/performance"
RUN_PAGE_LOAD_TESTS=true
RUN_RESPONSE_TIME_TESTS=true
RUN_SLA_COMPLIANCE_TESTS=true
HEADLESS=true
VERBOSE=false
PYTEST_ARGS=()

# Display usage information
usage() {
    echo "Usage: $(basename "$0") [OPTIONS]"
    echo
    echo "Run performance tests for the Storydoc application to verify SLA compliance."
    echo
    echo "Options:"
    echo "  -h, --help                 Display this help message"
    echo "  -p, --page-load            Run page load time tests only"
    echo "  -r, --response-time        Run response time tests only"
    echo "  -s, --sla                  Run SLA compliance tests only"
    echo "  --headless                 Run tests in headless browser mode (default: $HEADLESS)"
    echo "  --no-headless              Run tests with visible browser"
    echo "  -v, --verbose              Enable verbose output (default: $VERBOSE)"
    echo "  --all                      Run all tests (default if no test type specified)"
    echo
    echo "Example:"
    echo "  $(basename "$0") --headless --all"
    echo "  $(basename "$0") -p -r -v"
    exit 0
}

# Parse command-line arguments
parse_arguments() {
    local only_specific_test=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -p|--page-load)
                if [ "$only_specific_test" = false ]; then
                    # If this is the first test type flag, disable all tests first
                    RUN_PAGE_LOAD_TESTS=false
                    RUN_RESPONSE_TIME_TESTS=false
                    RUN_SLA_COMPLIANCE_TESTS=false
                    only_specific_test=true
                fi
                RUN_PAGE_LOAD_TESTS=true
                shift
                ;;
            -r|--response-time)
                if [ "$only_specific_test" = false ]; then
                    # If this is the first test type flag, disable all tests first
                    RUN_PAGE_LOAD_TESTS=false
                    RUN_RESPONSE_TIME_TESTS=false
                    RUN_SLA_COMPLIANCE_TESTS=false
                    only_specific_test=true
                fi
                RUN_RESPONSE_TIME_TESTS=true
                shift
                ;;
            -s|--sla)
                if [ "$only_specific_test" = false ]; then
                    # If this is the first test type flag, disable all tests first
                    RUN_PAGE_LOAD_TESTS=false
                    RUN_RESPONSE_TIME_TESTS=false
                    RUN_SLA_COMPLIANCE_TESTS=false
                    only_specific_test=true
                fi
                RUN_SLA_COMPLIANCE_TESTS=true
                shift
                ;;
            --headless)
                HEADLESS=true
                shift
                ;;
            --no-headless)
                HEADLESS=false
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --all)
                RUN_PAGE_LOAD_TESTS=true
                RUN_RESPONSE_TIME_TESTS=true
                RUN_SLA_COMPLIANCE_TESTS=true
                shift
                ;;
            *)
                PYTEST_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

# Setup environment
setup_environment() {
    echo "Setting up environment for performance testing..."
    
    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        echo "Error: pytest is not installed. Please install it with:"
        echo "  pip install pytest pytest-html pytest-json-report"
        exit 1
    fi
    
    # Create performance report directory if it doesn't exist
    mkdir -p "$PERFORMANCE_REPORT_DIR"
    
    # Set environment variables for performance testing
    export PERFORMANCE_TESTING=true
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Set performance thresholds based on SLA requirements
    export PAGE_LOAD_THRESHOLD=5000     # 5 seconds in milliseconds
    export API_RESPONSE_THRESHOLD=2000  # 2 seconds in milliseconds
    export USER_REGISTRATION_THRESHOLD=30000  # 30 seconds in milliseconds
    export USER_AUTHENTICATION_THRESHOLD=20000  # 20 seconds in milliseconds
    export STORY_CREATION_THRESHOLD=45000  # 45 seconds in milliseconds
    export STORY_SHARING_THRESHOLD=60000  # 60 seconds in milliseconds
    export FULL_WORKFLOW_THRESHOLD=180000  # 3 minutes in milliseconds
    
    # Set success rate thresholds
    export USER_REGISTRATION_SUCCESS_RATE=98  # 98%
    export USER_AUTHENTICATION_SUCCESS_RATE=99  # 99%
    export STORY_CREATION_SUCCESS_RATE=95  # 95%
    export STORY_SHARING_SUCCESS_RATE=95  # 95%
    export FULL_WORKFLOW_SUCCESS_RATE=90  # 90%
    
    # Set headless mode
    if [ "$HEADLESS" = true ]; then
        export HEADLESS_BROWSER=true
    else
        export HEADLESS_BROWSER=false
    fi
    
    # Set verbosity
    if [ "$VERBOSE" = true ]; then
        export VERBOSE_OUTPUT=true
    else
        export VERBOSE_OUTPUT=false
    fi
    
    echo "Environment setup complete."
    echo "Performance report directory: $PERFORMANCE_REPORT_DIR"
    echo "Headless mode: $HEADLESS"
    echo "Verbose output: $VERBOSE"
}

# Run performance tests
run_performance_tests() {
    echo "Running performance tests..."
    
    # Change to project root directory
    cd "$PROJECT_ROOT" || { echo "Failed to change to project root directory"; exit 1; }
    
    # Base pytest command
    PYTEST_CMD="python -m pytest"
    
    # Add verbosity if requested
    if [ "$VERBOSE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -v"
    fi
    
    # Add test paths based on enabled test types
    TEST_PATHS=""
    if [ "$RUN_PAGE_LOAD_TESTS" = true ]; then
        TEST_PATHS="$TEST_PATHS src/test/python/performance/test_page_load_times.py"
    fi
    
    if [ "$RUN_RESPONSE_TIME_TESTS" = true ]; then
        TEST_PATHS="$TEST_PATHS src/test/python/performance/test_api_response_times.py"
    fi
    
    if [ "$RUN_SLA_COMPLIANCE_TESTS" = true ]; then
        TEST_PATHS="$TEST_PATHS src/test/python/performance/test_sla_compliance.py"
    fi
    
    # If no specific tests were enabled, run all tests
    if [ -z "$TEST_PATHS" ]; then
        TEST_PATHS="src/test/python/performance/"
    fi
    
    # Add report generation options
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    REPORT_OPTIONS="--html=$PERFORMANCE_REPORT_DIR/report_$TIMESTAMP.html --self-contained-html"
    REPORT_OPTIONS="$REPORT_OPTIONS --json-report --json-report-file=$PERFORMANCE_REPORT_DIR/report_$TIMESTAMP.json"
    
    # Add additional pytest arguments
    ADDITIONAL_ARGS=""
    if [ ${#PYTEST_ARGS[@]} -gt 0 ]; then
        ADDITIONAL_ARGS="${PYTEST_ARGS[*]}"
    fi
    
    # Combine everything into the final command
    FINAL_CMD="$PYTEST_CMD $TEST_PATHS $REPORT_OPTIONS $ADDITIONAL_ARGS"
    
    echo "Running performance tests with command:"
    echo "$FINAL_CMD"
    
    # Execute the command
    eval "$FINAL_CMD"
    local exit_code=$?
    
    # Create symbolic links to the latest reports for easier access
    ln -sf "$PERFORMANCE_REPORT_DIR/report_$TIMESTAMP.html" "$PERFORMANCE_REPORT_DIR/latest_report.html"
    ln -sf "$PERFORMANCE_REPORT_DIR/report_$TIMESTAMP.json" "$PERFORMANCE_REPORT_DIR/latest_report.json"
    
    echo "Performance test execution complete."
    echo "Reports available at:"
    echo "  HTML: $PERFORMANCE_REPORT_DIR/latest_report.html"
    echo "  JSON: $PERFORMANCE_REPORT_DIR/latest_report.json"
    
    return $exit_code
}

# Clean up resources
cleanup() {
    echo "Cleaning up resources..."
    
    # Kill any stray browser processes
    if [ "$(uname)" = "Linux" ]; then
        pkill -f "chrome" > /dev/null 2>&1 || true
        pkill -f "firefox" > /dev/null 2>&1 || true
    elif [ "$(uname)" = "Darwin" ]; then
        pkill -f "Chrome" > /dev/null 2>&1 || true
        pkill -f "Firefox" > /dev/null 2>&1 || true
    elif [[ "$(uname)" == MINGW* ]] || [[ "$(uname)" == MSYS* ]]; then
        taskkill //F //IM chrome.exe //T > /dev/null 2>&1 || true
        taskkill //F //IM firefox.exe //T > /dev/null 2>&1 || true
    fi
    
    # Remove temporary files
    find "$PROJECT_ROOT" -name "*.pyc" -delete
    
    echo "Cleanup complete."
}

# Main function
main() {
    # Parse command-line arguments
    parse_arguments "$@"
    
    # Setup environment
    setup_environment
    
    # Run performance tests
    run_performance_tests
    local exit_code=$?
    
    # Cleanup resources
    cleanup
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Performance tests completed successfully."
    else
        echo "❌ Performance tests failed with exit code $exit_code."
    fi
    
    # Return exit code from tests
    return $exit_code
}

# Execute main function
main "$@"
exit $?