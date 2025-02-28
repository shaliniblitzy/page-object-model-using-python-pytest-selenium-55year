"""
Initialization file for the story sharing test package that defines test modules, constants, 
and utility functions specific to story sharing feature tests. This package organizes test 
cases for validating the story sharing functionality, including interface interaction, 
recipient validation, email delivery verification, and shared story access.
"""

import pytest  # pytest 7.3+
from ...utilities.logger import get_logger
from ...utilities.email_helper import EmailHelper
from ...pages.share_dialog_page import ShareDialogPage
from ...config.config import get_config

# Initialize logger
logger = get_logger(__name__)

# Constants for story sharing tests
SHARING_TIMEOUT = 60
DEFAULT_PERSONAL_MESSAGE = "Check out this story I created in Storydoc!"
TEST_MODULES = [
    "test_sharing_interface",
    "test_recipient_validation",
    "test_share_story",
    "test_email_delivery",
    "test_sharing_confirmation",
    "test_access_shared_story",
    "test_sharing_permissions"
]

# Test data for email validation tests
INVALID_EMAIL_FORMATS = [
    "invalid",
    "invalid@",
    "@example.com",
    "invalid@invalid"
]

def get_test_modules():
    """
    Returns a list of all test modules in the story sharing package
    
    Returns:
        list: List of test module names in the story sharing package
    """
    return TEST_MODULES

def get_sharing_timeout():
    """
    Returns the configured timeout value for sharing operations
    
    Returns:
        int: Timeout value in seconds
    """
    # Get timeout from configuration or use default SHARING_TIMEOUT
    return get_config("timeout_story_sharing", SHARING_TIMEOUT)

def pytest_configure(config):
    """
    pytest hook to configure the story sharing test package
    
    Args:
        config: pytest configuration object
    """
    # Register story sharing specific markers
    config.addinivalue_line(
        "markers", "story_sharing_ui: mark tests that validate story sharing UI elements"
    )
    config.addinivalue_line(
        "markers", "story_sharing_email: mark tests that validate email delivery for shared stories"
    )
    config.addinivalue_line(
        "markers", "story_sharing_validation: mark tests that validate input validation for story sharing"
    )
    config.addinivalue_line(
        "markers", "story_sharing_integration: mark tests that validate end-to-end story sharing functionality"
    )
    
    logger.info("Registered pytest markers for story sharing tests")

class SharingTestHelper:
    """
    Helper class for story sharing tests providing common functionality
    """
    
    def __init__(self):
        """
        Initialize a new SharingTestHelper instance
        """
        # Initialize email_helper for verifying shared emails
        self.email_helper = EmailHelper()
        logger.info("Initialized SharingTestHelper")
    
    def verify_sharing_flow(self, driver, recipient_email, personal_message=None):
        """
        Verify the complete story sharing flow from dialog to email verification
        
        Args:
            driver: WebDriver instance
            recipient_email: Email address of the recipient
            personal_message: Optional personal message to include
            
        Returns:
            bool: True if sharing flow completes successfully, False otherwise
        """
        try:
            # Initialize share dialog page
            share_dialog = ShareDialogPage(driver)
            
            # Complete sharing with recipient_email and personal_message
            personal_message = personal_message or DEFAULT_PERSONAL_MESSAGE
            sharing_success = share_dialog.complete_sharing(recipient_email, personal_message)
            
            if not sharing_success:
                logger.error(f"Failed to complete sharing to {recipient_email}")
                return False
                
            # Verify email delivery 
            email_verified = share_dialog.verify_sharing_email(recipient_email)
            
            if not email_verified:
                logger.error(f"Failed to verify sharing email delivery to {recipient_email}")
                return False
                
            logger.info(f"Successfully verified sharing flow to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error in sharing flow verification: {str(e)}")
            return False
    
    def extract_sharing_link(self, recipient_email, timeout=None):
        """
        Extract sharing link from the received email
        
        Args:
            recipient_email: Recipient email address
            timeout: Timeout in seconds for waiting for email
            
        Returns:
            str: Sharing link or None if not found
        """
        try:
            # Use default timeout if not specified
            if timeout is None:
                timeout = get_sharing_timeout()
                
            # Wait for email with subject 'Story shared with you'
            message = self.email_helper.wait_for_email(
                recipient_email,
                "Story shared with you",
                timeout
            )
            
            if not message:
                logger.error(f"No sharing email found for {recipient_email}")
                return None
                
            # Extract verification link
            sharing_link = self.email_helper.extract_verification_link(message)
            
            if sharing_link:
                logger.info(f"Successfully extracted sharing link for {recipient_email}")
            else:
                logger.error(f"Failed to extract sharing link from email to {recipient_email}")
                
            return sharing_link
            
        except Exception as e:
            logger.error(f"Error extracting sharing link: {str(e)}")
            return None