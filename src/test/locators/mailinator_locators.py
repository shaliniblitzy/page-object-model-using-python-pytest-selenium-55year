"""
Locators for the Mailinator email service interface.

This module defines UI element locators for interacting with the Mailinator
public email service, which is used to verify emails during user registration
and story sharing testing workflows.
"""

from selenium.webdriver.common.by import By  # version: 4.10+

# Internal imports
from src.test.locators.base_locators import BaseLocators
from src.test.config.mailinator_config import get_public_inbox_url, EMAIL_SUBJECT_CONFIG

# Public Mailinator inbox URL
PUBLIC_MAILINATOR_URL = "https://www.mailinator.com/v4/public/inboxes.jsp"


class MailinatorLocators(BaseLocators):
    """
    Contains locators for interacting with the Mailinator public email service interface
    """
    # Inbox access elements
    INBOX_INPUT = (By.ID, "inbox_field")
    GO_BUTTON = (By.CSS_SELECTOR, "button.primary-btn")
    REFRESH_BUTTON = (By.CSS_SELECTOR, "button.refresh-btn, button[title='Refresh']")
    
    # Email list elements
    EMAIL_LIST = (By.CSS_SELECTOR, "div.primary-table, table.table-striped")
    EMAIL_ROW = (By.CSS_SELECTOR, "tr.even, tr.odd, tr.clickable")
    EMAIL_SENDER = (By.CSS_SELECTOR, "td.sender, td:nth-child(1)")
    EMAIL_SUBJECT = (By.CSS_SELECTOR, "td.subject, td:nth-child(2)")
    EMAIL_RECEIVED_TIME = (By.CSS_SELECTOR, "td.time, td:nth-child(3)")
    
    # Email content elements
    EMAIL_CONTENT_IFRAME = (By.ID, "html_msg_body")
    EMAIL_BODY = (By.CSS_SELECTOR, "body")
    EMAIL_LINKS = (By.CSS_SELECTOR, "a")
    
    # Verification-specific elements
    VERIFICATION_LINK = (By.XPATH, "//a[contains(@href, 'verify') or contains(@href, 'confirm') or contains(@href, 'activate')]")
    SHARING_LINK = (By.XPATH, "//a[contains(@href, 'shared') or contains(@href, 'story') or contains(@href, 'view')]")
    
    # Status messages
    NO_EMAILS_MESSAGE = (By.CSS_SELECTOR, ".empty-message, .no-messages")


class MailinatorEmailLocators(BaseLocators):
    """
    Contains locators for Storydoc-specific emails in Mailinator
    """
    # Specific email rows by subject
    REGISTRATION_EMAIL_ROW = (By.XPATH, f"//tr[contains(., '{EMAIL_SUBJECT_CONFIG['registration']}')]")
    SHARING_EMAIL_ROW = (By.XPATH, f"//tr[contains(., '{EMAIL_SUBJECT_CONFIG['sharing']}')]")
    
    # Specific links in emails
    REGISTRATION_VERIFICATION_LINK = (By.XPATH, f"//a[contains(@href, 'verify') or contains(@href, 'confirm') or contains(@href, 'activate')]")
    SHARING_LINK = (By.XPATH, f"//a[contains(@href, 'shared') or contains(@href, 'story') or contains(@href, 'view')]")