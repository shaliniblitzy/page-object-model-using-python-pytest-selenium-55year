# Storydoc Test Automation Best Practices

## Table of Contents

1. [Introduction](#introduction)
2. [Code Quality Standards](#code-quality-standards)
3. [Test Architecture](#test-architecture)
4. [Test Maintainability](#test-maintainability)
5. [Test Reliability](#test-reliability)
6. [Test Performance](#test-performance)
7. [Test Readability](#test-readability)
8. [Framework Extensions](#framework-extensions)
9. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
10. [Resources and References](#resources-and-references)

## Introduction

This guide provides comprehensive best practices for using and extending the Storydoc test automation framework. Following these guidelines will help ensure that your automated tests are maintainable, reliable, and efficient.

### Audience

- QA Engineers working on automating Storydoc application tests
- Developers contributing to the test automation framework
- Anyone reviewing or maintaining the existing test suite

### How to Use This Guide

Treat this document as a reference for standardizing your approach to test automation. When writing new tests or modifying existing ones, review the relevant sections to ensure your code adheres to the established best practices.

## Code Quality Standards

### PEP 8 Compliance

All Python code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines:

- Use 4 spaces for indentation (not tabs)
- Maximum line length of 79 characters
- Use appropriate naming conventions:
  - `snake_case` for functions, variables, and methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- Add whitespace appropriately:
  - Around operators: `x = 1 + 2`
  - After commas: `def func(a, b, c):`

Use `flake8` to check PEP 8 compliance:

```bash
flake8 src/test
```

### Type Hints

Use type hints to improve code readability and enable static type checking:

```python
def wait_for_element(locator: tuple[str, str], timeout: int = 10) -> WebElement:
    """Wait for element to be visible and return it."""
    return WebDriverWait(self.driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )
```

Use `mypy` to validate type hints:

```bash
mypy src/test
```

### Documentation Standards

Document all classes and methods using Google-style docstrings:

```python
def enter_email(self, email: str) -> None:
    """Enter email in the email input field.
    
    Args:
        email: Email address to enter
        
    Raises:
        TimeoutException: If email field is not visible within timeout
    """
    self.input_text(SignupLocators.EMAIL_FIELD, email)
```

Use `pydocstyle` to check docstring formatting:

```bash
pydocstyle src/test
```

### Code Formatting

Use `black` to maintain consistent code formatting:

```bash
black src/test
```

### Linting and Static Analysis

Configure pre-commit hooks to run all quality checks before committing:

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
```

## Test Architecture

### Page Object Model Implementation

Follow the Page Object Model (POM) pattern strictly:

1. Create a separate class for each page or component
2. Encapsulate all UI interactions within page objects
3. Keep locators separate from page interaction methods
4. Return new page objects when navigation occurs

Example page object structure:

```python
class SignupPage(BasePage):
    """Page object for the signup page."""
    
    def navigate_to(self) -> "SignupPage":
        """Navigate to the signup page."""
        self.driver.get(self.config.get_url("signup"))
        return self
    
    def enter_email(self, email: str) -> "SignupPage":
        """Enter email in the email field."""
        self.input_text(SignupLocators.EMAIL_FIELD, email)
        return self
    
    def complete_signup(self, email: str, password: str, name: str) -> DashboardPage:
        """Complete the entire signup process."""
        self.enter_email(email)
        self.enter_password(password)
        self.enter_name(name)
        self.check_terms()
        self.click_signup_button()
        return DashboardPage(self.driver)
```

### Test Organization

Organize tests by feature and follow a consistent directory structure:

```
src/test/
├── conftest.py                # pytest configuration
├── pages/                     # page objects
│   ├── base_page.py
│   ├── signup_page.py
│   └── ...
├── locators/                  # element locators
│   ├── base_locators.py
│   ├── signup_locators.py
│   └── ...
├── tests/                     # test cases
│   ├── test_signup.py
│   ├── test_signin.py
│   └── ...
├── utilities/                 # helper modules
│   ├── email_helper.py
│   ├── driver_factory.py
│   └── ...
└── data/                      # test data
    ├── test_users.json
    └── ...
```

### Test Data Management

Separate test data from test logic:

1. Store static test data in JSON files
2. Generate dynamic test data programmatically
3. Use fixtures to provide test data to test cases
4. Clean up test data after tests complete

```python
@pytest.fixture
def test_user():
    """Create test user data."""
    email = f"test.user.{int(time.time())}@mailinator.com"
    password = "Test@123"
    name = f"Test User {int(time.time())}"
    
    yield {
        "email": email,
        "password": password,
        "name": name
    }
```

## Test Maintainability

### Locator Management

Keep locators separate from page objects:

```python
# locators/signup_locators.py
from selenium.webdriver.common.by import By

class SignupLocators:
    """Locators for the signup page."""
    NAME_FIELD = (By.ID, "name")
    EMAIL_FIELD = (By.ID, "email")
    PASSWORD_FIELD = (By.ID, "password")
    TERMS_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
```

Prioritize locator strategies in this order:
1. ID (most stable)
2. Name
3. CSS selectors (simple)
4. XPath (only when necessary)

### Descriptive Naming

Use descriptive, intention-revealing names:

```python
# Avoid
def test_signup(self):
    # test code...

# Better
def test_user_can_register_with_valid_credentials(self):
    # test code...
```

### Creating Reusable Components

Extract common functionality into reusable methods:

```python
# Instead of repeating this pattern
self.driver.find_element(*SignupLocators.EMAIL_FIELD).clear()
self.driver.find_element(*SignupLocators.EMAIL_FIELD).send_keys(email)

# Create a reusable method in BasePage
def input_text(self, locator: tuple, text: str) -> None:
    """Clear and input text into an element."""
    element = self.wait_for_element(locator)
    element.clear()
    element.send_keys(text)
```

### Avoiding Hardcoded Values

Store configuration values in a central location:

```python
# Instead of
self.driver.get("https://editor-staging.storydoc.com/sign-up")

# Use a configuration manager
self.driver.get(self.config.get_url("signup"))
```

## Test Reliability

### Element Synchronization

Always use explicit waits instead of implicit waits or `sleep()`:

```python
# Avoid
time.sleep(5)
element = self.driver.find_element(*locator)

# Better
element = WebDriverWait(self.driver, 10).until(
    EC.visibility_of_element_located(locator)
)
```

Centralize wait logic in the base page:

```python
def wait_for_element(self, locator: tuple, timeout: int = 10) -> WebElement:
    """Wait for element to be visible and return it."""
    return WebDriverWait(self.driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )
```

### Retry Mechanisms

Implement retry for flaky operations:

```python
def click_with_retry(self, locator: tuple, retries: int = 3) -> None:
    """Click element with retry mechanism."""
    for attempt in range(retries):
        try:
            element = self.wait_for_element(locator)
            element.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException) as e:
            if attempt == retries - 1:
                raise e
            time.sleep(1)
```

Use pytest-rerunfailures to retry flaky tests:

```python
@pytest.mark.flaky(reruns=2)
def test_story_sharing():
    # Test code that might be flaky
```

### Error Handling

Implement appropriate exception handling:

```python
def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
    """Check if element is visible."""
    try:
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return True
    except TimeoutException:
        return False
```

### Screenshot Capture

Capture screenshots on test failures:

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshot_path = f"screenshots/failure_{item.name}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            allure.attach.file(
                screenshot_path,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
```

## Test Performance

### Browser Session Management

Minimize browser restarts:

```python
# Instead of creating a new driver for each test
@pytest.fixture(scope="function")
def driver():
    # Setup and teardown for each test

# Reuse driver where appropriate
@pytest.fixture(scope="class")
def driver():
    # Setup and teardown for the whole test class
```

### Headless Mode

Use headless mode for CI/CD execution:

```python
def get_driver(headless: bool = False):
    """Get WebDriver instance."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    # Configure additional options
    return webdriver.Chrome(options=options)
```

### Parallel Test Execution

Configure pytest-xdist for parallel execution:

```bash
# Run tests with 4 parallel processes
pytest -n 4 src/test
```

Ensure tests are designed to run in parallel:
- Avoid test interdependencies
- Use unique test data for each test
- Properly manage shared resources

### Resource Optimization

Minimize unnecessary browser operations:

```python
# Avoid multiple navigations
def test_inefficient(self, driver):
    driver.get("/page1")
    # Test page1
    driver.get("/page2")
    # Test page2

# Better: group tests by starting page
def test_page1(self, driver):
    driver.get("/page1")
    # Test page1
    
def test_page2(self, driver):
    driver.get("/page2")
    # Test page2
```

## Test Readability

### Consistent Naming Conventions

Follow consistent naming patterns:

- Test modules: `test_feature.py`
- Test classes: `TestFeature`
- Test methods: `test_specific_scenario_and_expected_outcome`
- Page objects: `FeaturePage`
- Locator classes: `FeatureLocators`

### Clear Docstrings

Document tests with clear docstrings:

```python
def test_user_can_register_with_valid_credentials(self, test_user):
    """
    Test that a user can successfully register with valid credentials.
    
    Steps:
    1. Navigate to signup page
    2. Fill in registration form with valid data
    3. Submit the form
    
    Expected:
    - User should be redirected to dashboard
    - Dashboard should display user's name
    """
    # Test implementation
```

### Arrange-Act-Assert Pattern

Structure tests using the Arrange-Act-Assert (AAA) pattern:

```python
def test_user_can_login(self, driver, test_user):
    # Arrange
    login_page = LoginPage(driver)
    login_page.navigate_to()
    
    # Act
    dashboard_page = login_page.login(
        test_user["email"], 
        test_user["password"]
    )
    
    # Assert
    assert dashboard_page.is_loaded()
    assert dashboard_page.get_user_name() == test_user["name"]
```

### Descriptive Assertions

Use descriptive assertions with custom messages:

```python
# Instead of
assert page.is_element_visible(locator)

# Use descriptive message
assert page.is_element_visible(locator), "The success message was not displayed after submission"
```

Consider using pytest-check for multiple soft assertions:

```python
from pytest_check import check

def test_dashboard_elements(self, dashboard_page):
    """Test all required elements are present on dashboard."""
    check.is_true(dashboard_page.is_element_visible(DashboardLocators.USER_MENU), 
                 "User menu is not visible")
    check.is_true(dashboard_page.is_element_visible(DashboardLocators.CREATE_BUTTON), 
                 "Create button is not visible")
    check.is_true(dashboard_page.is_element_visible(DashboardLocators.STORY_LIST), 
                 "Story list is not visible")
```

## Framework Extensions

### Adding New Page Objects

Follow these steps to add a new page object:

1. Create a new file in the `pages` directory
2. Create corresponding locators in the `locators` directory
3. Extend the `BasePage` class
4. Implement page-specific methods
5. Return appropriate page objects from navigation methods

```python
# pages/new_feature_page.py
from pages.base_page import BasePage
from locators.new_feature_locators import NewFeatureLocators

class NewFeaturePage(BasePage):
    """Page object for the new feature."""
    
    def navigate_to(self) -> "NewFeaturePage":
        """Navigate to the new feature page."""
        self.driver.get(self.config.get_url("new_feature"))
        return self
    
    def perform_action(self) -> "NewFeaturePage":
        """Perform a specific action on the page."""
        self.click(NewFeatureLocators.ACTION_BUTTON)
        return self
```

### Adding New Test Cases

Follow these steps to add new test cases:

1. Identify the feature to test
2. Create or update the test module in the `tests` directory
3. Define test methods following the AAA pattern
4. Use appropriate fixtures for setup and teardown
5. Add clear docstrings describing the test

```python
# tests/test_new_feature.py
import pytest
from pages.new_feature_page import NewFeaturePage

class TestNewFeature:
    """Test cases for the new feature."""
    
    @pytest.fixture(scope="function")
    def new_feature_page(self, driver):
        """Create and return a NewFeaturePage instance."""
        return NewFeaturePage(driver)
    
    def test_user_can_perform_action(self, new_feature_page):
        """Test that user can perform the action successfully."""
        # Arrange
        new_feature_page.navigate_to()
        
        # Act
        result_page = new_feature_page.perform_action()
        
        # Assert
        assert result_page.is_action_successful()
```

### Contributing to the Framework

When extending the framework core:

1. Identify reusable patterns across multiple page objects
2. Extract them to the base classes or utilities
3. Write comprehensive unit tests for new framework components
4. Update documentation to reflect changes
5. Follow the pull request process defined in the project

## Common Pitfalls and Solutions

### Timing Issues

**Problem**: Tests fail intermittently due to timing issues.

**Solutions**:
- Use explicit waits with appropriate conditions
- Implement retry mechanisms for flaky operations
- Adjust timeouts based on application performance
- Monitor and log timing metrics to identify slow operations

### Locator Fragility

**Problem**: Tests break when UI changes.

**Solutions**:
- Use stable locator strategies (IDs where possible)
- Maintain locators separately from page objects
- Use relative locators for elements without stable attributes
- Add descriptive comments for complex locators

### Test Data Management

**Problem**: Tests interfere with each other due to shared test data.

**Solutions**:
- Generate unique test data for each test run
- Clean up test data after each test
- Use test isolation patterns (separate users, separate stories)
- Implement database resets between test runs if needed

### Environment-Specific Issues

**Problem**: Tests pass in one environment but fail in another.

**Solutions**:
- Use configuration management for environment-specific values
- Implement environment detection and conditional logic
- Set appropriate timeouts for different environments
- Add environment information to test reports

## Resources and References

### Recommended Reading

- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/en/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)
- [Page Object Models (Martin Fowler)](https://martinfowler.com/bliki/PageObject.html)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)

### Useful Tools

- [pytest-html](https://github.com/pytest-dev/pytest-html): HTML report generation
- [pytest-xdist](https://github.com/pytest-dev/pytest-xdist): Parallel test execution
- [Allure Framework](https://github.com/allure-framework/allure2): Advanced reporting
- [Faker](https://github.com/joke2k/faker): Test data generation
- [pytest-check](https://github.com/okken/pytest-check): Multiple soft assertions

### Community Resources

- [Stack Overflow Selenium Topics](https://stackoverflow.com/questions/tagged/selenium)
- [Selenium User Group](https://groups.google.com/g/selenium-users)
- [Testing Conferences](https://testingconferences.org/)