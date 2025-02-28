from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators


class SharedStoryLocators(BaseLocators):
    """
    Class containing locator definitions for the Shared Story view in the Storydoc application.
    These locators are used to identify and interact with UI elements when a user accesses
    a shared story through a sharing link.
    """
    
    # Main container that holds the shared story content
    STORY_CONTAINER = (By.CSS_SELECTOR, ".story-container")
    
    # Story title element
    STORY_TITLE = (By.CSS_SELECTOR, ".story-title")
    
    # Main content area of the story
    STORY_CONTENT = (By.CSS_SELECTOR, ".story-content")
    
    # Information about who shared the story
    SHARED_BY_INFO = (By.CSS_SELECTOR, ".shared-by-info")
    
    # Container for viewer controls (next, previous, etc.)
    VIEWER_CONTROLS = (By.CSS_SELECTOR, ".viewer-controls")
    
    # Button to navigate to the next page/slide of the story
    NEXT_BUTTON = (By.CSS_SELECTOR, ".next-button")
    
    # Button to navigate to the previous page/slide of the story
    PREVIOUS_BUTTON = (By.CSS_SELECTOR, ".previous-button")
    
    # Indicator showing current page/slide number and total
    PAGINATION_INDICATOR = (By.CSS_SELECTOR, ".pagination-indicator")
    
    # Button to provide feedback on the shared story
    FEEDBACK_BUTTON = (By.CSS_SELECTOR, ".feedback-button")
    
    # Button to download the story (if available)
    DOWNLOAD_BUTTON = (By.CSS_SELECTOR, ".download-button")
    
    # Button to toggle fullscreen mode
    FULLSCREEN_BUTTON = (By.CSS_SELECTOR, ".fullscreen-button")
    
    # Message shown when access to the story is restricted
    ACCESS_RESTRICTED_MESSAGE = (By.CSS_SELECTOR, ".access-restricted-message")
    
    # Prompt encouraging users to login for full access
    LOGIN_PROMPT = (By.CSS_SELECTOR, ".login-prompt")
    
    # Message indicating the shared link has expired
    EXPIRATION_MESSAGE = (By.CSS_SELECTOR, ".expiration-message")