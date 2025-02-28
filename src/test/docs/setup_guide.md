# Setup Guide for Storydoc Test Automation Framework

This guide provides comprehensive instructions for setting up and configuring the Storydoc Test Automation Framework. Follow these steps to get the framework up and running for automating tests on the Storydoc application.

## Prerequisites

Before installing the framework, ensure your system meets the following requirements:

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 20.04+ (any modern OS with Python support)
- **CPU**: 2 cores minimum (4 cores recommended)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 1GB free space minimum (5GB recommended)
- **Network**: Stable internet connection

### Required Software

- **Python**: Version 3.9 or higher
- **Git**: Latest version for source control
- **Browser**: Chrome (latest version) is the primary supported browser
  - Firefox and Edge are supported with additional configuration

## Installation Steps

Follow these steps to install the Storydoc Test Automation Framework:

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/storydoc-automation.git
cd storydoc-automation
```

### 2. Set Up Python Virtual Environment

Creating a virtual environment is recommended to isolate dependencies:

#### For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Once your virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install the following main dependencies:
- Selenium WebDriver (v4.10+) - Browser automation
- pytest (v7.3+) - Testing framework
- pytest-html (v3.2+) - HTML report generation
- pytest-xdist (v3.3+) - Parallel test execution
- requests (v2.31+) - HTTP client for API interactions
- webdriver-manager (v4.0+) - WebDriver binary management
- python-dotenv (v1.0+) - Environment variable management

### 4. Verify Installation

Verify that the installation was successful by running:

```bash
python -c "import selenium, pytest, requests; print('Selenium version:', selenium.__version__, '\npytest version:', pytest.__version__, '\nrequests version:', requests.__version__)"
```

You should see the versions of the installed packages.

## Environment Configuration

The framework uses environment variables for configuration. These can be set through a `.env` file or directly in your environment.

### 1. Create `.env` File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with appropriate values:

```
# Application Settings
BASE_URL=https://editor-staging.storydoc.com
DEFAULT_TIMEOUT=10
HEADLESS_MODE=false

# Test Data
TEST_EMAIL_DOMAIN=mailinator.com
TEST_PASSWORD=TestPassword123
TEST_USER_NAME=Test User

# Mailinator Settings
MAILINATOR_API_KEY=your_api_key_here  # Optional but recommended
MAILINATOR_INBOX_CHECK_TIMEOUT=60
MAILINATOR_POLLING_INTERVAL=5

# Reporting
SCREENSHOT_DIR=screenshots
REPORT_DIR=reports/html
LOG_LEVEL=INFO
```

### 3. Environment-Specific Configuration

For different environments (local, CI/CD, etc.), you can create specific environment files:

- `.env.local` - Local development settings
- `.env.ci` - CI/CD environment settings

Load a specific environment file using:

```bash
# For Linux/macOS
export $(cat .env.local | xargs)

# For Windows PowerShell
Get-Content .env.local | ForEach-Object { if ($_ -match '^[^#]') { $var = $_.Split('=', 2); $key=$var[0]; $value=$var[1]; [Environment]::SetEnvironmentVariable($key, $value) } }
```

## WebDriver Setup

The framework uses Selenium WebDriver for browser automation. The webdriver-manager package handles driver binary management automatically.

### Automatic WebDriver Management

By default, the framework uses `webdriver-manager` to automatically download and manage the appropriate WebDriver binaries:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

No manual setup is needed with this approach.

### Manual WebDriver Configuration (Alternative)

If you prefer manual control or need to use a specific driver version:

1. **Chrome WebDriver**:
   - Download ChromeDriver from [ChromeDriver downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads)
   - Ensure the version matches your Chrome browser version
   - Add the driver to your PATH or specify the path in your code

2. **Firefox WebDriver**:
   - Download GeckoDriver from [GeckoDriver releases](https://github.com/mozilla/geckodriver/releases)
   - Add to your PATH or specify the path in your code

3. **Edge WebDriver**:
   - Download Edge WebDriver from [Edge WebDriver downloads](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
   - Add to your PATH or specify the path in your code

### Configuring Browser Options

#### Headless Mode

For CI/CD environments or when you don't need the browser UI, use headless mode:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

Set `HEADLESS_MODE=true` in your `.env` file to enable headless mode by default.

#### Other Browser Configurations

Additional useful options:

```python
options = webdriver.ChromeOptions()
# Disable extensions
options.add_argument('--disable-extensions')
# Disable popup blocking
options.add_argument('--disable-popup-blocking')
# Disable sandbox (useful in Docker)
options.add_argument('--no-sandbox')
# Disable shared memory usage (useful in CI environments)
options.add_argument('--disable-dev-shm-usage')
```

## Running Tests

The framework uses pytest for test execution. Here are common commands for running tests:

### Running All Tests

```bash
pytest
```

### Running Specific Tests

```bash
# Run tests in a specific file
pytest tests/test_user_registration.py

# Run a specific test
pytest tests/test_user_registration.py::test_valid_user_registration

