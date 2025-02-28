#!/bin/bash
# generate_report.sh
# Shell script that generates comprehensive test reports for the Storydoc automation framework

# Source the setup environment script to use its functions
source "$(dirname "$0")/setup_environment.sh"

# Global variables
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
TEST_DIR="$PROJECT_ROOT/src/test"
REPORTS_DIR="$TEST_DIR/reports"
HTML_REPORTS_DIR="$REPORTS_DIR/html"
SCREENSHOTS_DIR="$REPORTS_DIR/screenshots"
PERFORMANCE_DIR="$REPORTS_DIR/performance"
LOG_DIR="$REPORTS_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEFAULT_REPORT_NAME="report_$TIMESTAMP.html"
DEFAULT_JSON_NAME="report_$TIMESTAMP.json"
DEFAULT_JUNIT_NAME="report_$TIMESTAMP.xml"
DEFAULT_REPORT_FORMAT="html"
DEFAULT_TEST_RESULTS_PATH="$TEST_DIR/reports/results.json"

# Print usage information
print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help                   Display this help message"
    echo "  -f, --format FORMAT          Report format (html, json, junit, summary) [default: html]"
    echo "  -o, --output PATH            Path to save the report"
    echo "  -i, --input PATH             Path to test results JSON file"
    echo "  -p, --performance            Include performance metrics in the report"
    echo "  -t, --title TITLE            Report title"
    echo "  -s, --screenshots            Include screenshots in HTML report"
    echo ""
    echo "Examples:"
    echo "  $0 -f html -o ./report.html"
    echo "  $0 --format json --output ./report.json --performance"
    echo "  $0 -f summary -i ./test_results.json"
    echo ""
    echo "Available formats:"
    echo "  html     - HTML report with test results, screenshots, and charts"
    echo "  json     - JSON formatted report for programmatic consumption"
    echo "  junit    - JUnit XML format for CI/CD integration"
    echo "  summary  - Brief text summary of test execution"
}

# Parse command-line arguments
parse_arguments() {
    # Default values
    REPORT_FORMAT="$DEFAULT_REPORT_FORMAT"
    REPORT_PATH=""
    TEST_RESULTS_PATH="$DEFAULT_TEST_RESULTS_PATH"
    INCLUDE_PERFORMANCE=false
    REPORT_TITLE="Storydoc Test Report - $(date '+%Y-%m-%d %H:%M:%S')"
    INCLUDE_SCREENSHOTS=false

    # Parse options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                print_usage
                exit 0
                ;;
            -f|--format)
                REPORT_FORMAT="$2"
                shift 2
                ;;
            -o|--output)
                REPORT_PATH="$2"
                shift 2
                ;;
            -i|--input)
                TEST_RESULTS_PATH="$2"
                shift 2
                ;;
            -p|--performance)
                INCLUDE_PERFORMANCE=true
                shift
                ;;
            -t|--title)
                REPORT_TITLE="$2"
                shift 2
                ;;
            -s|--screenshots)
                INCLUDE_SCREENSHOTS=true
                shift
                ;;
            *)
                echo "Error: Unknown option $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Set default report path if not specified
    if [ -z "$REPORT_PATH" ]; then
        case "$REPORT_FORMAT" in
            html)
                REPORT_PATH="$HTML_REPORTS_DIR/$DEFAULT_REPORT_NAME"
                ;;
            json)
                REPORT_PATH="$HTML_REPORTS_DIR/$DEFAULT_JSON_NAME"
                ;;
            junit)
                REPORT_PATH="$HTML_REPORTS_DIR/$DEFAULT_JUNIT_NAME"
                ;;
            summary)
                REPORT_PATH="$HTML_REPORTS_DIR/summary_$TIMESTAMP.txt"
                ;;
            *)
                echo "Error: Unknown report format: $REPORT_FORMAT"
                print_usage
                exit 1
                ;;
        esac
    fi

    # Validate format
    case "$REPORT_FORMAT" in
        html|json|junit|summary)
            # Valid format
            ;;
        *)
            echo "Error: Invalid report format: $REPORT_FORMAT"
            print_usage
            exit 1
            ;;
    esac

    # Export variables for other functions to use
    export REPORT_FORMAT
    export REPORT_PATH
    export TEST_RESULTS_PATH
    export INCLUDE_PERFORMANCE
    export REPORT_TITLE
    export INCLUDE_SCREENSHOTS
}

