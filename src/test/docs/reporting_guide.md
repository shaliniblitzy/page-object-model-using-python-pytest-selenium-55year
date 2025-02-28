# Storydoc Test Automation Framework: Reporting Guide

## 1. Introduction

This guide details the reporting capabilities of the Storydoc test automation framework. It covers how to generate, customize, and analyze test reports to ensure quality and gain insights into test execution.

### 1.1 Purpose of Test Reporting

Test reporting in the Storydoc automation framework serves several key purposes:

- Providing visibility into test execution results
- Capturing evidence of test failures for debugging
- Tracking performance metrics against SLAs
- Supporting quality metrics and trend analysis
- Facilitating communication with stakeholders

### 1.2 Types of Reports

The framework supports multiple report formats:

| Report Type | Format | Primary Purpose |
|-------------|--------|------------------|
| HTML Reports | `.html` | Comprehensive visual reports with screenshots and metrics |
| JSON Reports | `.json` | Machine-readable data for programmatic processing |
| JUnit XML | `.xml` | Integration with CI/CD systems |
| Summary Reports | Text/Console | Quick overview of test execution results |
| Performance Reports | HTML/JSON | Detailed timing metrics for SLA compliance monitoring |

## 2. Report Configuration

### 2.1 Directory Structure

Reports are organized in the following directory structure:

```
src/test/reports/
├── html/           # HTML reports
├── screenshots/    # Test failure screenshots
├── logs/           # Test execution logs
└── performance/    # Performance metrics
```

### 2.2 Configuration Settings

Reporting settings can be configured in several ways:

1. Default configurations in `src/test/config/reporting_config.py`
2. Environment variables (prefixed with `TEST_`)
3. Command line arguments when running tests
4. Programmatic configuration in code

Key configuration options include:

```python
# HTML report options
html_report_options = {
    'report_title': 'Storydoc Test Automation Report',
    'add_timestamp': True,
    'include_screenshots': True,
    'include_logs': True,
    'include_performance': True,
    'theme': 'default'
}

# Screenshot options
screenshot_options = {
    'take_on_failure': True,
    'format': 'png',
    'resize_factor': 1.0,
    'highlight_elements': True
}

# Logging options
logging_options = {
    'log_level': 'INFO',
    'include_timestamps': True,
    'console_output': True,
    'file_output': True
}

# Performance options
performance_options = {
    'track_execution_time': True,
    'track_page_load_time': True,
    'track_api_response_time': True,
    'sla_monitoring': True
}
```

## 3. Generating Reports

### 3.1 Using pytest-html Plugin

The framework uses pytest-html plugin for HTML report generation. To generate reports during test execution:

```bash
pytest --html=report.html --self-contained-html
```

Additional pytest-html options:

```bash
pytest --html=report.html \
       --self-contained-html \
       --css=custom.css \
       --report-log=report.log
```

### 3.2 Using the Report Generation Script

The framework includes a dedicated script for report generation:

```bash
# Generate HTML report
./src/test/scripts/generate_report.sh -f html -o report.html

# Generate JSON report
./src/test/scripts/generate_report.sh -f json -o report.json

# Generate summary report
./src/test/scripts/generate_report.sh -f summary
```

Script options:

```
Usage: generate_report.sh [options]

Options:
  -f, --format FORMAT    Report format: html, json, junit, summary (default: html)
  -o, --output FILE      Output file path (default: auto-generated name with timestamp)
  -i, --input FILE       Input test results file (default: latest results)
  -p, --performance      Include performance metrics
  -s, --screenshots      Include screenshots
  -l, --logs             Include logs
  -h, --help             Show this help message
```

### 3.3 Programmatic Report Generation

Reports can also be generated programmatically using the `ReportingHelper` class:

```python
from src.test.utilities.reporting_helper import ReportingHelper

# Initialize reporting helper
reporting_helper = ReportingHelper()

# Generate HTML report
report_path = reporting_helper.generate_summary_report(
    report_name='custom_report.html',
    test_results=test_results_data
)

print(f"Report generated at: {report_path}")
```

## 4. Report Customization

### 4.1 Custom CSS Styling

HTML reports can be customized with custom CSS:

```python
from src.test.utilities.reporting_helper import ReportingHelper

custom_css = """
.report-header { background-color: #2c3e50; color: white; }
.pass { background-color: #27ae60; }
.fail { background-color: #e74c3c; }
.skip { background-color: #f39c12; }
"""

ReportingHelper().customize_style(custom_css)
```

### 4.2 Extending HTML Reports

The HTML report can be extended with custom sections using the `HTMLReportExtension` class:

```python
from src.test.utilities.reporting_helper import HTMLReportExtension

class CustomReportExtension(HTMLReportExtension):
    def pytest_html_results_summary(self, prefix, summary, postfix):
        # Add custom summary section
        summary.append('<h2>Custom Test Summary</h2>')
        summary.append('<p>Add your custom information here</p>')

# Register the extension in conftest.py
pytest_plugins = [CustomReportExtension()]
```

