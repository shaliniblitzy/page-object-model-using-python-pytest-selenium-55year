"""
Provides pytest fixtures for user-related test data and operations in the Storydoc automation framework.
This module contains fixtures for random user generation, test user creation, and user management that are used across various test cases for user registration, authentication, story creation, and sharing.
"""

import pytest  # pytest 7.3+
import time  # built-in
from typing import Dict  # built-in

# Internal imports
from .browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from .email_fixtures import email_helper  # src/test/fixtures/email_fixtures.py
from .email_fixtures import registration_email  # src/test/fixtures/email_fixtures.py
from ..pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from ..pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from ..utilities.random_data_generator import generate_random_email  # src/test/utilities/random_data_generator.py
from ..utilities.random_data_generator import generate_random_password  # src/test/utilities/random_data_generator.py
from ..utilities.random_data_generator import generate_random_name  # src/test/utilities/random_data_generator.py
from ..utilities.random_data_generator import generate_test_user_data  # src/test/utilities/random_data_generator.py
from ..utilities.logger import log_info  # src/test/utilities/logger.py
from ..utilities.logger import log_debug  # src/test/utilities/logger.py
from ..config.constants import TEST_USER  # src/test/config/constants.py
from ..config.constants import USER_DEFAULTS  # src/test/config/constants.py

# Global variables
DEFAULT_PASSWORD = USER_DEFAULTS.get('PASSWORD', 'Test@123')
DEFAULT_EMAIL_PREFIX = USER_DEFAULTS.get('EMAIL_PREFIX', 'test.user')
DEFAULT_REMEMBER_ME = USER_DEFAULTS.get('REMEMBER_ME', False)
DEFAULT_TIMEOUT = USER_DEFAULTS.get('TIMEOUT', 10)
USER_CREDENTIALS_CACHE = {}


def random_user_data(email_prefix: str = None) -> Dict:
    """Generate random user data for testing

    Args:
        email_prefix (str): Prefix for the email address

    Returns:
        dict: Dictionary containing user data with name, email, and password
    """
    # Set default email_prefix to DEFAULT_EMAIL_PREFIX if not provided
    if email_prefix is None:
        email_prefix = DEFAULT_EMAIL_PREFIX

    # Call generate_test_user_data() from random_data_generator
    user_data = generate_test_user_data()

    # If email_prefix provided, generate custom email using generate_random_email(email_prefix)
    if email_prefix:
        user_data['email'] = generate_random_email(email_prefix)

    # Log generated user data (masking password)
    log_info(f"Generated user data: name={user_data['name']}, email={user_data['email']}, password=********")

    # Return user data dictionary
    return user_data


def create_test_user(browser, user_data: Dict = None) -> Dict:
    """Create a new test user in the application

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_data (dict): User data dictionary

    Returns:
        dict: User data dictionary if creation successful, None otherwise
    """
    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # If user_data not provided, generate random user data using random_user_data()
    if user_data is None:
        user_data = random_user_data()

    # Call complete_signup method with user data (name, email, password)
    signup_success = signup_page.complete_signup(user_data['name'], user_data['email'], user_data['password'])

    # If signup successful, add user to USER_CREDENTIALS_CACHE
    if signup_success:
        USER_CREDENTIALS_CACHE[user_data['email']] = user_data
        # Log successful user creation
        log_info(f"Successfully created user: {user_data['email']}")
        # Return user data if successful, None otherwise
        return user_data
    else:
        log_info(f"Failed to create user")
        return None


def authenticate_user(browser, user_data: Dict = None, remember_me: bool = DEFAULT_REMEMBER_ME) -> bool:
    """Authenticate an existing user in the application

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_data (dict): User data dictionary
        remember_me (bool): Whether to check the 'remember me' checkbox

    Returns:
        bool: True if authentication successful, False otherwise
    """
    # Initialize SigninPage with browser instance
    signin_page = SigninPage(browser)

    # Set remember_me to DEFAULT_REMEMBER_ME if not provided
    if remember_me is None:
        remember_me = DEFAULT_REMEMBER_ME

    # If user_data not provided, use first entry from USER_CREDENTIALS_CACHE
    if user_data is None and USER_CREDENTIALS_CACHE:
        user_data = next(iter(USER_CREDENTIALS_CACHE.values()))

    # Call complete_signin method with user data (email, password, remember_me)
    signin_success = signin_page.complete_signin(user_data['email'], user_data['password'], remember_me)

    # Log authentication result
    if signin_success:
        log_info(f"Successfully authenticated user: {user_data['email']}")
    else:
        log_info(f"Failed to authenticate user: {user_data['email']}")

    # Return True if signin successful, False otherwise
    return signin_success