# Ensure all required directories exist
setup_directories() {
    # Call the function from setup_environment.sh
    create_directories
    
    # Create parent directory for report if it doesn't exist
    local report_dir=$(dirname "$REPORT_PATH")
    if [ ! -d "$report_dir" ]; then
        mkdir -p "$report_dir"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create report directory: $report_dir"
            return 1
        fi
    fi

    return 0
}

# Generate HTML report
generate_html_report() {
    local test_results_path="$1"
    local report_path="$2"
    
    echo "Generating HTML report from $test_results_path to $report_path..."
    
    # Check if test results file exists
    if [ ! -f "$test_results_path" ]; then
        echo "Error: Test results file not found: $test_results_path"
        return 1
    fi
    
    # Create a Python script to generate the report
    local script_path=$(generate_python_script "html" "$test_results_path" "$report_path")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create Python script for HTML report generation"
        return 1
    fi
    
    # Execute the Python script
    python3 "$script_path"
    local result=$?
    
    # Remove the temporary script
    rm -f "$script_path"
    
    if [ $result -eq 0 ]; then
        echo "HTML report generated successfully: $report_path"
        return 0
    else
        echo "Error: Failed to generate HTML report"
        return 1
    fi
}

# Generate JSON report
generate_json_report() {
    local test_results_path="$1"
    local report_path="$2"
    
    echo "Generating JSON report from $test_results_path to $report_path..."
    
    # Check if test results file exists
    if [ ! -f "$test_results_path" ]; then
        echo "Error: Test results file not found: $test_results_path"
        return 1
    fi
    
    # Create a Python script to generate the report
    local script_path=$(generate_python_script "json" "$test_results_path" "$report_path")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create Python script for JSON report generation"
        return 1
    fi
    
    # Execute the Python script
    python3 "$script_path"
    local result=$?
    
    # Remove the temporary script
    rm -f "$script_path"
    
    if [ $result -eq 0 ]; then
        echo "JSON report generated successfully: $report_path"
        return 0
    else
        echo "Error: Failed to generate JSON report"
        return 1
    fi
}

# Generate JUnit XML report
generate_junit_report() {
    local test_results_path="$1"
    local report_path="$2"
    
    echo "Generating JUnit XML report from $test_results_path to $report_path..."
    
    # Check if test results file exists
    if [ ! -f "$test_results_path" ]; then
        echo "Error: Test results file not found: $test_results_path"
        return 1
    fi
    
    # Create a Python script to generate the report
    local script_path=$(generate_python_script "junit" "$test_results_path" "$report_path")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create Python script for JUnit XML report generation"
        return 1
    fi
    
    # Execute the Python script
    python3 "$script_path"
    local result=$?
    
    # Remove the temporary script
    rm -f "$script_path"
    
    if [ $result -eq 0 ]; then
        echo "JUnit XML report generated successfully: $report_path"
        return 0
    else
        echo "Error: Failed to generate JUnit XML report"
        return 1
    fi
}

# Generate summary report
generate_summary_report() {
    local test_results_path="$1"
    local report_path="$2"
    
    echo "Generating summary report from $test_results_path to $report_path..."
    
    # Check if test results file exists
    if [ ! -f "$test_results_path" ]; then
        echo "Error: Test results file not found: $test_results_path"
        return 1
    fi
    
    # Create a Python script to generate the report
    local script_path=$(generate_python_script "summary" "$test_results_path" "$report_path")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create Python script for summary report generation"
        return 1
    fi
    
    # Execute the Python script
    python3 "$script_path"
    local result=$?
    
    # Remove the temporary script
    rm -f "$script_path"
    
    if [ $result -eq 0 ]; then
        echo "Summary report generated successfully: $report_path"
        # Display the summary to the console too
        if [ -f "$report_path" ]; then
            echo ""
            echo "Test Summary:"
            echo "============="
            cat "$report_path"
        fi
        return 0
    else
        echo "Error: Failed to generate summary report"
        return 1
    fi
}

