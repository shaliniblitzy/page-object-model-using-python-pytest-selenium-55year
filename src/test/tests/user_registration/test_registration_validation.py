import pytest  # pytest 7.3+
import time
from typing import Dict  # typing is a standard Python library

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from src.test.fixtures.email_fixtures import email_helper  # src/test/fixtures/email_fixtures.py
from src.test.fixtures.user_fixtures import test_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.user_fixtures import random_user_data  # src/test/fixtures/user_fixtures.py
from src.test.utilities.random_data_generator import generate_random_email  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_password  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_name  # src/test/utilities/random_data_generator.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.data.invalid_data import invalid_registration_data  # src/test/data/invalid_data.json

VALIDATION_TIMEOUT = 10  # Timeout for validation checks
DEFAULT_NAME = "Test User"  # Default name for validation tests
INVALID_EMAILS = invalid_registration_data['registration']['invalidEmails']  # List of invalid email formats
INVALID_PASSWORDS = invalid_registration_data['registration']['invalidPasswords']  # List of invalid passwords
INVALID_NAMES = invalid_registration_data['registration']['invalidNames']  # List of invalid names


@pytest.mark.validation
@pytest.mark.registration
def test_email_validation(browser):
    """Test that invalid email formats trigger appropriate validation errors"""
    log_info("Starting email validation test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter valid name and password
    signup_page.enter_name(DEFAULT_NAME)
    signup_page.enter_password(generate_random_password())

    # For each invalid email format in INVALID_EMAILS:
    for invalid_email in INVALID_EMAILS:
        # Enter invalid email
        signup_page.enter_email(invalid_email)

        # Click outside to trigger validation
        signup_page.click(SignupPage.NAME_FIELD)
        time.sleep(1)

        # Get error message
        error_message = signup_page.get_error_message('email')

        # Assert that appropriate error message is displayed
        assert error_message != "", f"No error message displayed for invalid email: {invalid_email}"

        # Assert email validation fails
        assert not signup_page.validate_email_field(invalid_email), f"Email validation did not fail for: {invalid_email}"


@pytest.mark.validation
@pytest.mark.registration
def test_password_validation(browser):
    """Test that weak passwords trigger appropriate validation errors"""
    log_info("Starting password validation test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter valid name and email
    signup_page.enter_name(DEFAULT_NAME)
    signup_page.enter_email(generate_random_email())

    # For each invalid password in INVALID_PASSWORDS:
    for invalid_password in INVALID_PASSWORDS:
        # Enter invalid password
        signup_page.enter_password(invalid_password)

        # Click outside to trigger validation
        signup_page.click(SignupPage.NAME_FIELD)
        time.sleep(1)

        # Get error message
        error_message = signup_page.get_error_message('password')

        # Assert that appropriate error message is displayed
        assert error_message != "", f"No error message displayed for invalid password: {invalid_password}"

        # Assert password validation fails
        assert not signup_page.validate_password_field(invalid_password), f"Password validation did not fail for: {invalid_password}"


@pytest.mark.validation
@pytest.mark.registration
def test_name_validation(browser):
    """Test that invalid names trigger appropriate validation errors"""
    log_info("Starting name validation test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter valid email and password
    signup_page.enter_email(generate_random_email())
    signup_page.enter_password(generate_random_password())

    # For each invalid name in INVALID_NAMES:
    for invalid_name in INVALID_NAMES:
        # Enter invalid name
        signup_page.enter_name(invalid_name)

        # Click outside to trigger validation
        signup_page.click(SignupPage.EMAIL_FIELD)
        time.sleep(1)

        # Get error message
        error_message = signup_page.get_error_message('name')

        # Assert that appropriate error message is displayed
        assert error_message != "", f"No error message displayed for invalid name: {invalid_name}"


@pytest.mark.validation
@pytest.mark.registration
def test_terms_validation(browser):
    """Test that registration fails if terms are not accepted"""
    log_info("Starting terms validation test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Fill out form with valid data (name, email, password)
    signup_page.fill_signup_form(generate_random_name(), generate_random_email(), generate_random_password(), accept_terms_checkbox=False)

    # Do NOT accept terms

    # Click signup button
    signup_page.click_signup_button()
    time.sleep(1)

    # Get error message for terms field
    error_message = signup_page.get_error_message('terms')

    # Assert that appropriate error message is displayed
    assert error_message != "", "No error message displayed for terms not accepted"


@pytest.mark.validation
@pytest.mark.registration
def test_form_validation_on_submit(browser):
    """Test that all form validations are triggered on form submission"""
    log_info("Starting form submission validation test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Leave all fields empty

    # Click signup button
    signup_page.click_signup_button()
    time.sleep(1)

    # Check for validation messages on all fields
    email_error = signup_page.get_error_message('email')
    password_error = signup_page.get_error_message('password')
    terms_error = signup_page.get_error_message('terms')

    # Assert that appropriate error messages are displayed for all required fields
    assert email_error != "", "No error message displayed for empty email"
    assert password_error != "", "No error message displayed for empty password"
    assert terms_error != "", "No error message displayed for terms not accepted"


@pytest.mark.validation
@pytest.mark.registration
def test_validation_messages_visibility(browser):
    """Test that validation messages appear and disappear appropriately"""
    log_info("Starting validation messages visibility test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter invalid email
    signup_page.enter_email("invalid-email")

    # Click outside to trigger validation
    signup_page.click(SignupPage.NAME_FIELD)
    time.sleep(1)

    # Assert that error message is displayed
    assert signup_page.is_signin_error_displayed(), "Error message is not displayed for invalid email"

    # Enter valid email
    signup_page.enter_email(generate_random_email())

    # Click outside again
    signup_page.click(SignupPage.NAME_FIELD)
    time.sleep(1)

    # Assert that error message disappears
    assert not signup_page.is_signin_error_displayed(), "Error message did not disappear after entering valid email"


@pytest.mark.validation
@pytest.mark.registration
def test_validation_clears_on_correct_input(browser):
    """Test that validation errors clear when correct input is provided"""
    log_info("Starting validation clearing test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # For each field (name, email, password):
    for field in ['name', 'email', 'password']:
        # Enter invalid value
        if field == 'name':
            signup_page.enter_name("123")
            signup_page.click(SignupPage.EMAIL_FIELD)
        elif field == 'email':
            signup_page.enter_email("invalid-email")
            signup_page.click(SignupPage.PASSWORD_FIELD)
        elif field == 'password':
            signup_page.enter_password("weak")
            signup_page.click(SignupPage.NAME_FIELD)
        time.sleep(1)

        # Verify error appears
        assert signup_page.get_error_message(field) != "", f"Error message did not appear for invalid {field}"

        # Enter valid value
        if field == 'name':
            signup_page.enter_name(generate_random_name())
            signup_page.click(SignupPage.EMAIL_FIELD)
        elif field == 'email':
            signup_page.enter_email(generate_random_email())
            signup_page.click(SignupPage.PASSWORD_FIELD)
        elif field == 'password':
            signup_page.enter_password(generate_random_password())
            signup_page.click(SignupPage.NAME_FIELD)
        time.sleep(1)

        # Verify error disappears
        assert signup_page.get_error_message(field) == "", f"Error message did not disappear after entering valid {field}"


@pytest.mark.validation
@pytest.mark.registration
def test_validation_prevents_submission(browser):
    """Test that form submission is prevented when validation errors exist"""
    log_info("Starting submission prevention test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter invalid email
    signup_page.enter_email("invalid-email")

    # Enter valid password and name
    signup_page.enter_password(generate_random_password())
    signup_page.enter_name(generate_random_name())

    # Accept terms
    signup_page.accept_terms()

    # Click signup button
    signup_page.click_signup_button()
    time.sleep(1)

    # Assert that form submission is prevented
    # Assert that we're still on the signup page
    assert "sign-up" in browser.current_url, "Form submission was not prevented"

    # Assert that error message for email is still visible
    assert signup_page.is_signin_error_displayed(), "Error message for email is not visible"


@pytest.mark.validation
@pytest.mark.registration
def test_inline_validation_timing(browser):
    """Test that inline validation occurs at the appropriate time (on blur)"""
    log_info("Starting inline validation timing test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter invalid email
    signup_page.enter_email("invalid-email")

    # Assert that NO error message appears yet (validation should happen on blur)
    assert not signup_page.is_signin_error_displayed(), "Error message appeared before blur event"

    # Click outside the field (trigger blur event)
    signup_page.click(SignupPage.NAME_FIELD)
    time.sleep(1)

    # Assert that error message now appears
    assert signup_page.is_signin_error_displayed(), "Error message did not appear after blur event"


@pytest.mark.validation
@pytest.mark.registration
def test_multiple_validation_errors(browser):
    """Test handling of multiple validation errors simultaneously"""
    log_info("Starting multiple validation errors test")

    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Navigate to signup page
    signup_page.navigate_to()

    # Enter invalid values for all fields (name, email, password)
    signup_page.enter_name("123")
    signup_page.enter_email("invalid-email")
    signup_page.enter_password("weak")

    # Don't accept terms
    # Click signup button
    signup_page.click_signup_button()
    time.sleep(1)

    # Assert that appropriate error messages are displayed for all fields
    assert signup_page.get_error_message('name') != "", "No error message displayed for invalid name"
    assert signup_page.get_error_message('email') != "", "No error message displayed for invalid email"
    assert signup_page.get_error_message('password') != "", "No error message displayed for invalid password"
    assert signup_page.get_error_message('terms') != "", "No error message displayed for terms not accepted"