from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators

class SignupLocators(BaseLocators):
    """
    Locators for Storydoc signup page elements used during test automation
    """
    
    # Full name input field
    NAME_FIELD = (By.ID, "name")
    
    # Email input field for registration
    EMAIL_FIELD = (By.ID, "email")
    
    # Password input field
    PASSWORD_FIELD = (By.ID, "password")
    
    # Terms and conditions checkbox
    TERMS_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    
    # Signup/Create account button - could override the SUBMIT_BUTTON from BaseLocators
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    # Sign in link for existing users
    SIGNIN_LINK = (By.LINK_TEXT, "Sign in")
    
    # Email-specific error message
    EMAIL_ERROR_MESSAGE = (By.CSS_SELECTOR, ".email-error")
    
    # Password-specific error message
    PASSWORD_ERROR_MESSAGE = (By.CSS_SELECTOR, ".password-error")
    
    # Terms agreement error message
    TERMS_ERROR_MESSAGE = (By.CSS_SELECTOR, ".terms-error")
    
    # Successful registration message
    SIGNUP_SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".signup-success")
    
    # Verification email sent message
    VERIFICATION_EMAIL_SENT = (By.CSS_SELECTOR, ".verification-email-sent")