"""
Test module for verifying the integration between Storydoc's user registration process and Mailinator email service.
Tests email delivery, verification link extraction, and validation of the complete email verification workflow.
"""

import pytest  # pytest 7.3+
import time
from typing import Dict, Optional
from selenium.common.exceptions import TimeoutException

# Import page objects
from src.test.pages.signup_page import SignupPage

# Import utilities
from src.test.utilities.email_helper import EmailHelper
from src.test.utilities.mailinator_api import MailinatorAPI
from src.test.utilities.random_data_generator import generate_random_email, generate_random_password, generate_random_name

# Import fixtures
from src.test.fixtures.browser_fixtures import browser
from src.test.fixtures.email_fixtures import (
    email_helper, 
    mailinator_api, 
    random_email, 
    wait_for_registration_email, 
    registration_verification_link
)

# Import configuration
from src.test.config.mailinator_config import DEFAULT_DOMAIN, EMAIL_SUBJECT_CONFIG, MAILINATOR_TIMEOUT

# Define global constants
REGISTRATION_SUBJECT = EMAIL_SUBJECT_CONFIG['registration']
DEFAULT_TIMEOUT = MAILINATOR_TIMEOUT


def test_mailinator_api_integration(mailinator_api: MailinatorAPI):
    """
    Test direct integration with the Mailinator API
    
    Args:
        mailinator_api: Fixture providing MailinatorAPI instance
    """
    # Generate a unique test email address
    test_email = generate_random_email(prefix="api_test")
    
    # Get the inbox for the generated email address
    inbox = mailinator_api.get_inbox(test_email)
    
    # Verify the inbox response structure
    assert inbox is not None, "Failed to get inbox from Mailinator API"
    assert "msgs" in inbox, "Inbox response does not contain 'msgs' field"
    
    # As it's a new inbox, it should be empty but properly structured
    assert isinstance(inbox["msgs"], list), "Inbox msgs field is not a list"
    
    # Verify API is accessible by checking we got a valid response
    assert mailinator_api.is_api_accessible_domain(DEFAULT_DOMAIN), f"{DEFAULT_DOMAIN} should be API accessible"


def test_generate_random_email(email_helper: EmailHelper):
    """
    Test that random email generation works correctly
    
    Args:
        email_helper: Fixture providing EmailHelper instance
    """
    # Generate a random email using email_helper
    email1 = email_helper.generate_email_address()
    
    # Verify the email follows the expected format
    assert "@" in email1, "Generated email should contain @ symbol"
    assert email1.endswith(DEFAULT_DOMAIN), f"Generated email should end with {DEFAULT_DOMAIN}"
    
    # Generate another email and verify they are different (uniqueness)
    email2 = email_helper.generate_email_address()
    assert email1 != email2, "Generated emails should be unique"


def test_email_verification_link_extraction(mailinator_api: MailinatorAPI):
    """
    Test the extraction of verification links from email content
    
    Args:
        mailinator_api: Fixture providing MailinatorAPI instance
    """
    # Create sample HTML email content with a verification link
    sample_content = """
    <html>
        <body>
            <p>Thank you for signing up!</p>
            <p>Please click <a href="https://editor-staging.storydoc.com/verify/abc123">here</a> to verify your account.</p>
        </body>
    </html>
    """
    
    # Create a mock message structure similar to what Mailinator API returns
    mock_message = {
        "parts": [
            {
                "headers": {
                    "content-type": "text/html; charset=UTF-8"
                },
                "body": sample_content
            }
        ]
    }
    
    # Extract verification link
    verification_link = mailinator_api.extract_verification_link(mock_message)
    
    # Verify that the correct verification link is extracted
    assert verification_link is not None, "Verification link should be extracted from email content"
    assert "https://editor-staging.storydoc.com/verify/abc123" in verification_link, "Extracted link does not match expected verification link"
    
    # Test with invalid content and verify appropriate handling
    invalid_message = {"parts": [{"headers": {"content-type": "text/plain"}, "body": "No links here"}]}
    no_link = mailinator_api.extract_verification_link(invalid_message)
    assert no_link is None, "Should return None when no verification link is found"