# Check if Python environment is set up correctly
check_python_environment() {
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in PATH"
        return 1
    fi
    
    # Check Python version
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local min_version="3.9"
    
    if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
        echo "Error: Python version $python_version is less than required minimum $min_version"
        return 1
    fi
    
    # Check if required packages are installed
    local required_packages=("pytest" "pytest-html" "jinja2" "matplotlib" "pandas")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "Error: The following required Python packages are missing:"
        for package in "${missing_packages[@]}"; do
            echo "  - $package"
        done
        echo "Please install them using: pip install ${missing_packages[*]}"
        return 1
    fi
    
    return 0
}

# Generate Python script for report generation
generate_python_script() {
    local report_format="$1"
    local test_results_path="$2"
    local report_path="$3"
    
    # Create a temporary file
    local temp_file=$(mktemp /tmp/report_script_XXXXXX.py)
    
    # Write Python script content
    cat > "$temp_file" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
from pathlib import Path

# Report configuration
report_format = "$report_format"
test_results_path = "$test_results_path"
report_path = "$report_path"
include_performance = $INCLUDE_PERFORMANCE
report_title = "$REPORT_TITLE"
include_screenshots = $INCLUDE_SCREENSHOTS
screenshots_dir = "$SCREENSHOTS_DIR"
performance_dir = "$PERFORMANCE_DIR"

class ReportingHelper:
    """Helper class for generating test reports"""
    
    @staticmethod
    def load_test_results(file_path):
        """Load test results from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test results: {e}")
            sys.exit(1)
    
    @staticmethod
    def generate_html_report(test_results, output_path, title, include_screenshots=False, screenshots_dir=None):
        """Generate HTML report from test results"""
        try:
            # Calculate summary statistics
            total_tests = len(test_results.get('tests', []))
            passed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'passed'])
            failed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'failed'])
            skipped = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'skipped'])
            error = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'error'])
            
            pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
            
            # Create HTML content
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .summary {{ display: flex; justify-content: space-between; background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 24px; font-weight: bold; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .error {{ color: #6c757d; }}
        .total {{ color: #17a2b8; }}
        .test-case {{ margin-bottom: 10px; padding: 10px; border-radius: 5px; }}
        .test-case-passed {{ background-color: #d4edda; }}
        .test-case-failed {{ background-color: #f8d7da; }}
        .test-case-skipped {{ background-color: #fff3cd; }}
        .test-case-error {{ background-color: #e2e3e5; }}
        .test-name {{ font-weight: bold; }}
        .test-duration {{ font-size: 0.9em; color: #6c757d; }}
        .test-error {{ color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-top: 10px; white-space: pre-wrap; }}
        .screenshot {{ max-width: 100%; margin-top: 10px; border: 1px solid #ddd; }}
        .timestamp {{ color: #6c757d; font-size: 0.9em; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <div class="summary-item">
            <div class="summary-number total">{total_tests}</div>
            <div>Total</div>
        </div>
        <div class="summary-item">
            <div class="summary-number passed">{passed}</div>
            <div>Passed</div>
        </div>
        <div class="summary-item">
            <div class="summary-number failed">{failed}</div>
            <div>Failed</div>
        </div>
        <div class="summary-item">
            <div class="summary-number skipped">{skipped}</div>
            <div>Skipped</div>
        </div>
        <div class="summary-item">
            <div class="summary-number error">{error}</div>
            <div>Error</div>
        </div>
        <div class="summary-item">
            <div class="summary-number">{pass_rate:.2f}%</div>
            <div>Pass Rate</div>
        </div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test</th>
            <th>Outcome</th>
            <th>Duration (s)</th>
        </tr>
"""
            
            # Add test cases
            for test in test_results.get('tests', []):
                outcome = test.get('outcome', 'unknown')
                name = test.get('name', 'Unnamed Test')
                duration = test.get('duration', 0)
                error_message = test.get('error_message', '')
                
                html += f"""
        <tr>
            <td>{name}</td>
            <td>{outcome}</td>
            <td>{duration:.2f}</td>
        </tr>"""
            
            html += """
    </table>
    
    <h2>Detailed Results</h2>
"""
            
            # Add detailed test results
            for test in test_results.get('tests', []):
                outcome = test.get('outcome', 'unknown')
                name = test.get('name', 'Unnamed Test')
                duration = test.get('duration', 0)
                error_message = test.get('error_message', '')
                screenshot = test.get('screenshot', '')
                
                outcome_class = f"test-case-{outcome}"
                
                html += f"""
    <div class="test-case {outcome_class}">
        <div class="test-name">{name}</div>
        <div class="test-duration">Duration: {duration:.2f} seconds</div>
"""
                
                if error_message:
                    html += f"""
        <div class="test-error">{error_message}</div>
"""
                
                if include_screenshots and screenshot and screenshots_dir:
                    screenshot_path = os.path.join(screenshots_dir, screenshot)
                    if os.path.exists(screenshot_path):
                        # Get relative path from the report to the screenshot
                        report_dir = os.path.dirname(os.path.abspath(output_path))
                        rel_path = os.path.relpath(screenshot_path, report_dir)
                        html += f"""
        <div>
            <img class="screenshot" src="{rel_path}" alt="Screenshot">
        </div>
"""
                
                html += """
    </div>
"""
            
            # Add performance metrics if available and requested
            if include_performance and 'performance' in test_results:
                html += """
    <h2>Performance Metrics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
"""
                
                for metric, value in test_results.get('performance', {}).items():
                    html += f"""
        <tr>
            <td>{metric}</td>
            <td>{value}</td>
        </tr>"""
                
                html += """
    </table>
"""
            
            # Closing HTML
            html += """
</body>
</html>
"""
            
            # Write HTML to file
            with open(output_path, 'w') as f:
                f.write(html)
            
            return True
            
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return False
    
    @staticmethod
    def generate_json_report(test_results, output_path):
        """Generate JSON report from test results"""
        try:
            # Add report metadata
            report_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'test_results': test_results
            }
            
            # Calculate summary statistics
            total_tests = len(test_results.get('tests', []))
            passed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'passed'])
            failed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'failed'])
            skipped = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'skipped'])
            error = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'error'])
            
            pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
            
            # Add summary
            report_data['summary'] = {
                'total': total_tests,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'error': error,
                'pass_rate': pass_rate
            }
            
            # Write JSON to file
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error generating JSON report: {e}")
            return False
    
    @staticmethod
    def generate_junit_report(test_results, output_path):
        """Generate JUnit XML report from test results"""
        try:
            # Create XML content
            xml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
