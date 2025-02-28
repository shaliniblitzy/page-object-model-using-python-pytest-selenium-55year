"""Tests for user authentication functionality in the Storydoc application. This module contains test cases for valid and invalid authentication scenarios, error handling, session management, and authentication redirects."""

# Internal imports
from .test_valid_authentication import TestValidAuthentication  # Import test class for valid user authentication scenarios
from .test_invalid_credentials import TestInvalidCredentials  # Import test class for invalid credentials scenarios
from .test_authentication_errors import TestAuthenticationErrors  # Import test class for authentication error scenarios
from .test_remember_me import TestRememberMe  # Import test class for remember me functionality
from .test_session_management import TestSessionManagement  # Import test class for session management tests
from .test_authentication_redirect import TestAuthenticationRedirect  # Import test class for authentication redirect tests
from src.test.config.timeout_config import USER_AUTHENTICATION_TIMEOUT  # Import authentication timeout configuration

MODULE_DESCRIPTION = "Tests for user authentication functionality in the Storydoc application. This module contains test cases for valid and invalid authentication scenarios, error handling, session management, and authentication redirects."

AUTH_TIMEOUT = USER_AUTHENTICATION_TIMEOUT  # Default timeout for authentication operations
AUTH_RETRY_COUNT = 3  # Default retry count for authentication operations
AUTHENTICATION_SLA_SECONDS = 3  # SLA for authentication process in seconds

__all__ = [
    "TestValidAuthentication",  # Export test class for valid authentication scenarios
    "TestInvalidCredentials",  # Export test class for invalid credentials scenarios
    "TestAuthenticationErrors",  # Export test class for authentication error scenarios
    "TestRememberMe",  # Export test class for remember me functionality
    "TestSessionManagement",  # Export test class for session management tests
    "TestAuthenticationRedirect",  # Export test class for authentication redirect tests
    "AUTH_TIMEOUT",  # Export authentication timeout configuration
    "AUTH_RETRY_COUNT",  # Export authentication retry count configuration
    "AUTHENTICATION_SLA_SECONDS", # Export authentication SLA timing requirement
]