import pytest  # pytest 7.3+
import json  # standard library
import os  # standard library

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.utilities.assertion_helper import assert_true, assert_false, assert_equal  # src/test/utilities/assertion_helper.py
from src.test.fixtures.user_fixtures import test_user, registered_user  # src/test/fixtures/user_fixtures.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py

# Define global constants for file paths
INVALID_CREDENTIALS_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'invalid_data.json')
USER_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'user_data.json')


def load_test_data(file_path: str) -> dict:
    """Load test data from the specified JSON file

    Args:
        file_path (str): Path to the JSON file

    Returns:
        dict: Test data loaded from JSON file
    """
    log_info(f"Loading test data from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        log_info(f"Error loading test data from {file_path}: {e}")
        return {}


def setup_signin_page(browser) -> SigninPage:
    """Initialize and navigate to the signin page

    Args:
        browser (webdriver.WebDriver): WebDriver instance

    Returns:
        SigninPage: Initialized signin page object
    """
    log_info("Starting signin page setup")
    try:
        signin_page = SigninPage(browser)
        signin_page.navigate_to()
        return signin_page
    except Exception as e:
        log_info(f"Exception during signin page setup: {e}")
        return None


class TestInvalidCredentials:
    """Test class for negative user authentication scenarios with invalid credentials"""

    def setup_method(self):
        """Set up test environment before each test method"""
        log_info("Starting test setup")
        self.invalid_credentials_data = load_test_data(INVALID_CREDENTIALS_DATA_FILE)
        self.user_data = load_test_data(USER_DATA_FILE)
        log_info("Completed test setup")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_empty_credentials(self, browser):
        """Test signin with empty email and password

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for empty credentials")
        signin_page = setup_signin_page(browser)
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("required" in signin_page.get_error_message(), "Error message does not contain 'required'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with empty credentials")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_empty_email(self, browser):
        """Test signin with empty email and valid password

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for empty email")
        signin_page = setup_signin_page(browser)
        signin_page.enter_password("Test@123")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("required" in signin_page.get_error_message(), "Error message does not contain 'required'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with empty email")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_empty_password(self, browser):
        """Test signin with valid email and empty password

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for empty password")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email("test@example.com")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("required" in signin_page.get_error_message(), "Error message does not contain 'required'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with empty password")

    @pytest.mark.authentication
    @pytest.mark.negative
    @pytest.mark.parametrize("invalid_email", ['plainaddress', 'email@domain', '@domain.com', 'email@domain..com'])
    def test_invalid_email_format(self, browser, invalid_email):
        """Test signin with invalid email format and valid password

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for invalid email format")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email(invalid_email)
        signin_page.enter_password("Test@123")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("valid" in signin_page.get_error_message(), "Error message does not contain 'valid'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with invalid email format")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_nonexistent_user(self, browser):
        """Test signin with well-formed but nonexistent user email

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for nonexistent user")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email("nonexistent@example.com")
        signin_page.enter_password("Test@123")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("Invalid" in signin_page.get_error_message(), "Error message does not contain 'Invalid'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with nonexistent user")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_invalid_password(self, browser, registered_user):
        """Test signin with valid email and incorrect password

        Args:
            browser (webdriver.WebDriver): WebDriver instance
            registered_user (dict): Registered user data
        """
        log_info("Starting test for invalid password")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email(registered_user['email'])
        signin_page.enter_password("WrongPassword")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_true("Invalid" in signin_page.get_error_message(), "Error message does not contain 'Invalid'")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with invalid password")

    @pytest.mark.authentication
    @pytest.mark.negative
    def test_multiple_failed_attempts(self, browser, registered_user):
        """Test behavior after multiple failed signin attempts

        Args:
            browser (webdriver.WebDriver): WebDriver instance
            registered_user (dict): Registered user data
        """
        log_info("Starting test for multiple failed attempts")
        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = "WrongPassword"
        for i in range(3):
            signin_page.enter_email(email)
            signin_page.enter_password(password)
            signin_page.click_signin_button()
            assert_true(signin_page.is_signin_error_displayed(), f"Signin error is not displayed on attempt {i+1}")
            assert_true("Invalid" in signin_page.get_error_message(), f"Error message does not contain 'Invalid' on attempt {i+1}")
        assert_false(signin_page.is_signin_successful(), "Signin was successful after multiple failed attempts")

    @pytest.mark.authentication
    @pytest.mark.negative
    @pytest.mark.security
    def test_sql_injection_attempt(self, browser):
        """Test signin form resilience against SQL injection attempts

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for SQL injection attempt")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email("test@example.com' OR '1'='1")
        signin_page.enter_password("password' OR '1'='1")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with SQL injection")
        # Add additional assertions to check for unexpected behavior

    @pytest.mark.authentication
    @pytest.mark.negative
    @pytest.mark.security
    def test_xss_attempt(self, browser):
        """Test signin form resilience against XSS attempts

        Args:
            browser (webdriver.WebDriver): WebDriver instance
        """
        log_info("Starting test for XSS attempt")
        signin_page = setup_signin_page(browser)
        signin_page.enter_email("<script>alert('XSS')</script>@example.com")
        signin_page.enter_password("password")
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_error_displayed(), "Signin error is not displayed")
        assert_false(signin_page.is_signin_successful(), "Signin was successful with XSS")
        # Add assertions to check that no JavaScript execution occurred