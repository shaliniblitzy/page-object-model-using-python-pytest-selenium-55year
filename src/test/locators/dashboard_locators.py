"""
This module contains locators for the Storydoc dashboard page.

The locators are used to identify elements on the dashboard page for
automated testing, following the Page Object Model pattern.
"""

from selenium.webdriver.common.by import By  # 4.10+

class DashboardLocators:
    """Class containing locators for elements on the Storydoc dashboard page.
    
    These locators are used by the DashboardPage class to interact with elements
    on the dashboard page, such as navigation, creating stories, and managing
    existing stories.
    """
    
    # Navigation and menu locators
    DASHBOARD_NAV = (By.CSS_SELECTOR, ".dashboard-nav")
    SETTINGS_MENU = (By.CSS_SELECTOR, ".settings-menu")
    PROFILE_MENU = (By.CSS_SELECTOR, ".profile-menu")
    
    # Story creation locators
    NEW_STORY_BUTTON = (By.CSS_SELECTOR, "button.create-story, .new-story-button")
    
    # Story list locators
    STORY_LIST = (By.CSS_SELECTOR, ".story-list")
    STORY_ITEMS = (By.CSS_SELECTOR, ".story-item")
    
    # Story action buttons
    EDIT_BUTTON = (By.CSS_SELECTOR, ".edit-button")
    SHARE_BUTTON = (By.CSS_SELECTOR, ".share-button")
    DELETE_BUTTON = (By.CSS_SELECTOR, ".delete-button")