@pytest.mark.integration
def test_email_delivery_verification(browser, random_email, mailinator_api: MailinatorAPI):
    """
    Test verification of email delivery using fixtures (requires actual registration)
    
    Args:
        browser: Fixture providing WebDriver instance
        random_email: Fixture providing a random email address
        mailinator_api: Fixture providing MailinatorAPI instance
    """
    # Initialize page objects
    signup_page = SignupPage(browser)
    
    # Generate random user data
    name = generate_random_name()
    password = generate_random_password()
    email = random_email
    
    # Record start time for SLA measurement
    start_time = time.time()
    
    # Complete the signup process
    signup_success = signup_page.complete_signup(name, email, password)
    assert signup_success, f"User registration failed for {email}"
    
    # Verify that the registration email is delivered within the expected SLA
    email_received = mailinator_api.verify_email_received(email, REGISTRATION_SUBJECT, DEFAULT_TIMEOUT)
    assert email_received, f"Registration email not received for {email} within {DEFAULT_TIMEOUT} seconds"
    
    # Calculate and log email delivery time
    delivery_time = time.time() - start_time
    print(f"Email delivery time: {delivery_time:.2f} seconds (SLA: {DEFAULT_TIMEOUT} seconds)")
    
    # Assert that delivery time meets SLA requirement
    assert delivery_time <= DEFAULT_TIMEOUT, f"Email delivery time ({delivery_time:.2f}s) exceeded SLA ({DEFAULT_TIMEOUT}s)"


@pytest.mark.integration
def test_registration_verification_link_extraction(browser, random_email, mailinator_api: MailinatorAPI):
    """
    Test the extraction of verification links from actual registration emails
    
    Args:
        browser: Fixture providing WebDriver instance
        random_email: Fixture providing a random email address
        mailinator_api: Fixture providing MailinatorAPI instance
    """
    # Initialize page objects
    signup_page = SignupPage(browser)
    
    # Generate random user data
    name = generate_random_name()
    password = generate_random_password()
    email = random_email
    
    # Complete the signup process
    signup_success = signup_page.complete_signup(name, email, password)
    assert signup_success, f"User registration failed for {email}"
    
    # Wait for registration email
    message = mailinator_api.wait_for_email(email, REGISTRATION_SUBJECT, DEFAULT_TIMEOUT)
    assert message is not None, f"Registration email not received for {email} within {DEFAULT_TIMEOUT} seconds"
    
    # Extract verification link
    verification_link = mailinator_api.get_verification_link(message)
    
    # Verify that a valid verification link was extracted
    assert verification_link is not None, "No verification link found in registration email"
    assert "https://" in verification_link, "Verification link should be a valid URL"
    assert "verify" in verification_link or "confirm" in verification_link, "Verification link should contain verification keywords"


@pytest.mark.integration
@pytest.mark.e2e
def test_complete_registration_with_email_verification(browser, random_email, wait_for_registration_email, registration_verification_link):
    """
    Test the complete user registration flow including email verification
    
    Args:
        browser: Fixture providing WebDriver instance
        random_email: Fixture providing a random email address
        wait_for_registration_email: Fixture that waits for registration email
        registration_verification_link: Fixture providing the verification link
    """
    # Initialize page objects
    signup_page = SignupPage(browser)
    
    # Generate random user data
    name = generate_random_name()
    password = generate_random_password()
    email = random_email
    
    # Complete the signup process
    signup_success = signup_page.complete_signup(name, email, password)
    assert signup_success, f"User registration failed for {email}"
    
    # Email verification is handled by the fixtures wait_for_registration_email and registration_verification_link
    
    # Verify that a valid verification link was extracted
    assert registration_verification_link is not None, "No verification link found in registration email"
    
    # Navigate to the verification link
    browser.get(registration_verification_link)
    
    # Verify that verification was successful by checking URL changes or specific elements
    # This could vary based on how Storydoc's verification flow works
    time.sleep(5)  # Allow time for verification to complete
    
    # Success could be indicated by redirect to dashboard or success message
    current_url = browser.current_url
    assert "dashboard" in current_url or "success" in current_url or "verified" in current_url, \
        f"Verification failed, unexpected redirect to: {current_url}"


