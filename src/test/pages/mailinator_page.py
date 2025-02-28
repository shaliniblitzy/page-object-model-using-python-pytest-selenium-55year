"""
Page object implementation for interacting with Mailinator email service UI to verify emails during testing.

Provides methods to access the Mailinator web interface, check inboxes, retrieve emails, and extract
verification links for user registration and story sharing workflows.
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Internal imports
from .base_page import BasePage
from ..locators.mailinator_locators import (
    MailinatorLocators, 
    MailinatorEmailLocators,
    PUBLIC_MAILINATOR_URL
)
from ..config.timeout_config import EMAIL_DELIVERY_TIMEOUT, EMAIL_POLLING_INTERVAL
from ..config.mailinator_config import get_public_inbox_url, EMAIL_SUBJECT_CONFIG
from ..utilities.logger import log_info, log_debug, log_warning, log_error

# Keywords to identify verification and sharing links in emails
VERIFICATION_KEYWORDS = ['verify', 'confirm', 'activate', 'verification']
SHARING_KEYWORDS = ['shared', 'share', 'access', 'view']


class MailinatorPage(BasePage):
    """Page object for interacting with Mailinator email service UI to verify emails during testing"""
    
    def __init__(self, driver):
        """
        Initialize the Mailinator page object
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.url = PUBLIC_MAILINATOR_URL
        log_info("Initialized Mailinator page object")
    
    def navigate_to_inbox(self, email_address):
        """
        Navigate to the Mailinator inbox for a specific email address
        
        Args:
            email_address: Email address to check
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            # Extract username from email address (part before @)
            username = email_address.split('@')[0]
            
            # Navigate to Mailinator public inbox URL
            self.driver.get(self.url)
            
            # Enter the username in the inbox input field
            self.input_text(MailinatorLocators.INBOX_INPUT, username)
            
            # Click the GO button to access the inbox
            self.click(MailinatorLocators.GO_BUTTON)
            
            # Wait for the email list to be visible
            self.wait_for_element(MailinatorLocators.EMAIL_LIST)
            
            log_info(f"Successfully navigated to inbox for {email_address}")
            return True
        except Exception as e:
            log_error(f"Failed to navigate to inbox for {email_address}: {str(e)}")
            self.take_screenshot(f"mailinator_inbox_navigation_failure_{username}")
            return False
    
    def navigate_to_public_inbox_url(self, email_address):
        """
        Navigate to a specifically formatted public inbox URL
        
        Args:
            email_address: Email address to check
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            # Get the formatted URL for the public inbox
            public_url = get_public_inbox_url(email_address)
            
            if not public_url:
                log_error(f"Could not generate public inbox URL for {email_address}")
                return False
            
            # Navigate to the URL
            self.driver.get(public_url)
            
            # Wait for the email list to be visible
            self.wait_for_element(MailinatorLocators.EMAIL_LIST)
            
            log_info(f"Successfully navigated to public inbox URL for {email_address}")
            return True
        except Exception as e:
            log_error(f"Failed to navigate to public inbox URL for {email_address}: {str(e)}")
            self.take_screenshot(f"mailinator_public_url_navigation_failure")
            return False
    
    def refresh_inbox(self):
        """
        Refresh the current Mailinator inbox
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            # Click the refresh button
            self.click(MailinatorLocators.REFRESH_BUTTON)
            
            # Wait for page to reload
            time.sleep(1)  # Brief wait for refresh to complete
            
            log_debug("Refreshed Mailinator inbox")
            return True
        except Exception as e:
            log_error(f"Failed to refresh Mailinator inbox: {str(e)}")
            return False
    
    def is_email_present(self, subject):
        """
        Check if an email with specific subject is present in the inbox
        
        Args:
            subject: Subject of the email to find
            
        Returns:
            bool: True if email is present, False otherwise
        """
        try:
            # Find all email rows in the inbox
            email_rows = self.find_elements(MailinatorLocators.EMAIL_ROW)
            
            # Check if the "no emails" message is displayed
            if self.is_element_visible(MailinatorLocators.NO_EMAILS_MESSAGE):
                log_debug(f"No emails found in inbox")
                return False
            
            # Check each email row for the subject
            for row in email_rows:
                try:
                    subject_element = row.find_element(*MailinatorLocators.EMAIL_SUBJECT)
                    email_subject = subject_element.text
                    
                    if subject.lower() in email_subject.lower():
                        log_info(f"Found email with subject: {subject}")
                        return True
                except Exception:
                    continue
            
            log_debug(f"Email with subject '{subject}' not found")
            return False
        except Exception as e:
            log_error(f"Error checking for email with subject '{subject}': {str(e)}")
            return False
    
    def is_registration_email_present(self):
        """
        Check if a registration email is present in the inbox
        
        Returns:
            bool: True if registration email is present, False otherwise
        """
        registration_subject = EMAIL_SUBJECT_CONFIG.get('registration', 'Welcome to Storydoc')
        return self.is_email_present(registration_subject)
    
    def is_sharing_email_present(self):
        """
        Check if a story sharing email is present in the inbox
        
        Returns:
            bool: True if sharing email is present, False otherwise
        """
        sharing_subject = EMAIL_SUBJECT_CONFIG.get('sharing', 'Story shared with you')
        return self.is_email_present(sharing_subject)
    
    def wait_for_email(self, subject, timeout=None, poll_interval=None):
        """
        Wait for an email with specific subject to appear in the inbox
        
        Args:
            subject: Subject of the email to wait for
            timeout: Maximum time to wait in seconds (default: EMAIL_DELIVERY_TIMEOUT)
            poll_interval: Time between refresh attempts in seconds (default: EMAIL_POLLING_INTERVAL)
            
        Returns:
            bool: True if email appeared within timeout, False otherwise
        """
        # Set default values if not provided
        if timeout is None:
            timeout = EMAIL_DELIVERY_TIMEOUT
        
        if poll_interval is None:
            poll_interval = EMAIL_POLLING_INTERVAL
        
        log_info(f"Waiting for email with subject '{subject}' (timeout: {timeout}s, interval: {poll_interval}s)")
        
        # Record start time
        start_time = time.time()
        
        # Loop until timeout
        while time.time() - start_time < timeout:
            # Check if email is present
            if self.is_email_present(subject):
                elapsed_time = time.time() - start_time
                log_info(f"Email with subject '{subject}' found after {elapsed_time:.2f} seconds")
                return True
            
            # If not found, refresh inbox and wait
            self.refresh_inbox()
            time.sleep(poll_interval)
        
        # If timeout reached without finding the email
        log_warning(f"Timeout waiting for email with subject '{subject}' after {timeout} seconds")
        self.take_screenshot("mailinator_email_timeout")
        return False
    
    def wait_for_registration_email(self, timeout=None, poll_interval=None):
        """
        Wait for registration verification email to appear in the inbox
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between refresh attempts in seconds
            
        Returns:
            bool: True if email appeared within timeout, False otherwise
        """
        registration_subject = EMAIL_SUBJECT_CONFIG.get('registration', 'Welcome to Storydoc')
        return self.wait_for_email(registration_subject, timeout, poll_interval)
    
    def wait_for_sharing_email(self, timeout=None, poll_interval=None):
        """
        Wait for story sharing email to appear in the inbox
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between refresh attempts in seconds
            
        Returns:
            bool: True if email appeared within timeout, False otherwise
        """
        sharing_subject = EMAIL_SUBJECT_CONFIG.get('sharing', 'Story shared with you')
        return self.wait_for_email(sharing_subject, timeout, poll_interval)
    
    def open_email(self, subject):
        """
        Open an email with specific subject
        
        Args:
            subject: Subject of the email to open
            
        Returns:
            bool: True if email opened successfully, False otherwise
        """
        try:
            # Find all email rows
            email_rows = self.find_elements(MailinatorLocators.EMAIL_ROW)
            
            # Find and click the row with matching subject
            for row in email_rows:
                try:
                    subject_element = row.find_element(*MailinatorLocators.EMAIL_SUBJECT)
                    email_subject = subject_element.text
                    
                    if subject.lower() in email_subject.lower():
                        # Click on the row to open the email
                        row.click()
                        
                        # Wait for email content to load
                        time.sleep(2)  # Allow time for the email content to load
                        
                        log_info(f"Opened email with subject: {subject}")
                        return True
                except Exception:
                    continue
            
            log_warning(f"Could not find email with subject: {subject}")
            return False
        except Exception as e:
            log_error(f"Error opening email with subject '{subject}': {str(e)}")
            return False
    
    def open_registration_email(self):
        """
        Open the registration verification email
        
        Returns:
            bool: True if email opened successfully, False otherwise
        """
        registration_subject = EMAIL_SUBJECT_CONFIG.get('registration', 'Welcome to Storydoc')
        return self.open_email(registration_subject)
    
    def open_sharing_email(self):
        """
        Open the story sharing email
        
        Returns:
            bool: True if email opened successfully, False otherwise
        """
        sharing_subject = EMAIL_SUBJECT_CONFIG.get('sharing', 'Story shared with you')
        return self.open_email(sharing_subject)
    
    def get_email_content(self):
        """
        Get the content of the currently opened email
        
        Returns:
            str: Email content as text
        """
        try:
            # Switch to the email content iframe
            self.switch_to_frame(MailinatorLocators.EMAIL_CONTENT_IFRAME)
            
            # Wait for email body to be visible
            email_body = self.wait_for_element(MailinatorLocators.EMAIL_BODY)
            
            # Get the text content
            content = email_body.text if email_body else ""
            
            # Switch back to default content
            self.switch_to_default_content()
            
            log_debug(f"Retrieved email content: {len(content)} characters")
            return content
        except Exception as e:
            log_error(f"Error getting email content: {str(e)}")
            self.switch_to_default_content()  # Ensure we switch back even on error
            return ""
    
    def extract_link_from_email(self, keywords):
        """
        Extract link from the currently opened email based on provided keywords
        
        Args:
            keywords: List of keywords to identify the link
            
        Returns:
            str: Extracted link or empty string if not found
        """
        try:
            # Switch to the email content iframe
            self.switch_to_frame(MailinatorLocators.EMAIL_CONTENT_IFRAME)
            
            # Try to find link elements directly
            link_elements = self.find_elements(MailinatorLocators.EMAIL_LINKS)
            
            # Check each link for keywords
            for link in link_elements:
                href = link.get_attribute('href')
                if href:
                    # Check if any keyword is in the href
                    if any(keyword.lower() in href.lower() for keyword in keywords):
                        log_info(f"Found link containing keywords: {href}")
                        
                        # Switch back to default content
                        self.switch_to_default_content()
                        return href
            
            # If no link found by direct inspection, try getting the full content and using regex
            email_body = self.wait_for_element(MailinatorLocators.EMAIL_BODY)
            if email_body:
                html_content = email_body.get_attribute('innerHTML')
                
                # Find all URLs in the HTML content
                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', html_content)
                
                # Filter URLs by keywords
                for url in urls:
                    if any(keyword.lower() in url.lower() for keyword in keywords):
                        log_info(f"Found link containing keywords via regex: {url}")
                        
                        # Switch back to default content
                        self.switch_to_default_content()
                        return url
            
            # Switch back to default content
            self.switch_to_default_content()
            
            log_warning(f"No link found with keywords: {keywords}")
            return ""
        except Exception as e:
            log_error(f"Error extracting link from email: {str(e)}")
            # Ensure we switch back to default content even on error
            try:
                self.switch_to_default_content()
            except:
                pass
            return ""
    
    def extract_verification_link(self):
        """
        Extract verification link from the currently opened email
        
        Returns:
            str: Verification link or empty string if not found
        """
        return self.extract_link_from_email(VERIFICATION_KEYWORDS)
    
    def extract_sharing_link(self):
        """
        Extract sharing link from the currently opened email
        
        Returns:
            str: Sharing link or empty string if not found
        """
        return self.extract_link_from_email(SHARING_KEYWORDS)
    
    def get_verification_link(self, email_address, timeout=None, poll_interval=None):
        """
        Combined method to find, open registration email and extract verification link
        
        Args:
            email_address: Email address to check
            timeout: Maximum time to wait for email in seconds
            poll_interval: Time between refresh attempts in seconds
            
        Returns:
            str: Verification link if found, empty string otherwise
        """
        # Navigate to the inbox
        if not self.navigate_to_inbox(email_address):
            log_error(f"Failed to navigate to inbox for {email_address}")
            return ""
        
        # Wait for registration email
        registration_subject = EMAIL_SUBJECT_CONFIG.get('registration', 'Welcome to Storydoc')
        if not self.wait_for_email(registration_subject, timeout, poll_interval):
            log_error(f"Registration email not found for {email_address}")
            self.take_screenshot(f"registration_email_not_found_{email_address.split('@')[0]}")
            return ""
        
        # Open the email
        if not self.open_registration_email():
            log_error(f"Failed to open registration email for {email_address}")
            self.take_screenshot(f"open_registration_email_failure_{email_address.split('@')[0]}")
            return ""
        
        # Extract and return the verification link
        verification_link = self.extract_verification_link()
        
        if not verification_link:
            log_error(f"Verification link not found in registration email for {email_address}")
            self.take_screenshot(f"verification_link_not_found_{email_address.split('@')[0]}")
        else:
            log_info(f"Successfully extracted verification link for {email_address}")
        
        return verification_link
    
    def get_sharing_link(self, email_address, timeout=None, poll_interval=None):
        """
        Combined method to find, open sharing email and extract sharing link
        
        Args:
            email_address: Email address to check
            timeout: Maximum time to wait for email in seconds
            poll_interval: Time between refresh attempts in seconds
            
        Returns:
            str: Sharing link if found, empty string otherwise
        """
        # Navigate to the inbox
        if not self.navigate_to_inbox(email_address):
            log_error(f"Failed to navigate to inbox for {email_address}")
            return ""
        
        # Wait for sharing email
        sharing_subject = EMAIL_SUBJECT_CONFIG.get('sharing', 'Story shared with you')
        if not self.wait_for_email(sharing_subject, timeout, poll_interval):
            log_error(f"Sharing email not found for {email_address}")
            self.take_screenshot(f"sharing_email_not_found_{email_address.split('@')[0]}")
            return ""
        
        # Open the email
        if not self.open_sharing_email():
            log_error(f"Failed to open sharing email for {email_address}")
            self.take_screenshot(f"open_sharing_email_failure_{email_address.split('@')[0]}")
            return ""
        
        # Extract and return the sharing link
        sharing_link = self.extract_sharing_link()
        
        if not sharing_link:
            log_error(f"Sharing link not found in email for {email_address}")
            self.take_screenshot(f"sharing_link_not_found_{email_address.split('@')[0]}")
        else:
            log_info(f"Successfully extracted sharing link for {email_address}")
        
        return sharing_link