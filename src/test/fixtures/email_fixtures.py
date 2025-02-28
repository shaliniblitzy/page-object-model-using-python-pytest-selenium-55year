"""
Provides pytest fixtures related to email generation, verification, and integration with 
Mailinator for testing user registration and story sharing workflows in the Storydoc automation framework.
"""

import pytest  # version 7.3+
import time
import os
from typing import Dict, Any, Optional

# Internal imports
from ..utilities.email_helper import EmailHelper
from ..utilities.mailinator_api import MailinatorAPI
from ..utilities.random_data_generator import generate_random_email
from ..config.mailinator_config import (
    DEFAULT_DOMAIN,
    MAILINATOR_API_KEY,
    MAILINATOR_TIMEOUT,
    MAILINATOR_POLLING_INTERVAL,
    EMAIL_SUBJECT_CONFIG
)
from ..utilities.logger import log_info, log_debug, log_warning, log_error

# Global variables
DEFAULT_EMAIL_PREFIX = os.getenv('TEST_EMAIL_PREFIX', 'test.user')
DEFAULT_EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', MAILINATOR_TIMEOUT))
DEFAULT_POLLING_INTERVAL = int(os.getenv('EMAIL_POLLING_INTERVAL', MAILINATOR_POLLING_INTERVAL))
REGISTRATION_EMAIL_SUBJECT = EMAIL_SUBJECT_CONFIG['registration']
SHARING_EMAIL_SUBJECT = EMAIL_SUBJECT_CONFIG['sharing']

# Singleton instances
email_helper_instance = None  # Will be initialized in email_helper fixture
mailinator_api_instance = None  # Will be initialized in mailinator_api fixture


def initialize_email_helper() -> EmailHelper:
    """Initialize the EmailHelper singleton instance"""
    global email_helper_instance
    
    if email_helper_instance is None:
        email_helper_instance = EmailHelper()
        log_info("Initialized EmailHelper instance")
    
    return email_helper_instance


def initialize_mailinator_api() -> MailinatorAPI:
    """Initialize the MailinatorAPI singleton instance"""
    global mailinator_api_instance
    
    if mailinator_api_instance is None:
        mailinator_api_instance = MailinatorAPI(
            api_key=MAILINATOR_API_KEY,
            default_timeout=DEFAULT_EMAIL_TIMEOUT,
            polling_interval=DEFAULT_POLLING_INTERVAL
        )
        log_info("Initialized MailinatorAPI instance")
    
    return mailinator_api_instance


@pytest.fixture(scope='session')
def email_helper() -> EmailHelper:
    """Pytest fixture that provides an EmailHelper instance"""
    log_info("Providing email_helper fixture")
    helper = initialize_email_helper()
    yield helper


@pytest.fixture(scope='session')
def mailinator_api() -> MailinatorAPI:
    """Pytest fixture that provides a MailinatorAPI instance for direct API operations"""
    log_info("Providing mailinator_api fixture")
    api = initialize_mailinator_api()
    yield api


@pytest.fixture(scope='function')
def random_email(request) -> str:
    """Pytest fixture that provides a random email address for testing"""
    # Check if prefix is provided in request.param
    prefix = getattr(request, 'param', DEFAULT_EMAIL_PREFIX)
    email = generate_random_email(prefix)
    log_info(f"Generated random email: {email}")
    return email


@pytest.fixture(scope='function')
def registration_email(request) -> str:
    """Pytest fixture that provides a random email address for registration testing"""
    # Check if prefix is provided in request.param
    prefix = getattr(request, 'param', f'register.user.{int(time.time())}')
    email = generate_random_email(prefix)
    log_info(f"Generated registration email: {email}")
    return email


@pytest.fixture(scope='function')
def sharing_email(request) -> str:
    """Pytest fixture that provides a random email address for story sharing testing"""
    # Check if prefix is provided in request.param
    prefix = getattr(request, 'param', f'share.recipient.{int(time.time())}')
    email = generate_random_email(prefix)
    log_info(f"Generated sharing email: {email}")
    return email


@pytest.fixture(scope='function')
def wait_for_registration_email(email_helper: EmailHelper, registration_email: str) -> Dict:
    """Pytest fixture that waits for and returns registration verification email"""
    log_info(f"Waiting for registration email for {registration_email}")
    message = email_helper.wait_for_email(
        registration_email,
        REGISTRATION_EMAIL_SUBJECT,
        DEFAULT_EMAIL_TIMEOUT
    )
    assert message is not None, f"Registration email not received within {DEFAULT_EMAIL_TIMEOUT} seconds"
    log_info("Registration email verification successful")
    return message


@pytest.fixture(scope='function')
def wait_for_sharing_email(email_helper: EmailHelper, sharing_email: str) -> Dict:
    """Pytest fixture that waits for and returns story sharing email"""
    log_info(f"Waiting for sharing email for {sharing_email}")
    message = email_helper.wait_for_email(
        sharing_email,
        SHARING_EMAIL_SUBJECT,
        DEFAULT_EMAIL_TIMEOUT
    )
    assert message is not None, f"Sharing email not received within {DEFAULT_EMAIL_TIMEOUT} seconds"
    log_info("Sharing email verification successful")
    return message


@pytest.fixture(scope='function')
def registration_verification_link(email_helper: EmailHelper, wait_for_registration_email: Dict) -> str:
    """Pytest fixture that provides the verification link from registration email"""
    log_info("Extracting registration verification link")
    verification_link = email_helper.extract_verification_link(wait_for_registration_email)
    assert verification_link is not None, "No verification link found in registration email"
    log_info(f"Registration verification link: {verification_link}")
    return verification_link


@pytest.fixture(scope='function')
def sharing_verification_link(email_helper: EmailHelper, wait_for_sharing_email: Dict) -> str:
    """Pytest fixture that provides the sharing link from sharing email"""
    log_info("Extracting sharing verification link")
    sharing_link = email_helper.extract_verification_link(wait_for_sharing_email)
    assert sharing_link is not None, "No verification link found in sharing email"
    log_info(f"Sharing verification link: {sharing_link}")
    return sharing_link


@pytest.fixture(scope='function')
def verify_email_delivery(email_helper: EmailHelper, request) -> bool:
    """Pytest fixture that verifies email delivery to a specific address"""
    params = request.param if hasattr(request, 'param') else {}
    
    email_address = params.get('email_address')
    subject = params.get('subject')
    timeout = params.get('timeout', DEFAULT_EMAIL_TIMEOUT)
    
    log_info(f"Verifying email delivery to {email_address} with subject '{subject}'")
    result = email_helper.verify_email_received(email_address, subject, timeout)
    return result