"""
            
            # Group tests by test suite
            test_suites = {}
            for test in test_results.get('tests', []):
                suite_name = test.get('suite', 'unknown')
                if suite_name not in test_suites:
                    test_suites[suite_name] = []
                test_suites[suite_name].append(test)
            
            # Add test suites
            for suite_name, tests in test_suites.items():
                # Calculate suite statistics
                total_tests = len(tests)
                failures = len([t for t in tests if t.get('outcome') == 'failed'])
                skipped = len([t for t in tests if t.get('outcome') == 'skipped'])
                errors = len([t for t in tests if t.get('outcome') == 'error'])
                
                # Calculate suite time
                suite_time = sum(t.get('duration', 0) for t in tests)
                
                xml += f"""  <testsuite name="{suite_name}" tests="{total_tests}" failures="{failures}" errors="{errors}" skipped="{skipped}" time="{suite_time:.2f}">
"""
                
                # Add test cases
                for test in tests:
                    name = test.get('name', 'Unnamed Test')
                    duration = test.get('duration', 0)
                    outcome = test.get('outcome', 'unknown')
                    error_message = test.get('error_message', '')
                    
                    xml += f"""    <testcase name="{name}" time="{duration:.2f}">
"""
                    
                    if outcome == 'failed':
                        xml += f"""      <failure message="{error_message}"></failure>
"""
                    elif outcome == 'error':
                        xml += f"""      <error message="{error_message}"></error>
"""
                    elif outcome == 'skipped':
                        xml += """      <skipped/>
"""
                    
                    xml += """    </testcase>
"""
                
                xml += """  </testsuite>
"""
            
            xml += """</testsuites>