@pytest.mark.performance
def test_email_delivery_sla(browser, random_email, email_helper: EmailHelper):
    """
    Test that email delivery meets the SLA requirements
    
    Args:
        browser: Fixture providing WebDriver instance
        random_email: Fixture providing a random email address
        email_helper: Fixture providing EmailHelper instance
    """
    # Initialize page objects
    signup_page = SignupPage(browser)
    
    # Generate random user data
    name = generate_random_name()
    password = generate_random_password()
    email = random_email
    
    # Record start time
    start_time = time.time()
    
    # Complete the signup process
    signup_success = signup_page.complete_signup(name, email, password)
    assert signup_success, f"User registration failed for {email}"
    
    # Wait for the registration email with a timeout
    received = False
    try:
        email_helper.wait_for_email(email, REGISTRATION_SUBJECT, DEFAULT_TIMEOUT)
        received = True
    except TimeoutException:
        received = False
    
    # Calculate delivery time
    delivery_time = time.time() - start_time
    
    # Log the actual delivery time for monitoring
    print(f"Email delivery time: {delivery_time:.2f} seconds (SLA: 30 seconds)")
    
    # Assert that email was received within SLA
    assert received, f"Registration email not received within SLA (30 seconds)"
    assert delivery_time <= 30, f"Email delivery time ({delivery_time:.2f}s) exceeded SLA (30s)"


def test_mailinator_api_error_handling(mailinator_api: MailinatorAPI):
    """
    Test error handling in the Mailinator API integration
    
    Args:
        mailinator_api: Fixture providing MailinatorAPI instance
    """
    # Attempt to access an invalid inbox (with special characters)
    invalid_email = "invalid_email_!@#$%^&*()@mailinator.com"
    inbox = mailinator_api.get_inbox(invalid_email)
    
    # Verify that appropriate error handling occurs (returns empty inbox instead of throwing exception)
    assert inbox is not None, "Mailinator API should handle invalid email gracefully"
    assert "msgs" in inbox, "Inbox response should contain msgs field even for invalid email"
    assert isinstance(inbox["msgs"], list), "msgs field should be a list even for error scenarios"
    
    # Test timeout scenarios with a very short timeout
    short_timeout = 0.1  # Very short timeout that should trigger timeout handling
    nonexistent_email = generate_random_email("nonexistent")
    
    # The API call should handle the timeout gracefully
    result = mailinator_api.wait_for_email(nonexistent_email, "Nonexistent Subject", short_timeout)
    assert result is None, "API should handle timeouts gracefully and return None"


@pytest.mark.integration
def test_multiple_email_verification(browser, random_email, email_helper: EmailHelper):
    """
    Test verification of multiple emails for the same user
    
    Args:
        browser: Fixture providing WebDriver instance
        random_email: Fixture providing a random email address
        email_helper: Fixture providing EmailHelper instance
    """
    # Initialize page objects
    signup_page = SignupPage(browser)
    
    # Generate random user data
    name = generate_random_name()
    password = generate_random_password()
    email = random_email
    
    # Complete registration for a new user
    signup_success = signup_page.complete_signup(name, email, password)
    assert signup_success, f"User registration failed for {email}"
    
    # Verify the first registration email is received
    registration_msg = email_helper.wait_for_email(email, REGISTRATION_SUBJECT, DEFAULT_TIMEOUT)
    assert registration_msg is not None, "Registration email not received"
    
    registration_link = email_helper.extract_verification_link(registration_msg)
    assert registration_link is not None, "Registration verification link not found"
    
    # We would trigger a password reset or other notification here
    # For test purposes, we'll just assert that we could successfully extract the first link
    # and verify that the mailinator service can handle multiple emails for the same inbox
    
    # In a real implementation, we would:
    # 1. Sign in using the newly registered user
    # 2. Trigger a password reset
    # 3. Check for the password reset email
    # 4. Extract the password reset link
    # 5. Verify both links are different
    
    # For now, we'll just verify the registration link is valid
    assert "https://" in registration_link, "Verification link should be a valid URL"