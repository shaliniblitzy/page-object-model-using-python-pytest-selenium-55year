import pytest  # pytest 7.3+
import logging  # standard library
import time  # standard library

from src.test.pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from src.test.pages.verification_page import VerificationPage  # src/test/pages/verification_page.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.email_fixtures import email_helper  # src/test/fixtures/email_fixtures.py
from src.test.fixtures.email_fixtures import registration_email  # src/test/fixtures/email_fixtures.py
from src.test.fixtures.user_fixtures import random_user_data  # src/test/fixtures/user_fixtures.py
from src.test.config.timeout_config import EMAIL_DELIVERY_TIMEOUT  # src/test/config/timeout_config.py

logger = logging.getLogger(__name__)


@pytest.mark.registration
@pytest.mark.email_verification
def test_email_verification_on_registration(browser, registration_email, email_helper):
    """Tests that an email verification is sent upon successful registration and can be verified

    Args:
        browser: WebDriver instance
        registration_email: Fixture for generating a mailinator email address
        email_helper: Fixture for EmailHelper instance
    """
    # Initialize SignupPage and VerificationPage objects with the browser instance
    signup_page = SignupPage(browser)
    verification_page = VerificationPage(browser)

    # Generate random user data with the registration_email
    user_data = random_user_data()
    user_data['email'] = registration_email

    # Navigate to the signup page
    signup_page.navigate_to()

    # Enter user details (name, email, password)
    signup_page.enter_name(user_data['name'])
    signup_page.enter_email(user_data['email'])
    signup_page.enter_password(user_data['password'])

    # Accept terms and conditions
    signup_page.accept_terms()

    # Submit the registration form
    signup_page.click_signup_button()

    # Verify registration was successful
    assert signup_page.is_signup_successful(), "Registration failed"

    # Wait for verification email to be delivered to Mailinator
    assert email_helper.verify_email_received(user_data['email'], "Welcome to Storydoc"), "Verification email not received"

    # Extract verification link from the email
    verification_link = email_helper.extract_verification_link(email_helper.wait_for_email(user_data['email'], "Welcome to Storydoc"))
    assert verification_link is not None, "No verification link found in email"

    # Navigate to the verification link
    verification_page.navigate_to_verification(verification_link.split("token=")[1])

    # Verify that the account is successfully verified
    assert verification_page.is_account_verified(), "Account verification failed"


@pytest.mark.registration
@pytest.mark.email_verification
def test_verification_link_expiry(browser, registration_email, email_helper):
    """Tests that the verification link expires after a certain period of time (simulated by manipulating the token)

    Args:
        browser: WebDriver instance
        registration_email: Fixture for generating a mailinator email address
        email_helper: Fixture for EmailHelper instance
    """
    # Initialize SignupPage and VerificationPage objects with the browser instance
    signup_page = SignupPage(browser)
    verification_page = VerificationPage(browser)

    # Generate random user data with the registration_email
    user_data = random_user_data()
    user_data['email'] = registration_email

    # Navigate to the signup page
    signup_page.navigate_to()

    # Enter user details (name, email, password)
    signup_page.enter_name(user_data['name'])
    signup_page.enter_email(user_data['email'])
    signup_page.enter_password(user_data['password'])

    # Accept terms and conditions
    signup_page.accept_terms()

    # Submit the registration form
    signup_page.click_signup_button()

    # Verify registration was successful
    assert signup_page.is_signup_successful(), "Registration failed"

    # Wait for verification email to be delivered to Mailinator
    assert email_helper.verify_email_received(user_data['email'], "Welcome to Storydoc"), "Verification email not received"

    # Extract verification link from the email
    verification_link = email_helper.extract_verification_link(email_helper.wait_for_email(user_data['email'], "Welcome to Storydoc"))
    assert verification_link is not None, "No verification link found in email"

    # Modify the verification link to simulate an expired link (e.g., change token)
    modified_link = verification_link.replace(verification_link.split("token=")[1], "invalid_token")

    # Navigate to the modified verification link
    verification_page.navigate_to_verification(modified_link.split("token=")[1])

    # Verify that the verification page shows an expiry message
    assert verification_page.is_verification_link_expired(), "Verification link expiry message not displayed"


