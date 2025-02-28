"""
Page object for the Dashboard page in the Storydoc application.
Implements methods for interacting with the dashboard UI elements following the Page Object Model pattern.
Provides functionality for navigating to story creation, accessing existing stories, and sharing stories directly from the dashboard.
"""

import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from .base_page import BasePage
from ..locators.dashboard_locators import DashboardLocators
from .story_editor_page import StoryEditorPage
from .share_dialog_page import ShareDialogPage
from ..config.timeout_config import get_page_timeout
from ..utilities.logger import log_info, log_error, log_debug


class DashboardPage(BasePage):
    """
    Page object representing the Dashboard page in the Storydoc application,
    providing methods for interacting with the dashboard UI elements
    """
    
    def __init__(self, driver):
        """
        Initialize a new DashboardPage instance
        
        Args:
            driver: WebDriver instance
        """
        # Call parent class constructor with driver
        super().__init__(driver)
        
        # Set URL for the dashboard page
        self.url = "https://editor-staging.storydoc.com/dashboard"
        
        # Set dashboard timeout from configuration
        self.dashboard_timeout = get_page_timeout("load")
        
        # Log page initialization
        log_info("Initialized Dashboard page object")
    
    def is_loaded(self):
        """
        Check if the Dashboard page is fully loaded
        
        Returns:
            bool: True if the page is loaded, False otherwise
        """
        # Check if dashboard navigation is visible
        nav_visible = self.is_element_visible(DashboardLocators.DASHBOARD_NAV)
        
        # Check if new story button is visible
        button_visible = self.is_element_visible(DashboardLocators.NEW_STORY_BUTTON)
        
        # Check if story list container is visible
        list_visible = self.is_element_visible(DashboardLocators.STORY_LIST)
        
        # Return True if all elements are visible, False otherwise
        result = nav_visible and button_visible and list_visible
        
        log_debug(f"Dashboard page is {'loaded' if result else 'not fully loaded'}")
        return result
    
    def wait_for_dashboard_load(self, timeout=None):
        """
        Wait for the Dashboard page to fully load
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if the dashboard loaded within the timeout, False otherwise
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.dashboard_timeout
        
        try:
            # Wait for dashboard navigation to be visible
            self.wait_for_element(DashboardLocators.DASHBOARD_NAV, timeout=timeout)
            
            # Wait for new story button to be visible
            self.wait_for_element(DashboardLocators.NEW_STORY_BUTTON, timeout=timeout)
            
            # Wait for story list to be visible
            self.wait_for_element(DashboardLocators.STORY_LIST, timeout=timeout)
            
            # Wait for page to be fully loaded
            self.wait_for_page_ready()
            
            log_info("Dashboard page loaded successfully")
            return True
        except TimeoutException:
            log_error(f"Timeout waiting for dashboard to load after {timeout} seconds")
            return False
        except Exception as e:
            log_error(f"Error waiting for dashboard to load: {str(e)}")
            return False
    
    def click_create_story_button(self):
        """
        Click the Create Story button to navigate to story editor
        
        Returns:
            StoryEditorPage: StoryEditorPage instance if navigation successful, None otherwise
        """
        log_info("Attempting to create new story")
        
        try:
            # Click the new story button
            self.click(DashboardLocators.NEW_STORY_BUTTON)
            
            # Wait for page navigation to complete
            self.wait_for_page_ready()
            
            # Create and return a new StoryEditorPage instance
            story_editor_page = StoryEditorPage(self.driver)
            
            # Wait for story editor to load
            if story_editor_page.wait_for_editor_load():
                log_info("Successfully navigated to story editor")
                return story_editor_page
            
            log_error("Story editor did not load after clicking create button")
            return None
        except Exception as e:
            log_error(f"Error creating new story: {str(e)}")
            self.take_screenshot("create_story_error")
            return None
    
    def get_story_list(self):
        """
        Get list of stories displayed on the dashboard
        
        Returns:
            list: List of story elements or empty list if none found
        """
        log_info("Getting list of stories")
        
        try:
            # Wait for story list container to be visible
            self.wait_for_element(DashboardLocators.STORY_LIST)
            
            # Find all story items
            story_elements = self.find_elements(DashboardLocators.STORY_ITEMS)
            
            log_info(f"Found {len(story_elements)} stories")
            return story_elements
        except Exception as e:
            log_error(f"Error getting story list: {str(e)}")
            return []
    
    def is_story_present(self, story_title):
        """
        Check if a story with the given title exists on the dashboard
        
        Args:
            story_title: Title of the story to check
            
        Returns:
            bool: True if story exists, False otherwise
        """
        log_info(f"Checking if story '{story_title}' exists")
        
        try:
            # Get list of stories
            stories = self.get_story_list()
            
            # Check each story for the matching title
            for story in stories:
                # Try to find text that matches the story title
                story_text = story.text
                if story_title in story_text:
                    log_info(f"Story '{story_title}' found")
                    return True
            
            log_info(f"Story '{story_title}' not found")
            return False
        except Exception as e:
            log_error(f"Error checking for story presence: {str(e)}")
            return False
    
    def open_story(self, story_title):
        """
        Open a story with the given title
        
        Args:
            story_title: Title of the story to open
            
        Returns:
            StoryEditorPage: StoryEditorPage instance if operation successful, None otherwise
        """
        log_info(f"Attempting to open story: {story_title}")
        
        try:
            # Get list of stories
            stories = self.get_story_list()
            
            # Find the story with matching title
            for story in stories:
                # Check if story title matches
                if story_title in story.text:
                    # Find and click the edit button within this story
                    edit_buttons = story.find_elements(By.CSS_SELECTOR, DashboardLocators.EDIT_BUTTON[1])
                    
                    if edit_buttons:
                        # Click the first edit button
                        edit_buttons[0].click()
                        
                        # Wait for page navigation to complete
                        self.wait_for_page_ready()
                        
                        # Create and return a new StoryEditorPage instance
                        story_editor_page = StoryEditorPage(self.driver)
                        
                        # Wait for story editor to load
                        if story_editor_page.wait_for_editor_load():
                            log_info(f"Successfully opened story: {story_title}")
                            return story_editor_page
            
            log_error(f"Story '{story_title}' not found or could not be opened")
            return None
        except Exception as e:
            log_error(f"Error opening story: {str(e)}")
            self.take_screenshot("open_story_error")
            return None
    
    def delete_story(self, story_title, confirm_deletion=True):
        """
        Delete a story with the given title
        
        Args:
            story_title: Title of the story to delete
            confirm_deletion: Whether to confirm deletion if prompted
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        log_info(f"Attempting to delete story: {story_title}")
        
        try:
            # Get list of stories
            stories = self.get_story_list()
            
            # Find the story with matching title
            for story in stories:
                # Check if story title matches
                if story_title in story.text:
                    # Find the delete button within this story
                    delete_buttons = story.find_elements(By.CSS_SELECTOR, DashboardLocators.DELETE_BUTTON[1])
                    
                    if delete_buttons:
                        # Click the first delete button
                        delete_buttons[0].click()
                        
                        # Handle confirmation dialog if needed
                        if confirm_deletion:
                            # Wait for confirmation dialog and confirm
                            confirm_button = self.wait_for_element((By.CSS_SELECTOR, ".confirm-delete-button"))
                            if confirm_button:
                                confirm_button.click()
                        
                        # Wait for deletion to complete
                        time.sleep(1)
                        
                        # Refresh the dashboard to see changes
                        self.refresh_dashboard()
                        
                        # Verify deletion by checking story is no longer present
                        if not self.is_story_present(story_title):
                            log_info(f"Successfully deleted story: {story_title}")
                            return True
                        
                        log_error(f"Story '{story_title}' still present after deletion attempt")
                        return False
            
            log_error(f"Story '{story_title}' not found for deletion")
            return False
        except Exception as e:
            log_error(f"Error deleting story: {str(e)}")
            self.take_screenshot("delete_story_error")
            return False
    
    def share_story(self, story_title):
        """
        Share a story with the given title
        
        Args:
            story_title: Title of the story to share
            
        Returns:
            ShareDialogPage: ShareDialogPage instance if operation successful, None otherwise
        """
        log_info(f"Attempting to share story: {story_title}")
        
        try:
            # Get list of stories
            stories = self.get_story_list()
            
            # Find the story with matching title
            for story in stories:
                # Check if story title matches
                if story_title in story.text:
                    # Find the share button within this story
                    share_buttons = story.find_elements(By.CSS_SELECTOR, DashboardLocators.SHARE_BUTTON[1])
                    
                    if share_buttons:
                        # Click the first share button
                        share_buttons[0].click()
                        
                        # Wait for share dialog to appear
                        time.sleep(1)
                        
                        # Create and return a new ShareDialogPage instance
                        share_dialog = ShareDialogPage(self.driver)
                        
                        # Check if dialog is open
                        if share_dialog.is_dialog_open():
                            log_info(f"Successfully opened share dialog for story: {story_title}")
                            return share_dialog
                        
                        log_error(f"Share dialog did not appear for story: {story_title}")
                        return None
            
            log_error(f"Story '{story_title}' not found for sharing")
            return None
        except Exception as e:
            log_error(f"Error sharing story: {str(e)}")
            self.take_screenshot("share_story_error")
            return None
    
    def refresh_dashboard(self):
        """
        Refresh the dashboard page
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        log_info("Refreshing dashboard")
        
        try:
            # Refresh the page
            self.driver.refresh()
            
            # Wait for dashboard to load after refresh
            result = self.wait_for_dashboard_load()
            
            if result:
                log_info("Dashboard refreshed successfully")
            else:
                log_error("Dashboard did not load properly after refresh")
            
            return result
        except Exception as e:
            log_error(f"Error refreshing dashboard: {str(e)}")
            return False
    
    def get_story_count(self):
        """
        Get the number of stories on the dashboard
        
        Returns:
            int: Number of stories found
        """
        log_info("Getting story count")
        
        # Get story list and return its length
        stories = self.get_story_list()
        count = len(stories)
        
        log_info(f"Found {count} stories")
        return count
    
    def wait_for_story_to_appear(self, story_title, timeout=None, polling_interval=1):
        """
        Wait for a story with the given title to appear on the dashboard
        
        Args:
            story_title: Title of the story to wait for
            timeout: Maximum time to wait in seconds
            polling_interval: Time between checks in seconds
            
        Returns:
            bool: True if story appears within the timeout, False otherwise
        """
        log_info(f"Waiting for story '{story_title}' to appear")
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.dashboard_timeout
        
        # Record start time
        start_time = time.time()
        
        # Check repeatedly until timeout
        while (time.time() - start_time) < timeout:
            # Check if story is present
            if self.is_story_present(story_title):
                log_info(f"Story '{story_title}' appeared after {time.time() - start_time:.2f} seconds")
                return True
            
            # Wait before checking again
            time.sleep(polling_interval)
        
        log_error(f"Story '{story_title}' did not appear within {timeout} seconds")
        return False