### 4.3 Adding Custom Content

Custom content can be added to test reports:

```python
# Add a screenshot
reporting_helper.add_screenshot('path/to/screenshot.png', 'Screenshot description')

# Add HTML content
reporting_helper.add_html_content('<div class="custom">Custom HTML</div>', 'Custom Section')

# Add a data table
headers = ['Column 1', 'Column 2', 'Column 3']
rows = [
    ['Value 1A', 'Value 1B', 'Value 1C'],
    ['Value 2A', 'Value 2B', 'Value 2C']
]
reporting_helper.add_table(headers, rows, 'Data Table Example')

# Add JSON data
json_data = {
    'key1': 'value1',
    'key2': 'value2',
    'nested': {
        'key3': 'value3'
    }
}
reporting_helper.add_json_data(json_data, 'JSON Example')
```

## 5. Screenshot Capture

### 5.1 Automatic Screenshot Capture

The framework automatically captures screenshots on test failures through pytest hooks in `conftest.py`:

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # If test failed in call phase, capture a screenshot
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshot_path = screenshot_manager.capture_failure_screenshot(
                driver, 
                item.name, 
                str(report.longrepr)
            )
            # Add screenshot to report
            if screenshot_path:
                report.extra = [
                    {'name': 'Screenshot', 'content': screenshot_path, 'type': 'image'}
                ]
```

### 5.2 Manual Screenshot Capture

Screenshots can also be captured manually during test execution:

```python
from src.test.utilities.screenshot_manager import ScreenshotManager

# Capture a regular screenshot
screenshot_path = ScreenshotManager().capture_screenshot(
    driver,
    filename="custom-screenshot",
    subfolder="custom"
)

# Capture a screenshot highlighting a specific element
element = driver.find_element(By.ID, "element-id")
screenshot_path = ScreenshotManager().capture_element_screenshot(
    driver,
    element,
    filename="element-screenshot"
)
```

## 6. Performance Monitoring

### 6.1 Tracking Test Execution Time

The framework tracks test execution time for performance monitoring:

```python
from src.test.utilities.performance_monitor import PerformanceMonitor

performance_monitor = PerformanceMonitor()

# Start a timer
performance_monitor.start_timer("login_process")

# Perform login steps
# ...

# Stop the timer
performance_monitor.stop_timer("login_process")

# Get elapsed time
elapsed_time = performance_monitor.get_elapsed_time("login_process")
print(f"Login process took {elapsed_time:.2f} seconds")

# Check against SLA
SLA_LIMIT = 3.0  # seconds
assert elapsed_time <= SLA_LIMIT, f"Login exceeded SLA limit of {SLA_LIMIT}s"
```

### 6.2 SLA Compliance Monitoring

Tests can be annotated for SLA monitoring:

```python
@pytest.mark.sla_limit(seconds=5)
def test_user_registration():
    # Test implementation
    pass
```

SLA compliance is reported in the performance section of the HTML report.

### 6.3 Performance Reports

A dedicated performance summary can be generated:

```python
from src.test.utilities.performance_monitor import PerformanceMonitor

# Get performance summary
summary = PerformanceMonitor().get_performance_summary()

# Add to HTML report
reporting_helper.add_performance_data(
    categories=["page_load", "api_response", "test_execution"],
    title="Performance Metrics"
)
```

## 7. Integration with CI/CD

### 7.1 GitHub Actions Integration

Example GitHub Actions workflow using the reporting capabilities:

```yaml
name: Storydoc Test Automation

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r src/test/requirements.txt
      - name: Run tests
        run: |
          pytest src/test/tests/ --html=report.html --self-contained-html
      - name: Generate custom report
        run: |
          ./src/test/scripts/generate_report.sh -f html -o custom_report.html -p -s -l
      - name: Upload test report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: |
            report.html
            custom_report.html
            src/test/reports/screenshots/
```

### 7.2 Test Status Notifications

Automated notifications can be set up based on test report results:

```python
from src.test.utilities.reporting_helper import ReportingHelper

# Get test results summary
test_results = ReportingHelper().get_test_results_summary()

# Send notification if failure rate exceeds threshold
failure_rate = test_results['failure_rate']
if failure_rate > 10.0:  # More than 10% failure rate
    send_slack_notification(
        channel="#test-alerts",
        message=f"⚠️ High test failure rate: {failure_rate:.1f}%",
        report_url="http://ci-server/reports/latest.html"
    )
