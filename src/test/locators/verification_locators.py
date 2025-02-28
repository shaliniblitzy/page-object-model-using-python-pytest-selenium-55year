from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators


class VerificationLocators(BaseLocators):
    """
    Defines locators for verification-related pages and components in the Storydoc application.
    
    These locators are used to identify elements on verification pages including:
    - Email verification pages after registration
    - Account verification confirmation screens
    - Verification code entry forms
    - Shared story access verification pages
    """
    
    # Email verification elements
    EMAIL_VERIFICATION_HEADING = (By.CSS_SELECTOR, ".email-verification-heading")
    EMAIL_VERIFICATION_SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".email-verification-success")
    EMAIL_VERIFICATION_ERROR_MESSAGE = (By.CSS_SELECTOR, ".email-verification-error")
    
    # Account verification elements
    ACCOUNT_VERIFIED_MESSAGE = (By.CSS_SELECTOR, ".account-verified-message")
    VERIFICATION_LINK_EXPIRED = (By.CSS_SELECTOR, ".verification-link-expired")
    RESEND_VERIFICATION_BUTTON = (By.CSS_SELECTOR, ".resend-verification-button")
    CONTINUE_TO_DASHBOARD_BUTTON = (By.CSS_SELECTOR, ".continue-to-dashboard-button")
    VERIFICATION_CODE_INPUT = (By.CSS_SELECTOR, "input.verification-code")
    VERIFY_CODE_BUTTON = (By.CSS_SELECTOR, ".verify-code-button")
    
    # Shared story access verification elements
    SHARED_STORY_ACCESS_HEADING = (By.CSS_SELECTOR, ".shared-story-heading")
    SHARED_STORY_ACCESS_SUCCESS = (By.CSS_SELECTOR, ".shared-story-access-success")
    SHARED_STORY_ACCESS_ERROR = (By.CSS_SELECTOR, ".shared-story-access-error")