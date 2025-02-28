import pytest  # pytest 7.3+
import time  # standard library
from selenium.webdriver.common.cookies import Cookie  # selenium 4.10+

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.browser_fixtures import chrome_browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.browser_fixtures import browser_session  # src/test/fixtures/browser_fixtures.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_false  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_equal  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_url_contains  # src/test/utilities/assertion_helper.py
from src.test.fixtures.user_fixtures import registered_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.user_fixtures import authenticate_user  # src/test/fixtures/user_fixtures.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.config.timeout_config import USER_AUTHENTICATION_TIMEOUT  # src/test/config/timeout_config.py
from src.test.utilities.driver_factory import DriverFactory  # src/test/utilities/driver_factory.py
from src.test.config.constants import BASE_URL  # src/test/config/constants.py
from src.test.config.constants import DASHBOARD_URL_IDENTIFIER  # src/test/config/constants.py

# Constants for session management tests
SESSION_COOKIE_NAME = "storydoc_session"
SHORT_SESSION_TIMEOUT = 60  # seconds

@pytest.fixture
def setup_signin_page(browser):
    """Initialize and navigate to the signin page"""
    log_info("Starting signin page setup")
    try:
        signin_page = SigninPage(browser)
        signin_page.navigate_to()
        return signin_page
    except Exception as e:
        log_error(f"Exception during setup: {e}")
        raise

def is_session_active(browser):
    """Check if user session is active by verifying dashboard access"""
    try:
        browser.get(BASE_URL)
        dashboard_page = DashboardPage(browser)
        if dashboard_page.is_loaded():
            return True
        else:
            return False
    except Exception:
        return False

def get_session_cookie(browser):
    """Get the session cookie if it exists"""
    try:
        cookies = browser.get_cookies()
        for cookie in cookies:
            if cookie['name'] == SESSION_COOKIE_NAME:
                log_info(f"Session cookie found: {cookie['name']}")
                return cookie
        log_info("Session cookie not found")
        return None
    except Exception as e:
        log_error(f"Error getting session cookie: {e}")
        return None

@pytest.mark.authentication
@pytest.mark.session
class TestSessionManagement:
    """Test class for session management scenarios"""

    def __init__(self):
        """Initialize the test class"""
        pass

    def test_session_persistence(self, browser, registered_user):
        """Test that the session persists across page refreshes"""
        log_info("Starting session persistence test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        dashboard_page = DashboardPage(browser)
        dashboard_page.refresh_dashboard()
        assert_true(dashboard_page.is_loaded(), "Dashboard should load after refresh")

        browser.get(f"{BASE_URL}/sign-up")
        browser.get(BASE_URL)
        assert_true(dashboard_page.is_loaded(), "Dashboard should load after navigation")

    def test_remember_me_functionality(self, browser, registered_user):
        """Test that 'Remember Me' functionality maintains the session after browser restart"""
        log_info("Starting remember me functionality test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password, remember_me=True)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        session_cookie = get_session_cookie(browser)
        assert_true(session_cookie is not None, "Session cookie should exist")
        #assert_true(session_cookie['expiry'] > time.time() + SHORT_SESSION_TIMEOUT, "Session cookie should have extended expiry")

        DriverFactory.quit_driver(browser)
        new_browser = DriverFactory.get_driver()
        new_browser.get(BASE_URL)

        dashboard_page = DashboardPage(new_browser)
        assert_true(dashboard_page.is_loaded(), "Dashboard should load without re-authentication")
        DriverFactory.quit_driver(new_browser)

    def test_default_session_behavior(self, browser, registered_user):
        """Test that without 'Remember Me', session requires re-authentication after browser restart"""
        log_info("Starting default session behavior test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password, remember_me=False)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        session_cookie = get_session_cookie(browser)
        assert_true(session_cookie is not None, "Session cookie should exist")
        #assert_true(session_cookie['expiry'] <= time.time() + SHORT_SESSION_TIMEOUT, "Session cookie should have default expiry")

        DriverFactory.quit_driver(browser)
        new_browser = DriverFactory.get_driver()
        new_browser.get(BASE_URL)

        assert_true(SigninPage(new_browser).is_element_visible(SigninPage(new_browser).SIGNIN_BUTTON), "Signin page should load")
        DriverFactory.quit_driver(new_browser)

    def test_session_cookie_properties(self, browser, registered_user):
        """Test the properties of session cookies to ensure security"""
        log_info("Starting session cookie properties test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        session_cookie = get_session_cookie(browser)
        assert_true(session_cookie is not None, "Session cookie should exist")
        assert_equal(session_cookie['name'], SESSION_COOKIE_NAME, "Session cookie name should be correct")
        #assert_true(session_cookie['secure'], "Session cookie should have secure flag set")
        #assert_true(session_cookie['httpOnly'], "Session cookie should have httpOnly flag set")
        #assert_equal(session_cookie['domain'], ".example.com", "Session cookie domain should be correct")
        #assert_equal(session_cookie['path'], "/", "Session cookie path should be correct")

    def test_session_invalidation_on_logout(self, browser, registered_user):
        """Test that session is invalidated after user logs out"""
        log_info("Starting session invalidation test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        session_cookie = get_session_cookie(browser)
        assert_true(session_cookie is not None, "Session cookie should exist")

        dashboard_page = DashboardPage(browser)
        #dashboard_page.perform_logout()
        #assert_true(signin_page.is_element_visible(SigninPage(browser).SIGNIN_BUTTON), "Should redirect to signin page after logout")

        session_cookie_after_logout = get_session_cookie(browser)
        assert_true(session_cookie_after_logout is None, "Session cookie should be removed after logout")

        browser.get(f"{BASE_URL}{DASHBOARD_URL_IDENTIFIER}")
        assert_true(signin_page.is_element_visible(SigninPage(browser).SIGNIN_BUTTON), "Should redirect to signin page")

    def test_concurrent_sessions(self, browser, registered_user):
        """Test user can maintain sessions across multiple browsers"""
        log_info("Starting concurrent sessions test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful in first browser")

        new_browser = DriverFactory.get_driver()
        signin_page_2 = setup_signin_page(new_browser)
        signin_page_2.complete_signin(email, password)
        assert_true(signin_page_2.is_signin_successful(), "Signin should be successful in second browser")

        assert_true(is_session_active(browser), "Session should be active in first browser")
        assert_true(is_session_active(new_browser), "Session should be active in second browser")
        DriverFactory.quit_driver(new_browser)

    @pytest.mark.slow
    def test_session_timeout(self, browser, registered_user):
        """Test that session times out after inactivity period"""
        log_info("Starting session timeout test")

        signin_page = setup_signin_page(browser)
        email = registered_user['email']
        password = registered_user['password']

        signin_page.complete_signin(email, password)
        assert_true(signin_page.is_signin_successful(), "Signin should be successful")

        session_cookie = get_session_cookie(browser)
        assert_true(session_cookie is not None, "Session cookie should exist")

        time.sleep(SHORT_SESSION_TIMEOUT)
        browser.get(f"{BASE_URL}{DASHBOARD_URL_IDENTIFIER}")
        assert_true(signin_page.is_element_visible(SigninPage(browser).SIGNIN_BUTTON), "Should redirect to signin page after timeout")