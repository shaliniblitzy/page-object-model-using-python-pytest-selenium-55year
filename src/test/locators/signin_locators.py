from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators

class SigninLocators(BaseLocators):
    """
    Contains locators for elements on the Storydoc sign-in page.
    These locators are used by the SigninPage class to interact with UI elements 
    during test automation of the user authentication feature.
    """
    
    # Email input field
    EMAIL_FIELD = (By.ID, "email")
    
    # Password input field
    PASSWORD_FIELD = (By.ID, "password")
    
    # Sign-in button
    SIGNIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    # Main error message for invalid credentials
    SIGNIN_ERROR_MESSAGE = (By.CSS_SELECTOR, ".signin-error")
    
    # Specific error message for email field
    EMAIL_ERROR_MESSAGE = (By.CSS_SELECTOR, "#email-error")
    
    # Specific error message for password field
    PASSWORD_ERROR_MESSAGE = (By.CSS_SELECTOR, "#password-error")
    
    # Remember me checkbox
    REMEMBER_ME_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    
    # Forgot password link
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot password?")
    
    # Sign up link for new users
    SIGNUP_LINK = (By.LINK_TEXT, "Sign up")