# Run tests matching a pattern
pytest -k "registration or authentication"
```

### Running Tests in Parallel

To speed up test execution, use pytest-xdist for parallel execution:

```bash
# Run tests with 4 parallel processes
pytest -n 4
```

### Generating Reports

Generate HTML reports for better visualization of test results:

```bash
# Basic HTML report
pytest --html=reports/report.html

# Self-contained HTML report (includes CSS/JS)
pytest --html=reports/report.html --self-contained-html
```

Reports will be generated in the specified location with details of test execution, including:
- Test results (pass/fail)
- Test duration
- Error messages for failures
- Screenshots for failed tests (if configured)

### Test Configuration

You can customize test behavior using a `pytest.ini` file:

```ini
[pytest]
# Default command line options
addopts = -v --html=reports/report.html --self-contained-html

# Define custom markers
markers =
    smoke: Run smoke tests only
    regression: Run regression tests
    slow: Tests that take longer to run

# Set base directory for test discovery
testpaths = tests

# Set timeout for test functions
timeout = 300
```

### Running Tests by Tags/Markers

```bash
# Run only smoke tests
pytest -m smoke

# Skip slow tests
pytest -m "not slow"
```

## Using Helper Scripts

The framework includes several helper scripts to simplify common operations.

### Running Script for Basic Test Execution

Create a `run_tests.sh` (Linux/macOS) or `run_tests.bat` (Windows) script for common test scenarios:

#### For Linux/macOS:

```bash
#!/bin/bash
# run_tests.sh

# Activate virtual environment
source venv/bin/activate

# Run tests based on argument
case "$1" in
  smoke)
    echo "Running smoke tests..."
    pytest -m smoke --html=reports/smoke_report.html
    ;;
  regression)
    echo "Running regression tests..."
    pytest -m regression --html=reports/regression_report.html
    ;;
  all)
    echo "Running all tests..."
    pytest --html=reports/full_report.html
    ;;
  *)
    echo "Please specify a test suite: smoke, regression, or all"
    exit 1
    ;;
esac
```

Make the script executable:

```bash
chmod +x run_tests.sh
```

#### For Windows:

```batch
@echo off
REM run_tests.bat

REM Activate virtual environment
call venv\Scripts\activate

REM Run tests based on argument
if "%1"=="smoke" (
  echo Running smoke tests...
  pytest -m smoke --html=reports/smoke_report.html
) else if "%1"=="regression" (
  echo Running regression tests...
  pytest -m regression --html=reports/regression_report.html
) else if "%1"=="all" (
  echo Running all tests...
  pytest --html=reports/full_report.html
) else (
  echo Please specify a test suite: smoke, regression, or all
  exit /b 1
)
```

### Data Generation Scripts

The framework may include scripts for generating test data:

```bash
# Generate test users
python utilities/generate_test_data.py users 10

# Clean up test data
python utilities/cleanup_test_data.py
```

## Troubleshooting

For a comprehensive list of common issues and troubleshooting steps, please refer to the [Troubleshooting Guide](troubleshooting.md).

### Common Issues

#### Python Environment Issues

- **Issue**: ImportError or ModuleNotFoundError
  **Solution**: Verify that your virtual environment is activated and all dependencies are installed.
  
  ```bash
  # Activate virtual environment
  source venv/bin/activate  # Linux/macOS
  venv\Scripts\activate     # Windows
  
  # Reinstall dependencies
  pip install -r requirements.txt
  ```

#### WebDriver Issues

- **Issue**: WebDriver executable not found
  **Solution**: Ensure webdriver-manager is installed and working correctly.
  
  ```bash
  pip install --upgrade webdriver-manager
  ```

- **Issue**: Browser version incompatibility
  **Solution**: Update your browser to the latest version, or specify the correct driver version.

#### Test Execution Issues

- **Issue**: Tests are running slowly
  **Solution**: Use headless mode and parallel execution.
  
  ```bash
  pytest -n 4 --headless=true
  ```

- **Issue**: Element not found errors
  **Solution**: Check if the application structure has changed. Update locators if necessary.

#### Mailinator Integration Issues

- **Issue**: Email verification timeouts
  **Solution**: Increase the email timeout value in your environment configuration.
  
  ```
  MAILINATOR_INBOX_CHECK_TIMEOUT=120  # Increase to 120 seconds
  ```

For more detailed troubleshooting, please consult the [Troubleshooting Guide](troubleshooting.md).

## Additional Resources

- [Framework Overview](framework_overview.md) - Comprehensive overview of the framework architecture and components
- [Mailinator Integration](mailinator_integration.md) - Details about email verification setup and usage
- [Troubleshooting Guide](troubleshooting.md) - Detailed guide for resolving common issues

### External Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [pytest Documentation](https://docs.pytest.org/)
- [Mailinator API Documentation](https://www.mailinator.com/v3/index.jsp#/api)

## Support

If you encounter issues not covered in this guide or the troubleshooting documentation, please:

1. Check existing GitHub issues to see if the problem has been reported
2. Create a new issue with detailed reproduction steps if needed
3. Contact the framework maintainers for urgent support

Happy testing!