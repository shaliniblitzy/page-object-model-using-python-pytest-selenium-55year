"""
Page object for the Shared Story view in the Storydoc application.

This class represents the page that appears when a user accesses a story via a sharing link.
It implements the Page Object Model pattern to encapsulate interactions with the shared story interface,
enabling verification of story sharing functionality from the recipient's perspective.
"""

import time
import urllib.parse
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from .base_page import BasePage
from ..locators.shared_story_locators import SharedStoryLocators
from ..config.timeout_config import PAGE_LOAD_TIMEOUT, ELEMENT_TIMEOUT, get_timeout
from ..utilities.logger import log_info, log_error

# Constants for shared story URLs and timeouts
SHARED_STORY_URL_PATTERN = "shared"
SHARED_STORY_ACCESS_TIMEOUT = 30


class SharedStoryPage(BasePage):
    """
    Page object representing the Shared Story view in the Storydoc application, providing methods
    for verifying and interacting with shared stories.
    """

    def __init__(self, driver):
        """
        Initialize a new SharedStoryPage instance
        
        Args:
            driver: WebDriver instance for browser interaction
        """
        super().__init__(driver, page_name="Shared Story")
        self.shared_link = None
        log_info("Initialized SharedStoryPage")

    def navigate_to_shared_story(self, link):
        """
        Navigate to a shared story using the provided link
        
        Args:
            link: URL of the shared story
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            # Validate that the link contains the shared story pattern
            if SHARED_STORY_URL_PATTERN not in link:
                log_error(f"Invalid shared story link: {link}")
                return False

            self.shared_link = link
            log_info(f"Navigating to shared story: {link}")

            # Navigate to the URL
            self.driver.get(link)

            # Wait for page to load
            self.wait_for_page_ready()

            return self.is_loaded()
        except Exception as e:
            log_error(f"Failed to navigate to shared story: {str(e)}")
            self.take_screenshot("shared_story_navigation_failure")
            return False

    def is_loaded(self, timeout=ELEMENT_TIMEOUT):
        """
        Check if the shared story page is loaded successfully
        
        Args:
            timeout: Maximum time to wait for the page to load
            
        Returns:
            bool: True if the page is loaded, False otherwise
        """
        try:
            # Check if story container is visible
            story_container_visible = self.is_element_visible(
                SharedStoryLocators.STORY_CONTAINER, timeout)
            
            # Check if story title is visible
            story_title_visible = self.is_element_visible(
                SharedStoryLocators.STORY_TITLE, timeout)
            
            # Page is considered loaded if both elements are visible
            is_loaded = story_container_visible and story_title_visible
            
            log_info(f"Shared story page loaded: {is_loaded}")
            return is_loaded
        except Exception as e:
            log_error(f"Error checking if shared story page is loaded: {str(e)}")
            return False

    def get_story_title(self):
        """
        Get the title of the shared story
        
        Returns:
            str: The story title or empty string if not found
        """
        try:
            if not self.is_loaded():
                log_error("Cannot get story title - page not loaded")
                return ""
            
            title = self.get_text(SharedStoryLocators.STORY_TITLE)
            log_info(f"Retrieved story title: {title}")
            return title
        except Exception as e:
            log_error(f"Failed to get story title: {str(e)}")
            return ""

    def get_story_content(self):
        """
        Get the content of the shared story
        
        Returns:
            str: The story content or empty string if not found
        """
        try:
            if not self.is_loaded():
                log_error("Cannot get story content - page not loaded")
                return ""
            
            content = self.get_text(SharedStoryLocators.STORY_CONTENT)
            log_info(f"Retrieved story content (length: {len(content)})")
            return content
        except Exception as e:
            log_error(f"Failed to get story content: {str(e)}")
            return ""

    def get_shared_by_info(self):
        """
        Get information about who shared the story
        
        Returns:
            str: Information about who shared the story or empty string if not found
        """
        try:
            if not self.is_element_visible(SharedStoryLocators.SHARED_BY_INFO):
                log_error("Shared by info not visible")
                return ""
            
            shared_by = self.get_text(SharedStoryLocators.SHARED_BY_INFO)
            log_info(f"Retrieved shared by info: {shared_by}")
            return shared_by
        except Exception as e:
            log_error(f"Failed to get shared by info: {str(e)}")
            return ""

    def navigate_to_next_section(self):
        """
        Navigate to the next section of the shared story
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            if not self.is_element_visible(SharedStoryLocators.NEXT_BUTTON):
                log_error("Next button not visible")
                return False
            
            # Get current section info before clicking
            current_section = self.get_current_section()
            
            # Click the next button
            self.click(SharedStoryLocators.NEXT_BUTTON)
            
            # Wait for content to update
            time.sleep(0.5)  # Short wait for animation
            
            # Check if section changed
            new_section = self.get_current_section()
            success = new_section != current_section
            
            log_info(f"Navigated to next section: {success}")
            return success
        except Exception as e:
            log_error(f"Failed to navigate to next section: {str(e)}")
            return False

    def navigate_to_previous_section(self):
        """
        Navigate to the previous section of the shared story
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            if not self.is_element_visible(SharedStoryLocators.PREVIOUS_BUTTON):
                log_error("Previous button not visible")
                return False
            
            # Get current section info before clicking
            current_section = self.get_current_section()
            
            # Click the previous button
            self.click(SharedStoryLocators.PREVIOUS_BUTTON)
            
            # Wait for content to update
            time.sleep(0.5)  # Short wait for animation
            
            # Check if section changed
            new_section = self.get_current_section()
            success = new_section != current_section
            
            log_info(f"Navigated to previous section: {success}")
            return success
        except Exception as e:
            log_error(f"Failed to navigate to previous section: {str(e)}")
            return False

    def get_current_section(self):
        """
        Get the current section information from pagination indicator
        
        Returns:
            str: Current section information or empty string if not found
        """
        try:
            if not self.is_element_visible(SharedStoryLocators.PAGINATION_INDICATOR):
                return ""
            
            pagination_text = self.get_text(SharedStoryLocators.PAGINATION_INDICATOR)
            log_info(f"Current section: {pagination_text}")
            return pagination_text
        except Exception as e:
            log_error(f"Failed to get current section: {str(e)}")
            return ""

    def has_viewer_controls(self):
        """
        Check if the story viewer has controls (next/previous buttons, etc.)
        
        Returns:
            bool: True if viewer controls are present, False otherwise
        """
        is_visible = self.is_element_visible(SharedStoryLocators.VIEWER_CONTROLS)
        log_info(f"Viewer controls present: {is_visible}")
        return is_visible

    def is_access_restricted(self):
        """
        Check if access to the shared story is restricted
        
        Returns:
            bool: True if access is restricted, False otherwise
        """
        # Check for access restriction message
        restricted_message = self.is_element_visible(SharedStoryLocators.ACCESS_RESTRICTED_MESSAGE)
        
        # Check for login prompt
        login_prompt = self.is_element_visible(SharedStoryLocators.LOGIN_PROMPT)
        
        is_restricted = restricted_message or login_prompt
        log_info(f"Access is restricted: {is_restricted}")
        return is_restricted

    def has_story_expired(self):
        """
        Check if the shared story link has expired
        
        Returns:
            bool: True if story has expired, False otherwise
        """
        is_expired = self.is_element_visible(SharedStoryLocators.EXPIRATION_MESSAGE)
        log_info(f"Story has expired: {is_expired}")
        return is_expired

    def is_download_available(self):
        """
        Check if download option is available for the shared story
        
        Returns:
            bool: True if download is available, False otherwise
        """
        is_available = self.is_element_visible(SharedStoryLocators.DOWNLOAD_BUTTON)
        log_info(f"Download is available: {is_available}")
        return is_available

    def is_fullscreen_available(self):
        """
        Check if fullscreen option is available for the shared story
        
        Returns:
            bool: True if fullscreen is available, False otherwise
        """
        is_available = self.is_element_visible(SharedStoryLocators.FULLSCREEN_BUTTON)
        log_info(f"Fullscreen is available: {is_available}")
        return is_available

    def enter_fullscreen(self):
        """
        Enter fullscreen mode for the shared story
        
        Returns:
            bool: True if fullscreen mode was entered, False otherwise
        """
        try:
            if not self.is_fullscreen_available():
                log_error("Fullscreen button not available")
                return False
            
            self.click(SharedStoryLocators.FULLSCREEN_BUTTON)
            
            # Wait for fullscreen mode to activate
            time.sleep(1)
            
            # Check if we're in fullscreen mode (implementation dependent)
            # This is a placeholder - actual implementation would need to verify fullscreen state
            log_info("Entered fullscreen mode")
            return True
        except Exception as e:
            log_error(f"Failed to enter fullscreen mode: {str(e)}")
            return False

    def download_story(self):
        """
        Download the shared story
        
        Returns:
            bool: True if download was initiated, False otherwise
        """
        try:
            if not self.is_download_available():
                log_error("Download button not available")
                return False
            
            self.click(SharedStoryLocators.DOWNLOAD_BUTTON)
            
            # Wait for download to initiate
            time.sleep(1)
            
            # Since we can't easily verify the download completed in the browser,
            # we just return True if the click was successful
            log_info("Initiated story download")
            return True
        except Exception as e:
            log_error(f"Failed to download story: {str(e)}")
            return False

    def provide_feedback(self):
        """
        Provide feedback on the shared story if feedback button is available
        
        Returns:
            bool: True if feedback was provided, False otherwise
        """
        try:
            if not self.is_element_visible(SharedStoryLocators.FEEDBACK_BUTTON):
                log_error("Feedback button not available")
                return False
            
            self.click(SharedStoryLocators.FEEDBACK_BUTTON)
            
            # Wait for feedback interface to load
            time.sleep(1)
            
            # This is a placeholder - actual implementation would need to fill in and submit feedback
            log_info("Opened feedback interface")
            return True
        except Exception as e:
            log_error(f"Failed to provide feedback: {str(e)}")
            return False

    def verify_story_access(self, expected_title=None, verify_content=True):
        """
        Verify that the shared story can be accessed and viewed
        
        Args:
            expected_title: Expected title of the story (optional)
            verify_content: Whether to verify that story content is not empty
            
        Returns:
            bool: True if story is accessible and content can be verified, False otherwise
        """
        try:
            # Check if page is loaded
            if not self.is_loaded(timeout=SHARED_STORY_ACCESS_TIMEOUT):
                log_error("Shared story page not loaded")
                return False
            
            # Check if access is restricted
            if self.is_access_restricted():
                log_error("Access to shared story is restricted")
                return False
            
            # Check if story has expired
            if self.has_story_expired():
                log_error("Shared story link has expired")
                return False
            
            # Verify story title if expected title is provided
            if expected_title:
                actual_title = self.get_story_title()
                if expected_title not in actual_title:
                    log_error(f"Story title mismatch. Expected: {expected_title}, Actual: {actual_title}")
                    return False
            
            # Verify that content is not empty if requested
            if verify_content:
                content = self.get_story_content()
                if not content.strip():
                    log_error("Story content is empty")
                    return False
            
            log_info("Shared story access verification successful")
            return True
        except Exception as e:
            log_error(f"Failed to verify shared story access: {str(e)}")
            self.take_screenshot("shared_story_verification_failure")
            return False