def register_and_authenticate_user(browser, user_data: Dict = None, remember_me: bool = DEFAULT_REMEMBER_ME) -> Dict:
    """Register a new user and authenticate in a single step

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        user_data (dict): User data dictionary
        remember_me (bool): Whether to check the 'remember me' checkbox

    Returns:
        dict: User data if registration and authentication successful, None otherwise
    """
    # Create new test user using create_test_user(browser, user_data)
    user_data = create_test_user(browser, user_data)

    # If user creation successful, authenticate user using authenticate_user(browser, user_data, remember_me)
    if user_data:
        auth_success = authenticate_user(browser, user_data, remember_me)

        # If both operations successful, return user data
        if auth_success:
            log_info(f"Successfully registered and authenticated user: {user_data['email']}")
            return user_data
        else:
            log_info(f"Failed to authenticate user after registration")
            return None
    else:
        log_info(f"Failed to register user")
        return None


@pytest.fixture(scope='function')
def test_user(request) -> Dict:
    """Pytest fixture that provides random test user data

    Args:
        request (pytest.FixtureRequest): Pytest fixture request object

    Returns:
        dict: Dictionary containing user data
    """
    # Check if email_prefix is provided in request.param
    email_prefix = getattr(request, 'param', None)

    # Generate random user data using random_user_data(email_prefix)
    user_data = random_user_data(email_prefix)

    # Log test user data being provided (masking password)
    log_info(f"Providing test user fixture: name={user_data['name']}, email={user_data['email']}, password=********")

    # Return user data dictionary
    return user_data


@pytest.fixture(scope='function')
def authenticated_user(browser, test_user: Dict) -> Dict:
    """Pytest fixture that provides an authenticated user session

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        test_user (dict): Dictionary containing user data

    Returns:
        dict: User data dictionary if authentication successful
    """
    # Register and authenticate user using register_and_authenticate_user(browser, test_user)
    user_data = register_and_authenticate_user(browser, test_user)

    # Assert that user authentication was successful
    assert user_data is not None, "User authentication failed"

    # Log authenticated user session created
    log_info(f"Authenticated user session created for: {user_data['email']}")

    # Yield user data to the test
    yield user_data

    # No specific cleanup as browser fixture will handle browser cleanup


@pytest.fixture(scope='function')
def registered_user(browser, test_user: Dict, email_helper) -> Dict:
    """Pytest fixture that provides a registered but not authenticated user

    Args:
        browser (webdriver.WebDriver): WebDriver instance
        test_user (dict): Dictionary containing user data
        email_helper (EmailHelper): Email helper fixture

    Returns:
        dict: User data dictionary if registration successful
    """
    # Create test user using create_test_user(browser, test_user)
    user_data = create_test_user(browser, test_user)

    # Assert that user registration was successful
    assert user_data is not None, "User registration failed"

    # Wait for verification email using email_helper
    # Extract verification link from email
    # Verify user account using verification link
    # Assert that user registration was successful
    # Log registered user created
    # Yield user data to the test
    # No specific cleanup as browser fixture will handle browser cleanup
    yield user_data
    # Create test user using create_test_user(browser, test_user)
    # Wait for verification email using email_helper
    # Extract verification link from email
    # Verify user account using verification link
    # Assert that user registration was successful
    # Log registered user created
    # Yield user data to the test
    # No specific cleanup as browser fixture will handle browser cleanup
    log_info(f"Registered user created for: {user_data['email']}")
    yield user_data


@pytest.fixture(scope='session')
def user_credentials(request) -> Dict:
    """Pytest fixture that provides user credentials that persist between tests

    Args:
        request (pytest.FixtureRequest): Pytest fixture request object

    Returns:
        dict: Dictionary of user credentials
    """
    # Check if USER_CREDENTIALS_CACHE is empty
    if not USER_CREDENTIALS_CACHE:
        # If empty, generate default credentials using random_user_data()
        default_credentials = random_user_data()
        USER_CREDENTIALS_CACHE[default_credentials['email']] = default_credentials

    # Log user credentials being provided (masking passwords)
    log_info(f"Providing user credentials fixture: email={next(iter(USER_CREDENTIALS_CACHE))}, password=********")

    # Return USER_CREDENTIALS_CACHE
    return USER_CREDENTIALS_CACHE

    # No specific cleanup required