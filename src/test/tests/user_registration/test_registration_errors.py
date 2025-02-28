import pytest  # pytest 7.3+
import time  # standard library
from typing import Dict  # standard library
from selenium.common.exceptions import TimeoutException  # selenium 4.10+

from src.test.fixtures.browser_fixtures import browser, take_screenshot_on_failure  # Internal import
from src.test.pages.signup_page import SignupPage  # Internal import
from src.test.pages.error_page import ErrorPage, ERROR_TYPES  # Internal import
from src.test.fixtures.user_fixtures import random_user_data  # Internal import
from src.test.utilities.random_data_generator import generate_random_email, generate_random_password, generate_random_name  # Internal import
from src.test.utilities.logger import log_info, log_error  # Internal import
from src.test.utilities.wait_helper import WaitUtils  # Internal import

ERROR_TIMEOUT = 10  # Timeout for error checks
NETWORK_DELAY = 2  # Delay for simulating network issues


@pytest.mark.errors
@pytest.mark.registration
def test_duplicate_email_error(browser):
    """Test that using an already registered email displays an appropriate error message"""
    log_info("Starting duplicate email error test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    test_user_data = random_user_data()
    signup_page.fill_signup_form(test_user_data['name'], test_user_data['email'], test_user_data['password'])
    signup_page.click_signup_button()

    assert signup_page.is_signup_successful(), "Registration was not successful"

    signup_page.navigate_to()

    signup_page.fill_signup_form(test_user_data['name'], test_user_data['email'], generate_random_password())
    signup_page.click_signup_button()

    assert error_page.is_specific_error_displayed('registration'), "Error message for duplicate email is not displayed"
    assert "email address is already registered" in error_page.get_error_message('registration').lower(), "Error does not contain expected text about email already being registered"


@pytest.mark.errors
@pytest.mark.registration
def test_server_error_handling(browser):
    """Test how the application handles server errors during registration"""
    log_info("Starting server error handling test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    test_user_data = random_user_data()

    # Simulate server error using browser devtools protocol
    browser.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 1000,  # Add some latency
        "downloadThroughput": 0,  # Simulate no download
        "uploadThroughput": 0,  # Simulate no upload
        "connectionType": "none"
    })

    signup_page.fill_signup_form(test_user_data['name'], test_user_data['email'], test_user_data['password'])
    signup_page.click_signup_button()

    assert error_page.is_specific_error_displayed('server'), "Server error message is not displayed"
    assert "server" in error_page.get_error_message('server').lower(), "Error does not contain expected text about server issues"

    # Reset network conditions
    browser.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 0,
        "downloadThroughput": 0,
        "uploadThroughput": 0,
        "connectionType": "none"
    })

    error_page.capture_error_screenshot('server')


@pytest.mark.errors
@pytest.mark.registration
def test_network_error_handling(browser):
    """Test how the application handles network errors during registration"""
    log_info("Starting network error handling test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    test_user_data = random_user_data()

    # Simulate network disconnection using browser devtools protocol
    browser.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": True,
        "latency": 0,
        "downloadThroughput": 0,
        "uploadThroughput": 0,
        "connectionType": "none"
    })

    signup_page.fill_signup_form(test_user_data['name'], test_user_data['email'], test_user_data['password'])
    signup_page.click_signup_button()

    assert error_page.is_specific_error_displayed('network'), "Network error message is not displayed"
    assert "connection" in error_page.get_error_message('network').lower(), "Error does not contain expected text about connection issues"

    # Reset network conditions
    browser.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 0,
        "downloadThroughput": 0,
        "uploadThroughput": 0,
        "connectionType": "none"
    })

    error_page.capture_error_screenshot('network')