```

## 8. Analyzing Reports

### 8.1 Understanding HTML Reports

The HTML report structure includes:

1. **Header**: Test execution summary with pass/fail/skip counts and duration
2. **Environment**: Details about test environment (browser, OS, etc.)
3. **Results Table**: Detailed list of test cases with status and duration
4. **Failure Details**: For failed tests, error messages and screenshots
5. **Performance Metrics**: Timing data for key operations
6. **Logs**: Test execution logs for debugging

### 8.2 Identifying Test Flakiness

The reporting system helps identify flaky tests through:

- Test history tracking across multiple runs
- Highlighting tests with inconsistent results
- Detailed timing information for intermittent failures
- Screenshots at the point of failure

### 8.3 Performance Trend Analysis

Performance trends can be analyzed to identify degradation:

```python
from src.test.utilities.performance_monitor import PerformanceMonitor

# Compare current performance with baseline
current = PerformanceMonitor().get_operation_timing("login")
baseline = PerformanceMonitor().get_baseline_timing("login")

percentage_change = ((current - baseline) / baseline) * 100
if percentage_change > 10:  # More than 10% slower
    print(f"⚠️ Performance degradation: Login is {percentage_change:.1f}% slower than baseline")
```

## 9. Best Practices

### 9.1 Report Naming Conventions

Follow these naming conventions for reports:

- Use descriptive names with timestamps: `storydoc_regression_20230615_120000.html`
- Include test type in the filename: `user_workflow_smoke_test.html`
- Use consistent naming across CI/CD pipelines

### 9.2 Screenshot Management

For effective screenshot management:

- Include test name and timestamp in screenshot filenames
- Organize screenshots in subdirectories by test suite
- Periodically clean up old screenshots to save space

```python
# Clean up screenshots older than 30 days
ScreenshotManager().clean_old_screenshots(days=30)
```

### 9.3 Optimizing Report Size

To keep reports manageable:

- Be selective about which screenshots to include
- Consider compression for large screenshots
- Use log level filtering to reduce log verbosity
- Set up retention policies for old reports

## 10. Troubleshooting

### 10.1 Common Issues

| Issue | Cause | Resolution |
|-------|------|------------|
| Missing screenshots in report | File path issues or write permissions | Check directory permissions and ensure absolute paths are used |
| Reports too large | Too many embedded screenshots | Enable selective screenshot capture or use lower resolution |
| Performance data not appearing | Performance monitoring not enabled | Verify performance_options configuration is correctly set |
| HTML report styling broken | CSS conflicts or missing resources | Use self-contained HTML option or verify CSS path |
| Report generation script fails | Environment or dependency issues | Check Python environment and required packages |

### 10.2 Debugging Report Generation

Enable debug logging to troubleshoot report generation:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
reporting_logger = logging.getLogger('reporting')
reporting_logger.setLevel(logging.DEBUG)
```

## 11. References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-html Plugin](https://pytest-html.readthedocs.io/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Internal Framework Documentation](/src/test/docs/)
  - [Framework Overview](/src/test/docs/framework_overview.md)
  - [Setup Guide](/src/test/docs/setup_guide.md)
  - [Test Cases](/src/test/docs/test_cases.md)

## 12. Appendix

### 12.1 Report Schema

The JSON report schema structure:

```json
{
  "test_session": {
    "start_time": "2023-06-15T12:00:00",
    "end_time": "2023-06-15T12:10:00",
    "duration": 600.0,
    "environment": {
      "browser": "Chrome",
      "browser_version": "114.0.5735.110",
      "os": "Windows 10",
      "python_version": "3.9.6"
    }
  },
  "summary": {
    "total": 50,
    "passed": 45,
    "failed": 3,
    "skipped": 2,
    "pass_rate": 90.0,
    "failure_rate": 6.0,
    "skip_rate": 4.0
  },
  "results": [
    {
      "test_id": "test_user_registration",
      "status": "passed",
      "duration": 5.2,
      "sla_limit": 10.0,
      "sla_met": true
    },
    {
      "test_id": "test_invalid_login",
      "status": "failed",
      "duration": 3.8,
      "error": "AssertionError: Expected error message not displayed",
      "traceback": "...",
      "screenshots": ["path/to/screenshot.png"]
    }
  ],
  "performance": {
    "page_load_times": {
      "login_page": 1.2,
      "dashboard": 2.3,
      "story_editor": 1.8
    },
    "api_response_times": {
      "authentication": 0.8,
      "story_save": 1.5,
      "sharing": 0.9
    },
    "operation_times": {
      "registration": 8.5,
      "authentication": 5.2,
      "story_creation": 12.3,
      "story_sharing": 9.8
    }
  }
}
```

### 12.2 Report Templates

The framework includes customizable HTML templates. To create a custom template:

1. Create a template file (e.g., `custom_template.html`) in `src/test/templates/`
2. Use Jinja2 template syntax for dynamic content
3. Configure the template in `reporting_config.py`:

```python
html_report_options = {
    # ...
    'template': 'custom_template.html'
}
```

Reference the existing template at `src/test/templates/report_template.html` for structure and variables.