"""
Page object class for handling notifications in the Storydoc application.
Provides methods to verify, interact with, and wait for various types of notifications
that appear during user workflows such as registration, authentication, story creation, and sharing.
"""

# Standard library imports
import time

# External imports - Selenium WebDriver (version 4.10+)
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Internal imports
from ..pages.base_page import BasePage
from ..locators.notification_locators import NotificationLocators
from ..config.timeout_config import ELEMENT_TIMEOUT, ELEMENT_DISAPPEAR_TIMEOUT
from ..utilities.logger import log_info, log_debug, log_error


class NotificationPage(BasePage):
    """Page object class for handling notification elements in the Storydoc application"""

    def __init__(self, driver):
        """
        Initialize the NotificationPage with a WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        
        # Map notification types to their locators
        self.notification_types = {
            'success': NotificationLocators.SUCCESS_NOTIFICATION,
            'error': NotificationLocators.ERROR_NOTIFICATION,
            'info': NotificationLocators.INFO_NOTIFICATION,
            'warning': NotificationLocators.WARNING_NOTIFICATION
        }
        
        log_info("Initialized NotificationPage")

    def is_notification_displayed(self, notification_type='success'):
        """
        Check if a notification is currently displayed
        
        Args:
            notification_type: Type of notification ('success', 'error', 'info', 'warning')
            
        Returns:
            bool: True if notification is displayed, False otherwise
        """
        log_debug(f"Checking if {notification_type} notification is displayed")
        
        # Get the appropriate locator based on notification type
        locator = self.notification_types.get(notification_type.lower(), NotificationLocators.SUCCESS_NOTIFICATION)
        
        # Check if the notification is visible
        return self.is_element_visible(locator, ELEMENT_TIMEOUT)

    def get_notification_message(self):
        """
        Get the text content of the notification message
        
        Returns:
            str: The text message of the notification or empty string if not found
        """
        log_debug("Getting notification message text")
        
        # First check if any notification container is visible
        if self.is_element_visible(NotificationLocators.NOTIFICATION_CONTAINER):
            # Get the message text
            return self.get_text(NotificationLocators.NOTIFICATION_MESSAGE)
        
        return ""

    def get_notification_title(self):
        """
        Get the title of the notification
        
        Returns:
            str: The title of the notification or empty string if not found
        """
        log_debug("Getting notification title text")
        
        # First check if any notification container is visible
        if self.is_element_visible(NotificationLocators.NOTIFICATION_CONTAINER):
            # Get the title text
            return self.get_text(NotificationLocators.NOTIFICATION_TITLE)
        
        return ""

    def close_notification(self):
        """
        Close the notification by clicking the close button
        
        Returns:
            bool: True if notification was closed successfully, False otherwise
        """
        log_debug("Attempting to close notification")
        
        # Check if notification container is displayed
        if self.is_element_visible(NotificationLocators.NOTIFICATION_CONTAINER):
            # Click the close button
            self.click(NotificationLocators.NOTIFICATION_CLOSE_BUTTON)
            
            # Wait for notification to disappear
            return self.wait_for_element_to_disappear(NotificationLocators.NOTIFICATION_CONTAINER, ELEMENT_DISAPPEAR_TIMEOUT)
        
        return False

    def wait_for_notification(self, notification_type='success', timeout=ELEMENT_TIMEOUT):
        """
        Wait for a notification to appear
        
        Args:
            notification_type: Type of notification ('success', 'error', 'info', 'warning')
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if notification appeared within timeout, False otherwise
        """
        log_debug(f"Waiting for {notification_type} notification to appear (timeout: {timeout}s)")
        
        # Get the appropriate locator based on notification type
        locator = self.notification_types.get(notification_type.lower(), NotificationLocators.SUCCESS_NOTIFICATION)
        
        # Wait for the notification to be visible
        return self.wait_for_element(locator, timeout) is not None

    def wait_for_notification_to_disappear(self, notification_type='success', timeout=ELEMENT_DISAPPEAR_TIMEOUT):
        """
        Wait for a notification to disappear
        
        Args:
            notification_type: Type of notification ('success', 'error', 'info', 'warning')
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if notification disappeared within timeout, False otherwise
        """
        log_debug(f"Waiting for {notification_type} notification to disappear (timeout: {timeout}s)")
        
        # Get the appropriate locator based on notification type
        locator = self.notification_types.get(notification_type.lower(), NotificationLocators.SUCCESS_NOTIFICATION)
        
        # Wait for the notification to disappear
        return self.wait_for_element_to_disappear(locator, timeout)

    def is_success_notification_displayed(self):
        """
        Check if a success notification is displayed
        
        Returns:
            bool: True if success notification is displayed, False otherwise
        """
        return self.is_notification_displayed('success')

    def is_error_notification_displayed(self):
        """
        Check if an error notification is displayed
        
        Returns:
            bool: True if error notification is displayed, False otherwise
        """
        return self.is_notification_displayed('error')

    def is_info_notification_displayed(self):
        """
        Check if an info notification is displayed
        
        Returns:
            bool: True if info notification is displayed, False otherwise
        """
        return self.is_notification_displayed('info')

    def is_warning_notification_displayed(self):
        """
        Check if a warning notification is displayed
        
        Returns:
            bool: True if warning notification is displayed, False otherwise
        """
        return self.is_notification_displayed('warning')

    def wait_for_success_notification(self, timeout=ELEMENT_TIMEOUT):
        """
        Wait for a success notification to appear
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if success notification appeared within timeout, False otherwise
        """
        return self.wait_for_notification('success', timeout)

    def wait_for_error_notification(self, timeout=ELEMENT_TIMEOUT):
        """
        Wait for an error notification to appear
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if error notification appeared within timeout, False otherwise
        """
        return self.wait_for_notification('error', timeout)

    def is_signup_success_notification_displayed(self):
        """
        Check if signup success notification is displayed
        
        Returns:
            bool: True if signup success notification is displayed, False otherwise
        """
        return self.is_element_visible(NotificationLocators.SIGNUP_SUCCESS_NOTIFICATION, ELEMENT_TIMEOUT)

    def is_signin_success_notification_displayed(self):
        """
        Check if signin success notification is displayed
        
        Returns:
            bool: True if signin success notification is displayed, False otherwise
        """
        return self.is_element_visible(NotificationLocators.SIGNIN_SUCCESS_NOTIFICATION, ELEMENT_TIMEOUT)

    def is_story_saved_notification_displayed(self):
        """
        Check if story saved notification is displayed
        
        Returns:
            bool: True if story saved notification is displayed, False otherwise
        """
        return self.is_element_visible(NotificationLocators.STORY_SAVED_NOTIFICATION, ELEMENT_TIMEOUT)

    def is_story_shared_notification_displayed(self):
        """
        Check if story shared notification is displayed
        
        Returns:
            bool: True if story shared notification is displayed, False otherwise
        """
        return self.is_element_visible(NotificationLocators.STORY_SHARED_NOTIFICATION, ELEMENT_TIMEOUT)

    def wait_for_notification_with_text(self, expected_text, timeout=ELEMENT_TIMEOUT):
        """
        Wait for a notification containing specific text
        
        Args:
            expected_text: Text expected to be in the notification
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if notification with text appeared within timeout, False otherwise
        """
        log_debug(f"Waiting for notification containing text: '{expected_text}' (timeout: {timeout}s)")
        
        # Wait for notification container to be visible
        if self.wait_for_element(NotificationLocators.NOTIFICATION_CONTAINER, timeout):
            # Get the notification message text
            message = self.get_notification_message()
            
            # Check if the expected text is in the message
            return expected_text in message
        
        return False