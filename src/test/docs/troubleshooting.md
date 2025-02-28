# Storydoc Test Automation Framework - Troubleshooting Guide

This comprehensive troubleshooting guide provides solutions for common issues you may encounter while working with the Storydoc test automation framework. The guide includes debugging techniques, environment-specific guidance, and best practices for resolving problems.

## Table of Contents

1. [Common Issues and Solutions](#common-issues-and-solutions)
2. [Environment Setup Issues](#environment-setup-issues)
3. [WebDriver and Browser Issues](#webdriver-and-browser-issues)
4. [Element Locator Issues](#element-locator-issues)
5. [Email Verification Issues](#email-verification-issues)
6. [Test Execution Issues](#test-execution-issues)
7. [CI/CD Integration Issues](#cicd-integration-issues)
8. [Performance Issues](#performance-issues)
9. [Debugging Techniques](#debugging-techniques)
10. [Logging and Reporting Issues](#logging-and-reporting-issues)
11. [FAQ](#faq)

## Common Issues and Solutions

### Element Not Found Exceptions

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| `ElementNotVisibleException` | Element is in DOM but not visible | Use `wait_for_element_to_be_visible` method instead of just finding the element |
| `NoSuchElementException` | Element does not exist in DOM or locator is incorrect | Verify locator accuracy, increase wait timeout, check if element is in an iframe |
| `StaleElementReferenceException` | Element was found but is no longer attached to DOM | Re-find the element before interaction, use explicit waits |

### Example Solution for StaleElementReferenceException

```python
# Instead of:
element = self.driver.find_element(By.ID, "my-element")
# ... some actions that might change the DOM ...
element.click()  # Might throw StaleElementReferenceException

# Do this:
def click_with_retry(self, locator, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            element = self.driver.find_element(*locator)
            element.click()
            return
        except StaleElementReferenceException:
            if attempt == max_attempts - 1:
                raise
            time.sleep(0.5)
```

### Timeouts and Synchronization Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| `TimeoutException` | Element did not appear within the wait time | Increase timeout duration, check if element is actually present in the application |
| Test runs too fast for application | Application needs time to process actions | Add appropriate waits for application state, not just element presence |
| Inconsistent test results | Race conditions or application performance variability | Implement robust waiting strategies, avoid fixed sleeps |

### Example of Proper Wait Strategy

```python
# Instead of:
time.sleep(5)  # Fixed sleep - either too long or too short

# Do this:
wait = WebDriverWait(self.driver, 10)
wait.until(EC.visibility_of_element_located((By.ID, "dynamic-element")))
wait.until(EC.element_to_be_clickable((By.ID, "dynamic-element")))
```

## Environment Setup Issues

### Python Environment

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Package version conflicts | Incompatible dependencies | Use virtual environments, specify exact versions in requirements.txt |
| ImportError or ModuleNotFoundError | Missing dependencies, incorrect installation | Verify all requirements are installed: `pip install -r requirements.txt` |
| Permission errors | Insufficient privileges | Use `sudo` on Linux/Mac or run as Administrator on Windows |

### Example requirements.txt with Specific Versions

```
selenium==4.10.0
pytest==7.3.1
pytest-html==3.2.0
pytest-xdist==3.3.1
requests==2.31.0
webdriver-manager==4.0.0
python-dotenv==1.0.0
```

### Environment Variables

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Missing environment variables | .env file not loaded or variables not set | Verify .env file exists and is being loaded, check for typos in variable names |
| Different behavior between environments | Environment-specific configurations | Create environment-specific .env files (.env.staging, .env.local) |

### Example .env File Configuration

```
# .env file
BASE_URL=https://editor-staging.storydoc.com
DEFAULT_TIMEOUT=10
HEADLESS_MODE=false
TEST_EMAIL_DOMAIN=mailinator.com
```

## WebDriver and Browser Issues

### WebDriver Initialization

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Unable to initialize WebDriver | Missing driver binary, incompatible versions | Use webdriver-manager to handle driver binaries automatically |
| Browser crashes or hangs | Memory issues, browser extensions | Use headless mode, disable extensions, increase memory allocation |
| WebDriver session not closing | Improper teardown | Ensure driver.quit() is called in teardown, use context managers |

### Example of Proper WebDriver Setup/Teardown

```python
from contextlib import contextmanager

@contextmanager
def managed_driver(browser_type="chrome", headless=False):
    driver = None
    try:
        driver = DriverFactory.get_driver(browser_type, headless)
        yield driver
    finally:
        if driver:
            driver.quit()

# Usage
with managed_driver(headless=True) as driver:
    # Test code here
    pass  # Driver will be automatically quit even if an exception occurs
```

### Browser-Specific Issues

| Browser | Common Issues | Solutions |
|---------|--------------|-----------|
| Chrome | DevTools listening error | Ignore DevTools error messages, they don't affect test execution |
| Firefox | Slow initialization | Add proper timeouts, consider using Chrome for faster execution |
| Edge | WebDriver compatibility | Ensure you're using the correct EdgeChromiumDriver version |
| Headless Chrome | Element not visible | Add window size configuration: `options.add_argument("--window-size=1920,1080")` |

## Element Locator Issues

### Locator Stability

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Locators frequently break | Application changes, dynamic IDs | Use more stable locators (CSS paths, XPaths with text), avoid generated IDs |
| XPath not working | Complex DOM structure | Use relative XPaths, CSS selectors, or data-* attributes if available |
| Multiple elements found | Non-specific locator | Refine locator to be more specific, or use find_elements and index |

### Locator Selection Best Practices

1. **Priority Order for Locators**:
   - ID (most preferred)
   - Data attributes (data-test-id, data-cy, etc.)
   - CSS Selectors
   - XPath (use as last resort)

2. **Example of Good vs Bad Locators**:

```python
# Bad: Brittle locator dependent on position
BAD_LOCATOR = (By.XPATH, "//div[3]/span[2]")

# Good: Stable locator using attributes
GOOD_LOCATOR = (By.CSS_SELECTOR, "[data-test-id='signup-button']")
# or
GOOD_LOCATOR = (By.XPATH, "//button[contains(text(), 'Sign up')]")
```

### Debugging Locators

To debug locator issues:

1. Use browser developer tools to verify your locator:
   ```javascript
   // In Chrome DevTools Console for CSS selectors
   document.querySelector("[data-test-id='signup-button']")
   
   // For XPath
   $x("//button[contains(text(), 'Sign up')]")
   ```

2. If the element is inside an iframe, switch to the iframe first:
   ```python
   driver.switch_to.frame(driver.find_element(By.ID, "iframe-id"))
   # Now find elements inside the iframe
   driver.switch_to.default_content()  # Switch back to main content
   ```

## Email Verification Issues

### Mailinator API Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Emails not found | Delayed delivery, incorrect inbox name | Increase timeout for email checks, verify email address format |
| API throttling | Too many requests | Implement exponential backoff, reduce request frequency |
| Authentication failures | Invalid or missing API key | Verify API key, check if free tier limitations apply |

### Example of Robust Email Verification with Backoff

```python
def wait_for_email_with_backoff(self, email_address, subject, max_attempts=5, initial_wait=5):
    """Wait for an email with exponential backoff strategy"""
    for attempt in range(max_attempts):
        try:
            inbox = self.get_inbox(email_address)
            for message in inbox.get("msgs", []):
                if subject.lower() in message.get("subject", "").lower():
                    return self.get_message(message.get("id"))
            
            # Email not found, wait with exponential backoff
            wait_time = initial_wait * (2 ** attempt)
            logging.info(f"Email not found, waiting {wait_time} seconds (attempt {attempt+1}/{max_attempts})")
            time.sleep(wait_time)
        except Exception as e:
            logging.error(f"Error checking email: {str(e)}")
            wait_time = initial_wait * (2 ** attempt)
            time.sleep(wait_time)
    
    logging.error(f"Email with subject '{subject}' not found after {max_attempts} attempts")
    return None
```

### Email Content Extraction Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Verification link not found | Email format changes, regex pattern issues | Update extraction pattern, log full email content for debugging |
| HTML parsing errors | Complex email format | Use Beautiful Soup for more robust HTML parsing |
| Email encoding issues | Special characters in email | Use proper encoding handling |

## Test Execution Issues

### Test Failures

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Intermittent failures | Race conditions, timing issues | Implement retry mechanism for flaky tests, improve wait strategies |
| Sequential dependency failures | Tests depending on previous test state | Make tests independent, implement proper setup/teardown |
| Failed assertions | Application behavior changes, incorrect expectations | Update assertions to match current application behavior |

### Example Test Retry Mechanism

```python
# In conftest.py
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    for attempt in range(3):  # Try up to 3 times
        reports = runtestprotocol(item, nextitem=nextitem)
        if all(report.outcome != 'failed' for report in reports):
            # Test passed, no need to retry
            return True
        if attempt < 2:  # Don't sleep after the last attempt
            time.sleep(1)  # Wait before retry
    return True
```

### Parallel Execution Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Test interference | Tests sharing resources | Ensure tests use unique data, implement proper isolation |
| Resource exhaustion | Too many parallel browsers | Limit parallel execution based on available resources |
| Random failures in parallel mode | Race conditions | Mark flaky tests to run sequentially |

### Example pytest.ini Configuration for Parallel Execution

```ini
[pytest]
addopts = -v --html=reports/report.html --self-contained-html -n 4
markers =
    sequential: marks tests that should not be run in parallel
    flaky: marks tests that are flaky and might need retries
```

## CI/CD Integration Issues

### GitHub Actions Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Tests pass locally but fail in CI | Environment differences | Make environment explicit, use Docker containers |
| Timeouts in CI | Resource limitations in CI | Increase timeouts for CI, optimize test performance |
| Authentication failures | Secrets not configured | Verify GitHub secrets are properly set |

### Example GitHub Actions Workflow

```yaml
name: Test Automation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      env:
        BASE_URL: ${{ secrets.BASE_URL }}
        MAILINATOR_API_KEY: ${{ secrets.MAILINATOR_API_KEY }}
      run: |
        pytest -v --html=reports/report.html
        
    - name: Upload test report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-report
        path: reports/
```

### Docker Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Container startup failures | Missing dependencies | Verify Dockerfile includes all required dependencies |
| Cannot connect to browser | Browser not configured for container | Use `--no-sandbox` option for Chrome in Docker |
| Volume mount issues | Incorrect paths | Use absolute paths for volume mounts |

### Example Dockerfile

```dockerfile
FROM python:3.9-slim

# Install browser dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    xvfb

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set up working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test code
COPY . .

# Run tests with Xvfb
CMD Xvfb :99 -screen 0 1920x1080x24 & \
    export DISPLAY=:99 && \
    pytest -v --html=reports/report.html
```

## Performance Issues

### Slow Test Execution

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Tests run too slowly | Inefficient waits, unnecessary browser restarts | Optimize wait strategies, reuse browser sessions |
| High resource usage | Multiple browser instances | Use headless mode, limit parallel execution |
| Slow test initialization | WebDriver setup overhead | Implement browser reuse where appropriate |

### Optimizing Test Performance

1. **Use Browser Reuse for Related Tests**:

```python
@pytest.fixture(scope="class")
def shared_browser():
    driver = DriverFactory.get_driver()
    yield driver
    driver.quit()

class TestUserWorkflows:
    def test_signup(self, shared_browser):
        # Test signup using shared_browser
        
    def test_login(self, shared_browser):
        # Test login using same browser instance
```

2. **Implement Smart Waiting**:

```python
def wait_until_ready(self, timeout=10):
    """Wait until page is fully loaded and ready."""
    WebDriverWait(self.driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    # Also wait for any loader to disappear
    try:
        WebDriverWait(self.driver, timeout).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-indicator"))
        )
    except TimeoutException:
        # No loader found, page might be ready already
        pass
```

## Debugging Techniques

### Interactive Debugging

When tests fail and you need to investigate:

1. **Add Breakpoints in IDE**:
   
   In VS Code, add a breakpoint and launch your test with the debugger.

2. **Use Python's pdb**:

   ```python
   import pdb; pdb.set_trace()  # Add this line where you want to pause execution
   ```

3. **Debug Mode for pytest**:

   ```bash
   pytest --pdb test_file.py
   ```

### Screenshot Capture

Automatically capture screenshots on test failures:

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        driver = None
        for fixture in item.funcargs.values():
            if hasattr(fixture, "get_screenshot_as_png"):
                driver = fixture
                break
            if hasattr(fixture, "driver") and hasattr(fixture.driver, "get_screenshot_as_png"):
                driver = fixture.driver
                break
                
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_name = f"failure-{item.name}-{timestamp}.png"
            screenshot_path = os.path.join("screenshots", screenshot_name)
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
```

### Driver and Browser State

To debug WebDriver state:

1. **Get Browser Console Logs**:

```python
def get_browser_logs(self):
    """Get browser console logs for debugging."""
    try:
        logs = self.driver.get_log('browser')
        for log in logs:
            print(f"Browser log: {log}")
        return logs
    except Exception as e:
        print(f"Could not get browser logs: {str(e)}")
        return []
```

2. **Capture Page Source**:

```python
def capture_page_source(self, filename=None):
    """Save current page HTML for debugging."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"page-source-{timestamp}.html"
    
    path = os.path.join("debug", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(self.driver.page_source)
    
    print(f"Page source saved to {path}")
    return path
```

## Logging and Reporting Issues

### Logging Configuration

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Missing logs | Logger not configured | Set up proper logging configuration |
| Too verbose logs | Log level too low | Adjust log level based on environment |
| Log file permissions | Write permission issues | Check directory permissions |

### Example Logging Configuration

```python
def configure_logging():
    """Configure logging for the test framework."""
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"test-run-{timestamp}.log")
    
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
```

### HTML Report Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Reports not generated | pytest-html plugin not installed | Verify pytest-html is installed |
| Missing screenshots in report | Screenshot paths not relative | Use relative paths in reports |
| Corrupted reports | Process terminated during report generation | Ensure tests complete properly |

### Example pytest-html Configuration for Better Reports

```python
# In conftest.py
def pytest_configure(config):
    """Configure pytest-html report."""
    # Create report directory
    os.makedirs("reports", exist_ok=True)
    
    # Add environment info to report
    config._metadata["Browser"] = os.getenv("BROWSER", "Chrome")
    config._metadata["Environment"] = os.getenv("TEST_ENV", "Staging")
    config._metadata["Base URL"] = os.getenv("BASE_URL", "https://editor-staging.storydoc.com")
    config._metadata["Python Version"] = sys.version
    
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    
    if report.when == "call":
        # Always add test duration
        report.extra = extra + [
            {"name": "duration", "value": f"{report.duration:.2f}s"}
        ]
        
        # Add screenshots to report for failures
        if report.failed:
            driver = get_driver_from_item(item)
            if driver:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                screenshot_name = f"failure-{item.name}-{timestamp}.png"
                screenshot_path = os.path.join("screenshots", screenshot_name)
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(screenshot_path)
                
                # Add screenshot to report
                report.extra = extra + [
                    {"name": "screenshot", "image": screenshot_path}
                ]
```

## FAQ

### General Questions

#### Q: How do I debug a test that works locally but fails in CI?
A: First, check environment differences like browser versions and screen resolution. Enable more verbose logging in CI. Consider running tests locally in a Docker container to simulate the CI environment.

#### Q: What should I do if tests become flaky after application changes?
A: Review the locators that might have changed. Use page screenshots to verify the application state. Update page objects to match the new application behavior. Consider setting a more adequate wait strategy.

#### Q: How can I speed up test execution?
A: Use headless browser mode, parallel test execution with pytest-xdist, and optimize wait strategies. Consider reusing browser sessions for related tests and implementing smart skipping of redundant setup steps.

### WebDriver Questions

#### Q: Why do I get "Chrome failed to start: crashed" error?
A: This often occurs in Docker or CI environments. Ensure you've added the `--no-sandbox` and `--disable-dev-shm-usage` options to Chrome. For Docker, make sure you have all the required dependencies installed.

```python
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

#### Q: How can I interact with browser alerts?
A: Use the WebDriver's alert handling methods:

```python
# Accept an alert
driver.switch_to.alert.accept()

# Dismiss an alert
driver.switch_to.alert.dismiss()

# Get alert text
alert_text = driver.switch_to.alert.text

# Enter text in prompt
driver.switch_to.alert.send_keys("text")
```

### Page Object Questions

#### Q: What's the best way to organize page objects for a large application?
A: Group related pages into modules. Create a base page with common functionality. Use composition to share components across pages. Consider a hierarchy that mirrors the application structure.

```
pages/
├── base_page.py
├── components/
│   ├── header.py
│   ├── footer.py
│   └── navigation.py
├── auth/
│   ├── login_page.py
│   └── signup_page.py
└── stories/
    ├── dashboard_page.py
    ├── editor_page.py
    └── share_dialog.py
```

#### Q: How should I handle dynamic content in page objects?
A: Implement waiting strategies specific to the dynamic content. Create helper methods that wait for specific states of the application. Use expected conditions to check for state changes.

```python
def wait_for_story_list_loaded(self):
    """Wait until the story list is fully loaded."""
    self.wait.until(
        EC.presence_of_element_located(self.locators.STORY_LIST)
    )
    # Also wait for loading indicator to disappear
    self.wait.until_not(
        EC.visibility_of_element_located(self.locators.LOADING_INDICATOR)
    )
    # And wait for at least one story item to appear
    self.wait.until(
        EC.presence_of_element_located(self.locators.STORY_ITEM)
    )
```

---

## Additional Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [pytest Documentation](https://docs.pytest.org/)
- [WebDriverManager Documentation](https://github.com/bonigarcia/webdrivermanager)
- [Mailinator API Documentation](https://www.mailinator.com/api.html)

---

*If you encounter an issue not covered in this guide, please report it by creating a GitHub issue with detailed reproduction steps and environment information.*