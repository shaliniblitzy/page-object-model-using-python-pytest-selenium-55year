import pytest  # pytest version: latest
import time  # standard library
from selenium import webdriver  # selenium version: latest

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import test_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.user_fixtures import user_credentials  # src/test/fixtures/user_fixtures.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py


def test_signin_with_remember_me_checkbox(browser: webdriver.WebDriver, test_user: dict):
    """Test that signing in with Remember Me checkbox creates persistent authentication session

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        test_user (dict): Test user data
    """
    # Initialize SigninPage with the browser instance
    signin_page = SigninPage(browser)

    # Log test start information
    log_info("Starting test: signin with Remember Me checkbox")

    # Navigate to the signin page
    signin_page.navigate_to()

    # Enter user email from test_user
    signin_page.enter_email(test_user['email'])

    # Enter user password from test_user
    signin_page.enter_password(test_user['password'])

    # Check the Remember Me checkbox
    signin_page.check_remember_me()

    # Click the signin button
    signin_page.click_signin_button()

    # Verify signin is successful by checking dashboard loads
    assert signin_page.is_signin_successful(), "Signin failed"

    # Get browser cookies directly using WebDriver
    cookies = browser.get_cookies()

    # Assert that authentication cookie exists
    auth_cookie_found = False
    for cookie in cookies:
        if cookie['name'] == 'auth_token':  # Replace 'auth_token' with the actual cookie name
            auth_cookie_found = True
            # Assert that authentication cookie has an expiry date in the future
            assert cookie.get('expiry') is not None and cookie['expiry'] > time.time(), "Authentication cookie has no expiry or is in the past"
            break
    assert auth_cookie_found, "Authentication cookie not found"

    # Log test completion
    log_info("Test completed: signin with Remember Me checkbox")


def test_signin_without_remember_me_checkbox(browser: webdriver.WebDriver, test_user: dict):
    """Test that signing in without Remember Me checkbox creates session-only authentication

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        test_user (dict): Test user data
    """
    # Initialize SigninPage with the browser instance
    signin_page = SigninPage(browser)

    # Log test start information
    log_info("Starting test: signin without Remember Me checkbox")

    # Navigate to the signin page
    signin_page.navigate_to()

    # Enter user email from test_user
    signin_page.enter_email(test_user['email'])

    # Enter user password from test_user
    signin_page.enter_password(test_user['password'])

    # Ensure Remember Me checkbox is not checked (default state)
    # Assuming the checkbox is unchecked by default, no action needed

    # Click the signin button
    signin_page.click_signin_button()

    # Verify signin is successful by checking dashboard loads
    assert signin_page.is_signin_successful(), "Signin failed"

    # Get browser cookies directly using WebDriver
    cookies = browser.get_cookies()

    # Assert that authentication cookie exists
    auth_cookie_found = False
    for cookie in cookies:
        if cookie['name'] == 'auth_token':  # Replace 'auth_token' with the actual cookie name
            auth_cookie_found = True
            # Assert that authentication cookie doesn't have an expiry (or is session cookie)
            assert cookie.get('expiry') is None or cookie['expiry'] <= time.time(), "Authentication cookie has an expiry"
            break
    assert auth_cookie_found, "Authentication cookie not found"

    # Log test completion
    log_info("Test completed: signin without Remember Me checkbox")


def test_session_persistence_after_browser_restart(browser: webdriver.WebDriver, user_credentials: dict):
    """Test that authentication persists across browser sessions when Remember Me is checked

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_credentials (dict): User credentials
    """
    # Initialize SigninPage with the browser instance
    signin_page = SigninPage(browser)
    # Initialize DashboardPage with the browser instance
    dashboard_page = DashboardPage(browser)

    # Log test start information
    log_info("Starting test: session persistence after browser restart with Remember Me")

    # Complete signin with remember_me=True using user_credentials
    signin_page.complete_signin(user_credentials['email'], user_credentials['password'], remember_me=True)

    # Verify signin is successful
    assert signin_page.is_signin_successful(), "Signin failed"

    # Store browser cookies directly using WebDriver
    stored_cookies = browser.get_cookies()

    # Close the browser (simulating browser restart)
    browser.quit()

    # Create a new browser instance
    new_browser = webdriver.Chrome()  # Or any other browser you are using

    # Add stored cookies to the new browser
    new_browser.get(signin_page.url)  # Navigate to a page within the domain to set cookies
    for cookie in stored_cookies:
        new_browser.add_cookie(cookie)

    # Navigate to dashboard page directly
    new_browser.get(dashboard_page.url)

    # Assert that user is still authenticated (dashboard loads without signin)
    assert dashboard_page.is_loaded(), "User is not authenticated after browser restart"

    # Log test completion
    log_info("Test completed: session persistence after browser restart with Remember Me")

    new_browser.quit()


def test_session_expiry_without_remember_me(browser: webdriver.WebDriver, user_credentials: dict):
    """Test that authentication does not persist across browser sessions when Remember Me is not checked

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_credentials (dict): User credentials
    """
    # Initialize SigninPage with the browser instance
    signin_page = SigninPage(browser)
    # Initialize DashboardPage with the browser instance
    dashboard_page = DashboardPage(browser)

    # Log test start information
    log_info("Starting test: session expiry without Remember Me")

    # Complete signin with remember_me=False using user_credentials
    signin_page.complete_signin(user_credentials['email'], user_credentials['password'], remember_me=False)

    # Verify signin is successful
    assert signin_page.is_signin_successful(), "Signin failed"

    # Close the browser (simulating browser restart)
    browser.quit()

    # Create a new browser instance
    new_browser = webdriver.Chrome()  # Or any other browser you are using

    # Navigate to dashboard page directly
    new_browser.get(dashboard_page.url)

    # Assert that user is redirected to signin page (not authenticated)
    assert signin_page.is_signin_successful() is False, "User is still authenticated after browser restart"

    # Log test completion
    log_info("Test completed: session expiry without Remember Me")

    new_browser.quit()


@pytest.mark.skip(reason="Long-running test, run manually")
def test_remember_me_expiry_after_timeout(browser: webdriver.WebDriver, user_credentials: dict):
    """Test that Remember Me session expires after the configured timeout period

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_credentials (dict): User credentials
    """
    # Initialize SigninPage with the browser instance
    signin_page = SigninPage(browser)
    # Initialize DashboardPage with the browser instance
    dashboard_page = DashboardPage(browser)

    # Log test start information
    log_info("Starting test: Remember Me expiry after timeout")

    # Complete signin with remember_me=True using user_credentials
    signin_page.complete_signin(user_credentials['email'], user_credentials['password'], remember_me=True)

    # Verify signin is successful
    assert signin_page.is_signin_successful(), "Signin failed"

    # Get authentication cookie expiry time directly from browser
    expiry_time = None
    cookies = browser.get_cookies()
    for cookie in cookies:
        if cookie['name'] == 'auth_token':  # Replace 'auth_token' with the actual cookie name
            expiry_time = cookie.get('expiry')
            break

    assert expiry_time is not None, "Authentication cookie has no expiry"

    # Wait until just after cookie expiry time (conditionally skipped in CI environment)
    wait_time = expiry_time - time.time() + 5  # Add 5 seconds to ensure expiry
    if wait_time > 0:
        log_info(f"Waiting for {wait_time} seconds until session expires")
        time.sleep(wait_time)

    # Refresh the page
    browser.refresh()

    # Assert that user is redirected to signin page (session expired)
    assert signin_page.is_signin_successful() is False, "User is still authenticated after session expiry"

    # Log test completion
    log_info("Test completed: Remember Me expiry after timeout")