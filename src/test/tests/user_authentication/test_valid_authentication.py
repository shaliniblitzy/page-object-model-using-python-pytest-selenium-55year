import pytest  # pytest 7.3+
import time  # standard library

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.browser_fixtures import chrome_browser  # src/test/fixtures/browser_fixtures.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_equal  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_url_contains  # src/test/utilities/assertion_helper.py
from src.test.fixtures.user_fixtures import registered_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.user_fixtures import authenticate_user  # src/test/fixtures/user_fixtures.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.config.timeout_config import USER_AUTHENTICATION_TIMEOUT  # src/test/config/timeout_config.py

DASHBOARD_URL_IDENTIFIER = "dashboard"


def setup_signin_page(browser):
    """Initialize and navigate to the signin page

    Args:
        browser (webdriver.WebDriver): browser

    Returns:
        SigninPage: Initialized signin page object
    """
    try:
        log_info("Starting signin page setup")
        signin_page = SigninPage(browser)
        signin_page.navigate_to()
        return signin_page
    except Exception as e:
        log_info(f"Exception during setup_signin_page: {e}")
        raise


@pytest.mark.authentication
@pytest.mark.positive
class TestValidAuthentication:
    """Test class for validating successful user authentication scenarios"""

    def __init__(self):
        """Initialize the test class"""
        pass

    def test_valid_credentials(self, browser, registered_user):
        """Test successful signin with valid credentials

        Args:
            browser (webdriver.WebDriver): browser
            registered_user (dict): registered_user
        """
        log_info("Starting test for valid credentials")
        signin_page = setup_signin_page(browser)
        email = registered_user["email"]
        password = registered_user["password"]
        signin_page.enter_email(email)
        signin_page.enter_password(password)
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_successful(), "Signin was not successful")
        assert_url_contains(browser, DASHBOARD_URL_IDENTIFIER, "Dashboard URL is incorrect")

    def test_remember_me_functionality(self, browser, registered_user):
        """Test signin with 'Remember Me' option enabled

        Args:
            browser (webdriver.WebDriver): browser
            registered_user (dict): registered_user
        """
        log_info("Starting test for remember me functionality")
        signin_page = setup_signin_page(browser)
        email = registered_user["email"]
        password = registered_user["password"]
        signin_page.enter_email(email)
        signin_page.enter_password(password)
        signin_page.check_remember_me()
        signin_page.click_signin_button()
        assert_true(signin_page.is_signin_successful(), "Signin was not successful")
        browser.quit()
        chrome_browser = setup_signin_page(browser)
        chrome_browser.navigate_to()
        assert_true(chrome_browser.is_signin_successful(), "User is not still authenticated")

    def test_complete_signin_method(self, browser, registered_user):
        """Test the complete_signin method of SigninPage

        Args:
            browser (webdriver.WebDriver): browser
            registered_user (dict): registered_user
        """
        log_info("Starting test for complete signin method")
        signin_page = setup_signin_page(browser)
        email = registered_user["email"]
        password = registered_user["password"]
        success = signin_page.complete_signin(email, password, remember_me=False)
        assert_true(success, "complete_signin method failed")
        assert_true(DashboardPage(browser).is_loaded(), "Dashboard is not loaded")

    def test_authenticate_user_helper(self, browser, registered_user):
        """Test the authenticate_user helper function

        Args:
            browser (webdriver.WebDriver): browser
            registered_user (dict): registered_user
        """
        log_info("Starting test for authenticate user helper")
        success = authenticate_user(browser, registered_user)
        assert_true(success, "authenticate_user helper failed")
        assert_true(DashboardPage(browser).is_loaded(), "Dashboard is not loaded")

    @pytest.mark.performance
    def test_signin_performance(self, browser, registered_user):
        """Test signin performance meets SLA requirements

        Args:
            browser (webdriver.WebDriver): browser
            registered_user (dict): registered_user
        """
        log_info("Starting test for signin performance")
        signin_page = setup_signin_page(browser)
        email = registered_user["email"]
        password = registered_user["password"]
        start_time = time.time()
        signin_page.complete_signin(email, password)
        end_time = time.time()
        duration = end_time - start_time
        assert duration < 2, "Signin completed within SLA timeout"
        assert_true(signin_page.is_signin_successful(), "Signin was not successful")
        log_info(f"Signin completed in {duration} seconds")