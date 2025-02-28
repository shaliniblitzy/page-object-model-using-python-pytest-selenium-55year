"""
Module containing locators for error messages and error-related UI elements in the Storydoc application.
These locators are used by page objects and tests to identify and interact with error elements
during test automation of various error scenarios.
"""

from selenium.webdriver.common.by import By  # version 4.10+

class ErrorLocators:
    """Class containing locators for error messages and error-related UI elements across the Storydoc application"""
    
    # General error locators
    GENERAL_ERROR = (By.CSS_SELECTOR, ".error-message, .alert-error, [data-testid='error-message']")
    FIELD_ERROR = (By.CSS_SELECTOR, ".field-error, .form-field-error, .invalid-feedback")
    VALIDATION_ERROR = (By.CSS_SELECTOR, ".validation-error, [data-error='validation']")
    FORM_ERROR = (By.CSS_SELECTOR, ".form-error, form .error-summary")
    
    # Authentication-related error locators
    AUTHENTICATION_ERROR = (By.CSS_SELECTOR, ".auth-error, .login-error, [data-testid='auth-error']")
    REGISTRATION_ERROR = (By.CSS_SELECTOR, ".registration-error, .signup-error, [data-testid='registration-error']")
    EMAIL_FORMAT_ERROR = (By.CSS_SELECTOR, "[data-field='email'] .error-message, #email-error, .email-error")
    PASSWORD_STRENGTH_ERROR = (By.CSS_SELECTOR, "[data-field='password'] .error-message, #password-error, .password-error")
    TERMS_AGREEMENT_ERROR = (By.CSS_SELECTOR, "[data-field='terms'] .error-message, #terms-error, .terms-error")
    INVALID_CREDENTIALS_ERROR = (By.CSS_SELECTOR, ".invalid-credentials, .credentials-error, [data-testid='credentials-error']")
    
    # Network and server error locators
    NETWORK_ERROR = (By.CSS_SELECTOR, ".network-error, .connection-error, [data-testid='network-error']")
    SERVER_ERROR = (By.CSS_SELECTOR, ".server-error, .api-error, [data-testid='server-error']")
    TIMEOUT_ERROR = (By.CSS_SELECTOR, ".timeout-error, .request-timeout, [data-testid='timeout-error']")
    
    # Content-related error locators
    STORY_CREATION_ERROR = (By.CSS_SELECTOR, ".story-creation-error, .content-error, [data-testid='story-error']")
    SHARING_ERROR = (By.CSS_SELECTOR, ".sharing-error, .share-error, [data-testid='sharing-error']")
    EMAIL_DELIVERY_ERROR = (By.CSS_SELECTOR, ".email-delivery-error, .email-send-error, [data-testid='email-error']")
    
    # Error dialog locators
    ERROR_DIALOG = (By.CSS_SELECTOR, ".error-dialog, .modal-error, dialog.error")
    ERROR_DIALOG_CLOSE = (By.CSS_SELECTOR, ".error-dialog .close-button, .modal-error .close, dialog.error .close")