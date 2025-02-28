from selenium.webdriver.common.by import By  # version: 4.10+

class BaseLocators:
    """
    Defines base locators used across multiple pages in the application for common UI elements.
    These locators represent common elements that appear consistently throughout the Storydoc application.
    """
    
    # Common loading indicator, typically shown during page loads or AJAX requests
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading-spinner")
    
    # Common error message container shown when operations fail
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    
    # Common success message container shown when operations succeed
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".success-message")
    
    # Common submit button used in forms throughout the application
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    # Common cancel button used in dialogs and forms
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".cancel-button")
    
    # Common close button (X) used in dialogs and notifications
    CLOSE_BUTTON = (By.CSS_SELECTOR, ".close-button")
    
    # User menu/profile dropdown typically found in the navigation header
    USER_MENU = (By.CSS_SELECTOR, ".user-menu")
    
    # Notification element for displaying system notifications
    NOTIFICATION = (By.CSS_SELECTOR, ".notification")