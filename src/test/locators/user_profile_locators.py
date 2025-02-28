from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators

class UserProfileLocators(BaseLocators):
    """
    Locators for identifying elements on the user profile page of the Storydoc application
    """
    
    # Profile menu and navigation
    PROFILE_MENU_BUTTON = (By.CSS_SELECTOR, ".profile-menu-button")
    PROFILE_SETTINGS_LINK = (By.CSS_SELECTOR, ".profile-settings-link")
    
    # Profile information fields
    DISPLAY_NAME_FIELD = (By.ID, "display-name")
    EMAIL_FIELD = (By.ID, "email")
    
    # Password change fields
    CURRENT_PASSWORD_FIELD = (By.ID, "current-password")
    NEW_PASSWORD_FIELD = (By.ID, "new-password")
    CONFIRM_PASSWORD_FIELD = (By.ID, "confirm-password")
    
    # Action buttons
    SAVE_PROFILE_BUTTON = (By.CSS_SELECTOR, ".save-profile-button")
    CHANGE_PASSWORD_BUTTON = (By.CSS_SELECTOR, ".change-password-button")
    
    # Profile picture elements
    PROFILE_PICTURE = (By.CSS_SELECTOR, ".profile-picture")
    UPLOAD_PICTURE_BUTTON = (By.CSS_SELECTOR, ".upload-picture-button")
    
    # Account deletion elements
    DELETE_ACCOUNT_BUTTON = (By.CSS_SELECTOR, ".delete-account-button")
    CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, ".confirm-delete-button")
    CANCEL_DELETE_BUTTON = (By.CSS_SELECTOR, ".cancel-delete-button")
    
    # Status messages
    PROFILE_UPDATED_MESSAGE = (By.CSS_SELECTOR, ".profile-updated-message")
    PASSWORD_UPDATED_MESSAGE = (By.CSS_SELECTOR, ".password-updated-message")
    PASSWORD_ERROR_MESSAGE = (By.CSS_SELECTOR, ".password-error-message")
    PROFILE_ERROR_MESSAGE = (By.CSS_SELECTOR, ".profile-error-message")
    
    # Notification settings
    EMAIL_NOTIFICATIONS_TOGGLE = (By.CSS_SELECTOR, ".email-notifications-toggle")