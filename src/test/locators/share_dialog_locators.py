from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators


class ShareDialogLocators(BaseLocators):
    """
    Class containing locator definitions for the Share Dialog in the Storydoc application.
    
    These locators are used by the ShareDialogPage to interact with UI elements in the share dialog,
    enabling test automation of the story sharing functionality.
    """
    
    # Main container for the share dialog
    DIALOG_CONTAINER = (By.CSS_SELECTOR, ".share-dialog-container")
    
    # Title of the share dialog, typically contains text like "Share Story"
    DIALOG_TITLE = (By.CSS_SELECTOR, ".dialog-title")
    
    # Input field for entering recipient email address
    RECIPIENT_EMAIL_INPUT = (By.CSS_SELECTOR, ".recipient-email")
    
    # Textarea for entering an optional personal message to the recipient
    PERSONAL_MESSAGE_TEXTAREA = (By.CSS_SELECTOR, ".personal-message")
    
    # Button to submit the sharing request
    SHARE_BUTTON = (By.CSS_SELECTOR, ".share-button")
    
    # Button to cancel the sharing process and close the dialog
    # Inherits from BaseLocators.CANCEL_BUTTON but can be overridden if needed
    
    # Button to close the sharing dialog (typically an X in the corner)
    # Inherits from BaseLocators.CLOSE_BUTTON but can be overridden if needed
    
    # Success message shown when story is successfully shared
    SHARE_SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".sharing-success")
    
    # Error message shown when recipient email is invalid
    RECIPIENT_ERROR_MESSAGE = (By.CSS_SELECTOR, ".recipient-error")
    
    # Button to add additional recipient to the sharing list
    ADD_RECIPIENT_BUTTON = (By.CSS_SELECTOR, ".add-recipient-button")