@pytest.mark.registration
@pytest.mark.email_verification
def test_resend_verification_email(browser, registration_email, email_helper):
    """Tests that a new verification email can be requested and is delivered

    Args:
        browser: WebDriver instance
        registration_email: Fixture for generating a mailinator email address
        email_helper: Fixture for EmailHelper instance
    """
    # Initialize SignupPage and VerificationPage objects with the browser instance
    signup_page = SignupPage(browser)
    verification_page = VerificationPage(browser)

    # Generate random user data with the registration_email
    user_data = random_user_data()
    user_data['email'] = registration_email

    # Navigate to the signup page
    signup_page.navigate_to()

    # Enter user details (name, email, password)
    signup_page.enter_name(user_data['name'])
    signup_page.enter_email(user_data['email'])
    signup_page.enter_password(user_data['password'])

    # Accept terms and conditions
    signup_page.accept_terms()

    # Submit the registration form
    signup_page.click_signup_button()

    # Verify registration was successful
    assert signup_page.is_signup_successful(), "Registration failed"

    # Wait for verification email to be delivered to Mailinator
    assert email_helper.verify_email_received(user_data['email'], "Welcome to Storydoc"), "Verification email not received"

    # Extract verification link from the email
    verification_link = email_helper.extract_verification_link(email_helper.wait_for_email(user_data['email'], "Welcome to Storydoc"))
    assert verification_link is not None, "No verification link found in email"

    # Modify the verification link to simulate an expired link
    modified_link = verification_link.replace(verification_link.split("token=")[1], "invalid_token")

    # Navigate to the modified verification link
    verification_page.navigate_to_verification(modified_link.split("token=")[1])

    # Verify that the verification page shows an expiry message
    assert verification_page.is_verification_link_expired(), "Verification link expiry message not displayed"

    # Click the resend verification button
    verification_page.resend_verification_email()

    # Wait for a new verification email to be delivered
    assert email_helper.verify_email_received(user_data['email'], "Welcome to Storydoc"), "New verification email not received"

    # Extract the new verification link
    new_verification_link = email_helper.extract_verification_link(email_helper.wait_for_email(user_data['email'], "Welcome to Storydoc"))
    assert new_verification_link is not None, "No new verification link found in email"

    # Navigate to the new verification link
    verification_page.navigate_to_verification(new_verification_link.split("token=")[1])

    # Verify that the account is successfully verified
    assert verification_page.is_account_verified(), "Account verification failed"


@pytest.mark.registration
@pytest.mark.email_verification
def test_multiple_verification_attempts(browser, registration_email, email_helper):
    """Tests that a verification link can only be used once

    Args:
        browser: WebDriver instance
        registration_email: Fixture for generating a mailinator email address
        email_helper: Fixture for EmailHelper instance
    """
    # Initialize SignupPage and VerificationPage objects with the browser instance
    signup_page = SignupPage(browser)
    verification_page = VerificationPage(browser)

    # Generate random user data with the registration_email
    user_data = random_user_data()
    user_data['email'] = registration_email

    # Navigate to the signup page
    signup_page.navigate_to()

    # Enter user details (name, email, password)
    signup_page.enter_name(user_data['name'])
    signup_page.enter_email(user_data['email'])
    signup_page.enter_password(user_data['password'])

    # Accept terms and conditions
    signup_page.accept_terms()

    # Submit the registration form
    signup_page.click_signup_button()

    # Verify registration was successful
    assert signup_page.is_signup_successful(), "Registration failed"

    # Wait for verification email to be delivered to Mailinator
    assert email_helper.verify_email_received(user_data['email'], "Welcome to Storydoc"), "Verification email not received"

    # Extract verification link from the email
    verification_link = email_helper.extract_verification_link(email_helper.wait_for_email(user_data['email'], "Welcome to Storydoc"))
    assert verification_link is not None, "No verification link found in email"

    # Navigate to the verification link
    verification_page.navigate_to_verification(verification_link.split("token=")[1])

    # Verify that the account is successfully verified
    assert verification_page.is_account_verified(), "Account verification failed"

    # Navigate to the verification link again
    verification_page.navigate_to_verification(verification_link.split("token=")[1])

    # Verify that the verification page shows a message indicating the link has already been used
    assert "Your link has expired" in verification_page.get_verification_status_message(), "Multiple verification attempts not handled"


@pytest.mark.registration
@pytest.mark.email_verification
@pytest.mark.smoke
def test_complete_registration_workflow(browser, registration_email, email_helper):
    """Tests the complete registration workflow including email verification

    Args:
        browser: WebDriver instance
        registration_email: Fixture for generating a mailinator email address
        email_helper: Fixture for EmailHelper instance
    """
    # Initialize SignupPage with the browser instance
    signup_page = SignupPage(browser)

    # Generate random user data with the registration_email
    user_data = random_user_data()
    user_data['email'] = registration_email

    # Call complete_registration_with_verification method with the user data
    result = signup_page.complete_registration_with_verification(
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password']
    )

    # Verify that the registration process was completed successfully
    assert result['success'], f"Registration failed: {result['message']}"

    # Verify that the dashboard is displayed after verification
    assert "Dashboard" in browser.title, "Dashboard not loaded after verification"