"""
            
            # Write XML to file
            with open(output_path, 'w') as f:
                f.write(xml)
            
            return True
            
        except Exception as e:
            print(f"Error generating JUnit XML report: {e}")
            return False
    
    @staticmethod
    def generate_summary_report(test_results, output_path):
        """Generate summary report from test results"""
        try:
            # Calculate summary statistics
            total_tests = len(test_results.get('tests', []))
            passed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'passed'])
            failed = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'failed'])
            skipped = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'skipped'])
            error = len([t for t in test_results.get('tests', []) if t.get('outcome') == 'error'])
            
            pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
            fail_rate = (failed / total_tests) * 100 if total_tests > 0 else 0
            skip_rate = (skipped / total_tests) * 100 if total_tests > 0 else 0
            error_rate = (error / total_tests) * 100 if total_tests > 0 else 0
            
            # Calculate total duration
            total_duration = sum(t.get('duration', 0) for t in test_results.get('tests', []))
            
            # Create summary text
            summary = f"""TEST SUMMARY
===========
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Tests:   {total_tests}
Passed:        {passed} ({pass_rate:.2f}%)
Failed:        {failed} ({fail_rate:.2f}%)
Skipped:       {skipped} ({skip_rate:.2f}%)
Errors:        {error} ({error_rate:.2f}%)

Total Duration: {total_duration:.2f} seconds
"""
            
            # Add failed tests
            if failed > 0:
                summary += "\nFAILED TESTS\n============\n"
                for test in test_results.get('tests', []):
                    if test.get('outcome') == 'failed':
                        name = test.get('name', 'Unnamed Test')
                        duration = test.get('duration', 0)
                        error_message = test.get('error_message', 'No error message')
                        summary += f"\n{name} ({duration:.2f}s)\n"
                        summary += f"Error: {error_message}\n"
            
            # Add skipped tests
            if skipped > 0:
                summary += "\nSKIPPED TESTS\n=============\n"
                for test in test_results.get('tests', []):
                    if test.get('outcome') == 'skipped':
                        name = test.get('name', 'Unnamed Test')
                        summary += f"{name}\n"
            
            # Write summary to file
            with open(output_path, 'w') as f:
                f.write(summary)
            
            return True
            
        except Exception as e:
            print(f"Error generating summary report: {e}")
            return False

# Main execution
def main():
    # Load test results
    test_results = ReportingHelper.load_test_results(test_results_path)
    
    # Generate report based on format
    if report_format == 'html':
        success = ReportingHelper.generate_html_report(
            test_results, 
            report_path, 
            report_title, 
            include_screenshots, 
            screenshots_dir
        )
    elif report_format == 'json':
        success = ReportingHelper.generate_json_report(test_results, report_path)
    elif report_format == 'junit':
        success = ReportingHelper.generate_junit_report(test_results, report_path)
    elif report_format == 'summary':
        success = ReportingHelper.generate_summary_report(test_results, report_path)
    else:
        print(f"Error: Unknown report format: {report_format}")
        return 1
    
    if success:
        print(f"Report generated successfully: {report_path}")
        return 0
    else:
        print(f"Error generating {report_format} report")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    chmod +x "$temp_file"
    echo "$temp_file"
    return 0
}

# Main function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Check Python environment
    if ! check_python_environment; then
        echo "Error: Python environment is not set up correctly"
        return 1
    fi
    
    # Set up directories
    if ! setup_directories; then
        echo "Error: Failed to set up directories"
        return 1
    fi
    
    # Generate report based on format
    case "$REPORT_FORMAT" in
        html)
            if ! generate_html_report "$TEST_RESULTS_PATH" "$REPORT_PATH"; then
                echo "Error: Failed to generate HTML report"
                return 1
            fi
            ;;
        json)
            if ! generate_json_report "$TEST_RESULTS_PATH" "$REPORT_PATH"; then
                echo "Error: Failed to generate JSON report"
                return 1
            fi
            ;;
        junit)
            if ! generate_junit_report "$TEST_RESULTS_PATH" "$REPORT_PATH"; then
                echo "Error: Failed to generate JUnit XML report"
                return 1
            fi
            ;;
        summary)
            if ! generate_summary_report "$TEST_RESULTS_PATH" "$REPORT_PATH"; then
                echo "Error: Failed to generate summary report"
                return 1
            fi
            ;;
        *)
            echo "Error: Invalid report format: $REPORT_FORMAT"
            print_usage
            return 1
            ;;
    esac
    
    echo ""
    echo "Report generation completed successfully."
    echo "Report saved to: $REPORT_PATH"
    
    return 0
}

# Execute main function with all arguments
main "$@"
exit $?