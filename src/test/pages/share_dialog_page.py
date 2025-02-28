"""
Page object for the Share Dialog in the Storydoc application.
Implements the Page Object Model pattern to encapsulate interactions with the sharing interface,
enabling test automation of the story sharing functionality.
"""

import time  # standard library
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # version: 4.10+

from .base_page import BasePage
from ..locators.share_dialog_locators import ShareDialogLocators
from ..config.timeout_config import STORY_SHARING_TIMEOUT, get_timeout
from ..utilities.logger import log_info, log_error
from ..utilities.email_helper import EmailHelper


class ShareDialogPage(BasePage):
    """
    Page object representing the Share Dialog in the Storydoc application,
    providing methods for sharing stories with recipients.
    """
    
    def __init__(self, driver):
        """
        Initialize a new ShareDialogPage instance
        
        Args:
            driver: WebDriver instance
        """
        # Call parent class constructor with driver and page name 'Share Dialog'
        super().__init__(driver, page_name="Share Dialog")
        
        # Initialize email_helper for verifying shared emails
        self.email_helper = EmailHelper()
        
        # Set sharing timeout from configuration
        self.sharing_timeout = get_timeout("story_sharing", STORY_SHARING_TIMEOUT)
        
        # Log page initialization
        log_info("Initialized Share Dialog page object")
    
    def is_dialog_open(self):
        """
        Check if the Share Dialog is open
        
        Returns:
            bool: True if the dialog is open, False otherwise
        """
        # Check if dialog container is visible
        dialog_visible = self.is_element_visible(ShareDialogLocators.DIALOG_CONTAINER)
        
        # Check if dialog title is visible
        title_visible = self.is_element_visible(ShareDialogLocators.DIALOG_TITLE)
        
        # Return True if both elements are visible, False otherwise
        result = dialog_visible and title_visible
        
        # Log result of dialog open check
        log_info(f"Share dialog is {'open' if result else 'not open'}")
        
        return result
    
    def wait_for_dialog(self, timeout=None):
        """
        Wait for the Share Dialog to appear
        
        Args:
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            bool: True if dialog appears within timeout, False otherwise
        """
        # Use default sharing timeout if not specified
        if timeout is None:
            timeout = self.sharing_timeout
        
        try:
            # Wait for dialog container to be visible
            self.wait_for_element(ShareDialogLocators.DIALOG_CONTAINER, timeout=timeout)
            
            # Wait for dialog title to be visible
            self.wait_for_element(ShareDialogLocators.DIALOG_TITLE, timeout=timeout)
            
            # Return True if dialog appears within timeout
            log_info(f"Share dialog appeared within {timeout} seconds")
            return True
        
        except TimeoutException:
            # Handle timeouts and return False if dialog doesn't appear
            log_error(f"Timed out waiting for share dialog to appear after {timeout} seconds")
            return False
        
        except Exception as e:
            # Log any other exceptions
            log_error(f"Error waiting for share dialog: {str(e)}")
            return False
    
    def enter_recipient_email(self, email):
        """
        Enter recipient email address in the dialog
        
        Args:
            email (str): Email address of the recipient
            
        Returns:
            bool: True if email was entered successfully, False otherwise
        """
        # Log attempt to enter recipient email
        log_info(f"Entering recipient email: {email}")
        
        try:
            # Input the provided email into the recipient email field
            result = self.input_text(ShareDialogLocators.RECIPIENT_EMAIL_INPUT, email)
            
            # Return True if email entry was successful, False otherwise
            if result:
                log_info(f"Successfully entered recipient email: {email}")
            else:
                log_error(f"Failed to enter recipient email: {email}")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error entering recipient email: {str(e)}")
            return False
    
    def enter_personal_message(self, message):
        """
        Enter an optional personal message
        
        Args:
            message (str): Personal message to include in the sharing email
            
        Returns:
            bool: True if message was entered successfully, False otherwise
        """
        # Log attempt to enter personal message
        log_info(f"Entering personal message: {message}")
        
        try:
            # Input the provided message into the personal message textarea
            result = self.input_text(ShareDialogLocators.PERSONAL_MESSAGE_TEXTAREA, message)
            
            # Return True if message entry was successful, False otherwise
            if result:
                log_info("Successfully entered personal message")
            else:
                log_error("Failed to enter personal message")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error entering personal message: {str(e)}")
            return False
    
    def click_share_button(self):
        """
        Click the Share button to submit sharing request
        
        Returns:
            bool: True if click was successful, False otherwise
        """
        # Log attempt to click share button
        log_info("Clicking share button")
        
        try:
            # Click the share button element
            result = self.click(ShareDialogLocators.SHARE_BUTTON)
            
            # Return True if click was successful, False otherwise
            if result:
                log_info("Successfully clicked share button")
            else:
                log_error("Failed to click share button")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error clicking share button: {str(e)}")
            return False
    
    def click_cancel_button(self):
        """
        Click the Cancel button to dismiss dialog without sharing
        
        Returns:
            bool: True if click was successful, False otherwise
        """
        # Log attempt to click cancel button
        log_info("Clicking cancel button")
        
        try:
            # Click the cancel button element
            result = self.click(ShareDialogLocators.CANCEL_BUTTON)
            
            # Return True if click was successful, False otherwise
            if result:
                log_info("Successfully clicked cancel button")
            else:
                log_error("Failed to click cancel button")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error clicking cancel button: {str(e)}")
            return False
    
    def click_close_button(self):
        """
        Click the X close button to dismiss dialog
        
        Returns:
            bool: True if click was successful, False otherwise
        """
        # Log attempt to click close button
        log_info("Clicking close button")
        
        try:
            # Click the close button element
            result = self.click(ShareDialogLocators.CLOSE_BUTTON)
            
            # Return True if click was successful, False otherwise
            if result:
                log_info("Successfully clicked close button")
            else:
                log_error("Failed to click close button")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error clicking close button: {str(e)}")
            return False
    
    def add_additional_recipient(self):
        """
        Add an additional recipient by clicking add recipient button
        
        Returns:
            bool: True if click was successful, False otherwise
        """
        # Log attempt to add additional recipient
        log_info("Adding additional recipient")
        
        try:
            # Click the add recipient button
            result = self.click(ShareDialogLocators.ADD_RECIPIENT_BUTTON)
            
            # Return True if click was successful, False otherwise
            if result:
                log_info("Successfully added additional recipient")
            else:
                log_error("Failed to add additional recipient")
            
            return result
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error adding additional recipient: {str(e)}")
            return False
    
    def is_sharing_successful(self):
        """
        Check if sharing was successful by looking for success message
        
        Returns:
            bool: True if sharing success message is visible, False otherwise
        """
        # Log attempt to check sharing status
        log_info("Checking if sharing was successful")
        
        # Check if sharing success message is visible
        result = self.is_element_visible(ShareDialogLocators.SHARE_SUCCESS_MESSAGE)
        
        # Return True if message is visible, False otherwise
        if result:
            log_info("Sharing was successful, success message is visible")
        else:
            log_info("Sharing success message not visible")
        
        return result
    
    def is_recipient_email_error_shown(self):
        """
        Check if there's an error related to the recipient email
        
        Returns:
            bool: True if recipient error message is visible, False otherwise
        """
        # Log attempt to check recipient email error
        log_info("Checking if recipient email error is shown")
        
        # Check if recipient error message is visible
        result = self.is_element_visible(ShareDialogLocators.RECIPIENT_ERROR_MESSAGE)
        
        # Return True if error is visible, False otherwise
        if result:
            log_info("Recipient email error is visible")
        else:
            log_info("No recipient email error shown")
        
        return result
    
    def wait_for_sharing_complete(self, timeout=None):
        """
        Wait for the sharing operation to complete
        
        Args:
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            bool: True if sharing completes within timeout, False otherwise
        """
        # Use default sharing timeout if not specified
        if timeout is None:
            timeout = self.sharing_timeout
        
        try:
            # Wait for either sharing success message or error message to appear
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if self.is_sharing_successful():
                    log_info("Sharing completed successfully")
                    return True
                
                if self.is_recipient_email_error_shown():
                    log_error("Sharing failed, recipient email error shown")
                    return False
                
                # Wait briefly before checking again
                time.sleep(0.5)
            
            # If timeout reached without success or error message
            log_error(f"Timed out waiting for sharing operation to complete after {timeout} seconds")
            return False
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error waiting for sharing completion: {str(e)}")
            return False
    
    def complete_sharing(self, email, message=None, verify_delivery=False):
        """
        Complete the entire sharing process with a recipient
        
        Args:
            email (str): Recipient email address
            message (str, optional): Optional personal message
            verify_delivery (bool): Whether to verify email delivery
            
        Returns:
            bool: True if sharing was successful, False otherwise
        """
        # Log attempt to complete sharing process
        log_info(f"Starting complete sharing process with recipient: {email}")
        
        try:
            # Check if dialog is open, wait for it if not
            if not self.is_dialog_open():
                if not self.wait_for_dialog():
                    log_error("Share dialog not visible, cannot complete sharing")
                    return False
            
            # Enter recipient email
            if not self.enter_recipient_email(email):
                return False
            
            # Enter personal message if provided
            if message:
                if not self.enter_personal_message(message):
                    # Continue even if entering message fails
                    log_info("Failed to enter message but continuing with sharing")
            
            # Click share button
            if not self.click_share_button():
                return False
            
            # Wait for sharing operation to complete
            if not self.wait_for_sharing_complete():
                return False
            
            # Check if sharing was successful
            success = self.is_sharing_successful()
            
            # If verify_delivery is True, verify email was received by recipient
            if success and verify_delivery:
                log_info(f"Verifying email delivery to {email}")
                email_received = self.verify_sharing_email(email)
                
                if not email_received:
                    log_error(f"Sharing email not received by {email}")
                    return False
            
            # Return True if entire process was successful, False otherwise
            log_info(f"Share dialog process completed {'successfully' if success else 'with errors'}")
            return success
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error in complete sharing process: {str(e)}")
            return False
    
    def verify_sharing_email(self, recipient_email, timeout=None):
        """
        Verify that sharing email was received by the recipient
        
        Args:
            recipient_email (str): Recipient email address
            timeout (int, optional): Maximum time to wait in seconds
            
        Returns:
            bool: True if email was received, False otherwise
        """
        # Log attempt to verify sharing email
        log_info(f"Verifying sharing email was received by: {recipient_email}")
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.sharing_timeout
        
        try:
            # Use email_helper to verify that email with subject 'Story shared with you' was received
            email_received = self.email_helper.verify_email_received(
                recipient_email, 
                "Story shared with you",
                timeout
            )
            
            # Return True if email was received within timeout, False otherwise
            if email_received:
                log_info(f"Sharing email successfully received by {recipient_email}")
            else:
                log_error(f"Sharing email not received by {recipient_email} within {timeout} seconds")
            
            return email_received
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error verifying sharing email: {str(e)}")
            return False
    
    def get_sharing_link(self, recipient_email, timeout=None):
        """
        Get the sharing link from the received email
        
        Args:
            recipient_email (str): Recipient email address
            timeout (int, optional): Maximum time to wait in seconds
            
        Returns:
            str: Sharing link from email or None if not found
        """
        # Log attempt to get sharing link
        log_info(f"Getting sharing link from email sent to: {recipient_email}")
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.sharing_timeout
        
        try:
            # Use email_helper to wait for email with subject 'Story shared with you'
            message = self.email_helper.wait_for_email(
                recipient_email,
                "Story shared with you",
                timeout
            )
            
            if not message:
                log_error(f"No sharing email found for {recipient_email}")
                return None
            
            # Extract verification link from the email
            sharing_link = self.email_helper.extract_verification_link(message)
            
            # Return the sharing link or None if not found
            if sharing_link:
                log_info(f"Extracted sharing link: {sharing_link}")
            else:
                log_error("No sharing link found in email")
            
            return sharing_link
        
        except Exception as e:
            # Log any exceptions
            log_error(f"Error getting sharing link: {str(e)}")
            return None