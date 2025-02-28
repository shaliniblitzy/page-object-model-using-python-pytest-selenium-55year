"""
Page object class for handling error pages and error states in the Storydoc application.
This class provides methods to detect, verify, and interact with various error messages
and error conditions that may occur during test execution.
"""

# Standard library imports
import re
from typing import Dict, Optional, Union

# External imports
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Internal imports
from .base_page import BasePage
from ..locators.error_locators import ErrorLocators
from ..utilities.wait_helper import WaitUtils
from ..utilities.logger import log_info, log_error, log_debug

# Dictionary mapping error type names to their corresponding locators
ERROR_TYPES: dict[str, tuple] = {
    'general': ErrorLocators.GENERAL_ERROR,
    'field': ErrorLocators.FIELD_ERROR,
    'validation': ErrorLocators.VALIDATION_ERROR,
    'form': ErrorLocators.FORM_ERROR,
    'authentication': ErrorLocators.AUTHENTICATION_ERROR,
    'registration': ErrorLocators.REGISTRATION_ERROR,
    'email_format': ErrorLocators.EMAIL_FORMAT_ERROR,
    'password_strength': ErrorLocators.PASSWORD_STRENGTH_ERROR,
    'terms_agreement': ErrorLocators.TERMS_AGREEMENT_ERROR,
    'invalid_credentials': ErrorLocators.INVALID_CREDENTIALS_ERROR,
    'network': ErrorLocators.NETWORK_ERROR,
    'server': ErrorLocators.SERVER_ERROR,
    'timeout': ErrorLocators.TIMEOUT_ERROR,
    'story_creation': ErrorLocators.STORY_CREATION_ERROR,
    'sharing': ErrorLocators.SHARING_ERROR,
    'email_delivery': ErrorLocators.EMAIL_DELIVERY_ERROR
}

# Default timeout for error-related operations
DEFAULT_ERROR_TIMEOUT: float = 5.0