@pytest.mark.errors
@pytest.mark.registration
def test_error_message_dismissal(browser):
    """Test that error messages can be dismissed properly"""
    log_info("Starting error dismissal test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    signup_page.enter_email("invalid-email")
    signup_page.click_signup_button()

    assert error_page.is_error_displayed(), "Error message is not displayed"

    error_page.dismiss_error()

    assert not error_page.is_error_displayed(), "Error message is still displayed after dismissal"


@pytest.mark.errors
@pytest.mark.registration
def test_form_resubmission_after_error(browser):
    """Test that form can be resubmitted after correcting errors"""
    log_info("Starting form resubmission test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    test_user_data = random_user_data()
    signup_page.enter_email("invalid-email")
    signup_page.enter_password(test_user_data['password'])
    signup_page.enter_name(test_user_data['name'])
    signup_page.accept_terms()
    signup_page.click_signup_button()

    assert error_page.is_error_displayed(), "Error message is not displayed"

    signup_page.enter_email(generate_random_email())
    signup_page.click_signup_button()

    assert signup_page.is_signup_successful(), "Registration is not successful after correcting email"


@pytest.mark.errors
@pytest.mark.registration
def test_error_details_accuracy(browser):
    """Test that error messages provide accurate and helpful information"""
    log_info("Starting error details accuracy test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    # Test multiple error scenarios
    invalid_email = "invalid-email"
    weak_password = "weak"
    missing_name = ""

    signup_page.enter_email(invalid_email)
    signup_page.click_signup_button()
    assert "valid email" in error_page.get_error_message('registration').lower(), "Email format error message is not accurate"

    signup_page.enter_email(generate_random_email())
    signup_page.enter_password(weak_password)
    signup_page.click_signup_button()
    assert "at least 8 characters" in error_page.get_error_message('registration').lower(), "Password strength error message is not accurate"

    signup_page.enter_password(generate_random_password())
    signup_page.enter_name(missing_name)
    signup_page.click_signup_button()
    assert "name" in error_page.get_error_message('registration').lower(), "Missing name error message is not accurate"


@pytest.mark.errors
@pytest.mark.registration
def test_simultaneous_field_errors(browser):
    """Test handling of errors in multiple fields simultaneously"""
    log_info("Starting simultaneous field errors test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    # Enter invalid data in multiple fields
    signup_page.enter_email("invalid-email")
    signup_page.enter_password("weak")
    signup_page.enter_name("")
    signup_page.accept_terms()
    signup_page.click_signup_button()

    # Verify errors for all fields are displayed
    assert error_page.is_error_displayed(), "No error messages are displayed"
    assert "valid email" in error_page.get_error_message('registration').lower(), "Email format error message is not accurate"
    assert "at least 8 characters" in error_page.get_error_message('registration').lower(), "Password strength error message is not accurate"
    assert "name" in error_page.get_error_message('registration').lower(), "Missing name error message is not accurate"

    # Correct each field one by one
    signup_page.enter_email(generate_random_email())
    signup_page.click_signup_button()
    assert "at least 8 characters" in error_page.get_error_message('registration').lower(), "Password strength error message is not accurate"
    assert "name" in error_page.get_error_message('registration').lower(), "Missing name error message is not accurate"

    signup_page.enter_password(generate_random_password())
    signup_page.click_signup_button()
    assert "name" in error_page.get_error_message('registration').lower(), "Missing name error message is not accurate"

    signup_page.enter_name(generate_random_name())
    signup_page.click_signup_button()
    assert signup_page.is_signup_successful(), "Registration is not successful after correcting all errors"


@pytest.mark.errors
@pytest.mark.registration
def test_session_expiry_error(browser):
    """Test error handling when session expires during registration"""
    log_info("Starting session expiry test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    test_user_data = random_user_data()
    signup_page.fill_signup_form(test_user_data['name'], test_user_data['email'], test_user_data['password'])

    # Manipulate browser cookies to expire the session
    browser.delete_all_cookies()

    signup_page.click_signup_button()

    assert error_page.is_specific_error_displayed('server'), "Session expiry error is not displayed"
    assert "refresh" in error_page.get_error_message('server').lower() or "start over" in error_page.get_error_message('server').lower(), "User is not prompted to refresh or start over"


@pytest.mark.errors
@pytest.mark.registration
def test_error_logging(browser):
    """Test that errors during registration are properly logged"""
    log_info("Starting error logging test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    # Set up log capture for testing
    # Trigger various error scenarios
    # Verify each error is properly logged with appropriate level and context
    # Verify log messages contain relevant details for debugging
    pass  # Implementation details depend on logging framework


@pytest.mark.errors
@pytest.mark.registration
def test_error_screenshot_capture(browser, take_screenshot_on_failure):
    """Test that screenshots are captured when registration errors occur"""
    log_info("Starting error screenshot capture test")

    signup_page = SignupPage(browser)
    error_page = ErrorPage(browser)

    signup_page.navigate_to()

    # Trigger an error scenario
    signup_page.enter_email("invalid-email")
    signup_page.click_signup_button()

    # Use ErrorPage.capture_error_screenshot() to manually capture error state
    screenshot_path = error_page.capture_error_screenshot('registration')
    assert screenshot_path is not None, "Screenshot was not captured manually"

    # Force a test failure to verify automatic screenshot capture works
    assert False, "Forcing test failure to verify automatic screenshot capture"