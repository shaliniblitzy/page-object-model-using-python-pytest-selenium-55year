import pytest  # pytest 7.3+
import time  # built-in

from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.pages.error_page import ErrorPage  # src/test/pages/error_page.py
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import user_credentials  # src/test/fixtures/user_fixtures.py
from src.test.config.urls import BASE_URL  # src/test/config/urls.py
from src/test/config/urls import DASHBOARD_PATH  # src/test/config/urls.py
from src/test/config/urls import STORY_EDITOR_PATH  # src/test/config/urls.py
from src/test/config/urls import get_dashboard_url  # src/test/config/urls.py
from src/test/config/urls import get_story_editor_url  # src/test/config/urls.py
from src/test/utilities/wait_helper import WaitUtils  # src/test/utilities/wait_helper.py


@pytest.mark.authentication
@pytest.mark.redirect
def test_redirect_to_dashboard_after_signin(browser, user_credentials):
    """Tests that the user is redirected to the dashboard page after successful sign in

    Args:
        browser (webdriver.WebDriver): The WebDriver instance.
        user_credentials (dict): A dictionary containing user credentials.
    """
    # Initialize SigninPage with browser instance
    signin_page = SigninPage(browser)

    # Navigate to signin page
    signin_page.navigate_to()

    # Enter email from user_credentials
    signin_page.enter_email(user_credentials[next(iter(user_credentials))]['email'])

    # Enter password from user_credentials
    signin_page.enter_password(user_credentials[next(iter(user_credentials))]['password'])

    # Click the signin button
    signin_page.click_signin_button()

    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)

    # Assert that dashboard page is loaded successfully
    assert dashboard_page.is_loaded(), "Dashboard page should be loaded after signin"

    # Verify that current URL contains dashboard path
    WaitUtils.wait_for_page_url_contains(browser, DASHBOARD_PATH)
    assert get_dashboard_url() == browser.current_url, "Should be redirected to dashboard URL"


@pytest.mark.authentication
@pytest.mark.redirect
def test_redirect_to_originally_requested_page(browser, user_credentials):
    """Tests that the user is redirected to the originally requested page after authentication

    Args:
        browser (webdriver.WebDriver): The WebDriver instance.
        user_credentials (dict): A dictionary containing user credentials.
    """
    # Get the story editor URL which requires authentication
    story_editor_url = get_story_editor_url()

    # Navigate directly to story editor URL without being authenticated
    browser.get(story_editor_url)

    # Verify that browser is redirected to signin page
    WaitUtils.wait_for_page_url_contains(browser, "/sign-in")
    assert "/sign-in" in browser.current_url, "Should be redirected to sign-in page"

    # Initialize SigninPage with browser instance
    signin_page = SigninPage(browser)

    # Enter email from user_credentials
    signin_page.enter_email(user_credentials[next(iter(user_credentials))]['email'])

    # Enter password from user_credentials
    signin_page.enter_password(user_credentials[next(iter(user_credentials))]['password'])

    # Click the signin button
    signin_page.click_signin_button()

    # Wait for redirection to complete
    WaitUtils.wait_for_page_url_contains(browser, STORY_EDITOR_PATH)

    # Verify that current URL contains story editor path
    assert STORY_EDITOR_PATH in browser.current_url, "Should be redirected to story editor URL"

    # Assert that story editor URL is the current URL
    assert story_editor_url == browser.current_url, "Should be redirected to story editor URL"


@pytest.mark.authentication
@pytest.mark.redirect
@pytest.mark.skip(reason="Session timeout simulation requires backend modification")
def test_redirect_to_signin_after_session_timeout(browser, user_credentials):
    """Tests that the user is redirected to signin page after session timeout

    Args:
        browser (webdriver.WebDriver): The WebDriver instance.
        user_credentials (dict): A dictionary containing user credentials.
    """
    # Initialize SigninPage with browser instance
    signin_page = SigninPage(browser)

    # Complete signin process with user_credentials
    signin_page.complete_signin(user_credentials[next(iter(user_credentials))]['email'], user_credentials[next(iter(user_credentials))]['password'])

    # Initialize DashboardPage and verify successful login
    dashboard_page = DashboardPage(browser)
    assert dashboard_page.is_loaded(), "Dashboard should load after signin"

    # Simulate session timeout (this would require backend support or cookie manipulation)
    # For example, you might try to clear cookies or manipulate session storage

    # Try to access a protected resource
    browser.get(get_dashboard_url())

    # Verify that browser is redirected to signin page
    WaitUtils.wait_for_page_url_contains(browser, "/sign-in")
    assert "/sign-in" in browser.current_url, "Should be redirected to sign-in page after session timeout"

    # Assert that current URL contains signin path
    assert "/sign-in" in browser.current_url, "Should be redirected to sign-in page after session timeout"


@pytest.mark.authentication
@pytest.mark.redirect
def test_redirect_with_return_url_parameter(browser, user_credentials):
    """Tests redirection with a return_url parameter preserving the original destination

    Args:
        browser (webdriver.WebDriver): The WebDriver instance.
        user_credentials (dict): A dictionary containing user credentials.
    """
    # Get the story editor URL as a target for redirection
    story_editor_url = get_story_editor_url()

    # Construct signin URL with return_url parameter pointing to story editor
    signin_url = f"{BASE_URL}/sign-in?return_url={story_editor_url}"

    # Navigate to constructed signin URL
    browser.get(signin_url)

    # Initialize SigninPage with browser instance
    signin_page = SigninPage(browser)

    # Enter email from user_credentials
    signin_page.enter_email(user_credentials[next(iter(user_credentials))]['email'])

    # Enter password from user_credentials
    signin_page.enter_password(user_credentials[next(iter(user_credentials))]['password'])

    # Click the signin button
    signin_page.click_signin_button()

    # Wait for redirection to complete
    WaitUtils.wait_for_page_url_contains(browser, STORY_EDITOR_PATH)

    # Verify that current URL contains story editor path
    assert STORY_EDITOR_PATH in browser.current_url, "Should be redirected to story editor URL"

    # Assert that story editor URL is the current URL
    assert story_editor_url == browser.current_url, "Should be redirected to story editor URL"