class ErrorPage(BasePage):
    """Page object for handling error pages and error states in the Storydoc application."""

    def __init__(self, driver: WebDriver):
        """
        Initialize the ErrorPage object with WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.last_error_details: dict[str, str] = {}

    def is_error_displayed(self, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Check if any error message is displayed on the page
        
        Args:
            timeout: Maximum time to wait for error element
            
        Returns:
            True if any error message is displayed, False otherwise
        """
        log_info("Checking if any error message is displayed")
        
        for error_type, locator in ERROR_TYPES.items():
            if self.is_element_visible(locator, timeout):
                error_text = self.get_text(locator)
                log_debug(f"Found error of type '{error_type}': {error_text}")
                self.last_error_details = {
                    'type': error_type,
                    'message': error_text,
                    'locator': str(locator)
                }
                return True
        
        return False

    def is_specific_error_displayed(self, error_type: str, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Check if a specific type of error message is displayed
        
        Args:
            error_type: Type of error to check for (key in ERROR_TYPES dictionary)
            timeout: Maximum time to wait for error element
            
        Returns:
            True if the specified error is displayed, False otherwise
        """
        log_info(f"Checking if '{error_type}' error is displayed")
        
        if error_type not in ERROR_TYPES:
            log_error(f"Unknown error type: {error_type}. Available types: {', '.join(ERROR_TYPES.keys())}")
            return False
            
        locator = ERROR_TYPES[error_type]
        if self.is_element_visible(locator, timeout):
            error_text = self.get_text(locator)
            log_debug(f"Found '{error_type}' error: {error_text}")
            self.last_error_details = {
                'type': error_type,
                'message': error_text,
                'locator': str(locator)
            }
            return True
            
        return False

    def get_error_message(self, error_type: str, timeout: float = DEFAULT_ERROR_TIMEOUT) -> str:
        """
        Get the text of an error message
        
        Args:
            error_type: Type of error to get message for (key in ERROR_TYPES dictionary)
            timeout: Maximum time to wait for error element
            
        Returns:
            Error message text or empty string if not found
        """
        log_info(f"Getting error message for error type: {error_type}")
        
        if error_type not in ERROR_TYPES:
            log_error(f"Unknown error type: {error_type}. Available types: {', '.join(ERROR_TYPES.keys())}")
            return ""
            
        locator = ERROR_TYPES[error_type]
        error_text = self.get_text(locator)
        
        if error_text:
            self.last_error_details = {
                'type': error_type,
                'message': error_text,
                'locator': str(locator)
            }
            
        return error_text

    def get_all_error_messages(self, timeout: float = DEFAULT_ERROR_TIMEOUT) -> dict[str, str]:
        """
        Get a dictionary of all displayed error messages
        
        Args:
            timeout: Maximum time to wait for error elements
            
        Returns:
            Dictionary mapping error types to their messages
        """
        log_info("Getting all displayed error messages")
        
        results = {}
        for error_type, locator in ERROR_TYPES.items():
            if self.is_element_visible(locator, timeout):
                error_text = self.get_text(locator)
                if error_text:
                    results[error_type] = error_text
                    log_debug(f"Found '{error_type}' error: {error_text}")
        
        if results:
            self.last_error_details = {
                'types': ', '.join(results.keys()),
                'messages': results
            }
            
        return results

    def error_message_contains(self, error_type: str, expected_text: str, 
                              case_sensitive: bool = False, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Check if an error message contains specific text
        
        Args:
            error_type: Type of error to check (key in ERROR_TYPES dictionary)
            expected_text: Text to search for in the error message
            case_sensitive: Whether to perform case-sensitive comparison
            timeout: Maximum time to wait for error element
            
        Returns:
            True if error message contains the expected text, False otherwise
        """
        log_info(f"Checking if '{error_type}' error contains text: '{expected_text}'")
        
        error_message = self.get_error_message(error_type, timeout)
        if not error_message:
            return False
            
        if not case_sensitive:
            error_message = error_message.lower()
            expected_text = expected_text.lower()
            
        return expected_text in error_message

    def error_message_matches(self, error_type: str, pattern: str, 
                             timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Check if an error message matches a regular expression pattern
        
        Args:
            error_type: Type of error to check (key in ERROR_TYPES dictionary)
            pattern: Regular expression pattern to match
            timeout: Maximum time to wait for error element
            
        Returns:
            True if error message matches the pattern, False otherwise
        """
        log_info(f"Checking if '{error_type}' error matches pattern: '{pattern}'")
        
        error_message = self.get_error_message(error_type, timeout)
        if not error_message:
            return False
            
        regex = re.compile(pattern)
        return bool(regex.search(error_message))

    def dismiss_error(self, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Dismiss an error dialog if present
        
        Args:
            timeout: Maximum time to wait for error dialog
            
        Returns:
            True if error was dismissed, False otherwise
        """
        log_info("Attempting to dismiss error dialog")
        
        if self.is_element_visible(ErrorLocators.ERROR_DIALOG, timeout):
            try:
                close_button = self.find_element(ErrorLocators.ERROR_DIALOG_CLOSE)
                close_button.click()
                
                # Wait for dialog to disappear
                return self.wait_for_element_to_disappear(ErrorLocators.ERROR_DIALOG, timeout)
            except (NoSuchElementException, TimeoutException) as e:
                log_error(f"Failed to dismiss error dialog: {str(e)}")
                return False
                
        return False

    def capture_error_screenshot(self, error_type: str, filename_prefix: str = "error") -> Optional[str]:
        """
        Capture a screenshot of the current error state
        
        Args:
            error_type: Type of error for filename (key in ERROR_TYPES dictionary)
            filename_prefix: Prefix for the screenshot filename
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        log_info(f"Capturing screenshot for '{error_type}' error")
        
        # Construct filename
        filename = f"{filename_prefix}_{error_type}"
        
        # Take screenshot
        return self.take_screenshot(filename)

    def wait_for_error_to_appear(self, error_type: str, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Wait for a specific error to appear
        
        Args:
            error_type: Type of error to wait for (key in ERROR_TYPES dictionary)
            timeout: Maximum time to wait
            
        Returns:
            True if error appears within timeout, False otherwise
        """
        log_info(f"Waiting for '{error_type}' error to appear")
        
        if error_type not in ERROR_TYPES:
            log_error(f"Unknown error type: {error_type}. Available types: {', '.join(ERROR_TYPES.keys())}")
            return False
            
        locator = ERROR_TYPES[error_type]
        element = self.wait_for_element(locator, 'visible', timeout)
        
        if element:
            error_text = element.text
            self.last_error_details = {
                'type': error_type,
                'message': error_text,
                'locator': str(locator)
            }
            log_debug(f"'{error_type}' error appeared: {error_text}")
            return True
            
        return False

    def wait_for_error_to_disappear(self, error_type: str, timeout: float = DEFAULT_ERROR_TIMEOUT) -> bool:
        """
        Wait for a specific error to disappear
        
        Args:
            error_type: Type of error to wait for (key in ERROR_TYPES dictionary)
            timeout: Maximum time to wait
            
        Returns:
            True if error disappears within timeout, False otherwise
        """
        log_info(f"Waiting for '{error_type}' error to disappear")
        
        if error_type not in ERROR_TYPES:
            log_error(f"Unknown error type: {error_type}. Available types: {', '.join(ERROR_TYPES.keys())}")
            return False
            
        locator = ERROR_TYPES[error_type]
        result = WaitUtils.wait_for_element_state(self.driver, locator, 'invisible', timeout)
        
        if result is None:  # For invisible state, success is None
            log_debug(f"'{error_type}' error disappeared")
            return True
            
        return False

    def get_last_error_details(self) -> dict[str, str]:
        """
        Get the details of the last encountered error
        
        Returns:
            Dictionary with details of the last error
        """
        return self.last_error_details

    def clear_last_error_details(self) -> None:
        """
        Clear the stored last error details
        """
        self.last_error_details = {}