import pytest  # pytest 7.3+
import os  # standard library
import json  # standard library

from src.test.pages.signin_page import SigninPage  # Page object for interacting with the signin page
from src.test.fixtures.browser_fixtures import browser  # Pytest fixture for browser setup and teardown
from src.test.utilities.assertion_helper import assert_true, assert_false, assert_equal, assert_element_visible  # Enhanced assertion with detailed error reporting
from src.test.utilities.test_data_generator import generate_unique_email  # Generate unique email addresses for testing
from src.test.utilities.screenshot_manager import ScreenshotManager  # Capture screenshots on test failures

# Define the path to the invalid data JSON file
INVALID_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'invalid_data.json')

# Initialize ScreenshotManager
screenshot_manager = ScreenshotManager()

def load_invalid_data():
    """
    Load invalid test data from the invalid_data.json file
    
    Returns:
        dict: Dictionary containing invalid test data for authentication tests
    """
    try:
        # Open the JSON file in read mode
        with open(INVALID_DATA_FILE, 'r') as file:
            # Load the JSON data
            data = json.load(file)
            # Return the authentication section of the data
            return data['authentication']
    except FileNotFoundError:
        print(f"Error: The file {INVALID_DATA_FILE} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file {INVALID_DATA_FILE} contains invalid JSON.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

@pytest.mark.authentication
@pytest.mark.error
def test_empty_credentials(browser):
    """
    Test authentication with empty email and password fields
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Click signin button without entering any credentials
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions required fields
        error_message = signin_page.get_error_message()
        assert_true("Email is required" in error_message or "Password is required" in error_message, "Error message should mention required fields")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_empty_credentials")
        raise e

@pytest.mark.authentication
@pytest.mark.error
def test_empty_email(browser):
    """
    Test authentication with empty email field
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter a valid password
    signin_page.enter_password("Test@123")
    
    # Leave the email field empty
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions email is required
        error_message = signin_page.get_error_message()
        assert_true("Email is required" in error_message, "Error message should mention email is required")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_empty_email")
        raise e

@pytest.mark.authentication
@pytest.mark.error
def test_empty_password(browser):
    """
    Test authentication with empty password field
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter a valid email
    signin_page.enter_email("test@mailinator.com")
    
    # Leave the password field empty
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions password is required
        error_message = signin_page.get_error_message()
        assert_true("Password is required" in error_message, "Error message should mention password is required")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_empty_password")
        raise e

@pytest.mark.authentication
@pytest.mark.error
@pytest.mark.parametrize("invalid_email", ['plainaddress', 'email@domain', '@domain.com', 'email@domain..com'])
def test_invalid_email_format(browser, invalid_email):
    """
    Test authentication with invalid email format
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
        invalid_email (str): Invalid email address from the parametrize decorator
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter the invalid email
    signin_page.enter_email(invalid_email)
    
    # Enter a valid password
    signin_page.enter_password("Test@123")
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions invalid email format
        error_message = signin_page.get_error_message()
        assert_true("Invalid email format" in error_message, "Error message should mention invalid email format")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_invalid_email_format")
        raise e

@pytest.mark.authentication
@pytest.mark.error
def test_nonexistent_user(browser):
    """
    Test authentication with email that doesn't exist in the system
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Generate a unique nonexistent email
    nonexistent_email = generate_unique_email()
    
    # Enter the nonexistent email
    signin_page.enter_email(nonexistent_email)
    
    # Enter a valid password
    signin_page.enter_password("Test@123")
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions invalid credentials
        error_message = signin_page.get_error_message()
        assert_true("Invalid credentials" in error_message, "Error message should mention invalid credentials")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_nonexistent_user")
        raise e

@pytest.mark.authentication
@pytest.mark.error
def test_incorrect_password(browser):
    """
    Test authentication with correct email but incorrect password
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter a known valid email
    signin_page.enter_email("test@mailinator.com")
    
    # Enter an incorrect password
    signin_page.enter_password("WrongPassword123")
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that the error message mentions invalid credentials
        error_message = signin_page.get_error_message()
        assert_true("Invalid credentials" in error_message, "Error message should mention invalid credentials")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_incorrect_password")
        raise e

@pytest.mark.authentication
@pytest.mark.security
@pytest.mark.error
def test_sql_injection_attempt(browser):
    """
    Test authentication with SQL injection attempt in credentials
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter email with SQL injection pattern
    signin_page.enter_email("user@example.com' OR '1'='1")
    
    # Enter password with SQL injection pattern
    signin_page.enter_password("password' OR '1'='1")
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that authentication failed (not redirected to dashboard)
        assert_false(signin_page.is_signin_successful(), "Authentication should fail")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_sql_injection_attempt")
        raise e

@pytest.mark.authentication
@pytest.mark.security
@pytest.mark.error
def test_xss_attempt(browser):
    """
    Test authentication with XSS attempt in credentials
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter email with XSS script pattern
    signin_page.enter_email("<script>alert('XSS')</script>@mailinator.com")
    
    # Enter password with XSS script pattern
    signin_page.enter_password("<script>alert('XSS')</script>")
    
    # Click signin button
    signin_page.click_signin_button()
    
    try:
        # Assert that an error message is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that no JavaScript execution occurred
        # (This is difficult to verify directly with Selenium, so we'll just check that authentication failed)
        assert_false(signin_page.is_signin_successful(), "Authentication should fail")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_xss_attempt")
        raise e

@pytest.mark.authentication
@pytest.mark.security
@pytest.mark.error
def test_excessive_login_attempts(browser):
    """
    Test authentication behavior after multiple failed login attempts
    
    Args:
        browser (webdriver): WebDriver instance provided by the browser fixture
    """
    # Initialize SigninPage with browser fixture
    signin_page = SigninPage(browser)
    
    # Navigate to the signin page
    signin_page.navigate_to()
    
    # Enter a valid email format but with incorrect password
    signin_page.enter_email("test@mailinator.com")
    
    # Attempt to login multiple times
    for i in range(5):
        signin_page.enter_password("WrongPassword123")
        signin_page.click_signin_button()
    
    try:
        # Assert that an appropriate message about excessive attempts is displayed
        assert_true(signin_page.is_signin_error_displayed(), "Error message should be displayed")
        
        # Assert that authentication is throttled or account is temporarily locked
        error_message = signin_page.get_error_message()
        assert_true("Too many failed attempts" in error_message or "Account locked" in error_message, "Error message should mention excessive attempts")
    except AssertionError as e:
        screenshot_manager.capture_failure_screenshot(browser, "test_excessive_login_attempts")
        raise e