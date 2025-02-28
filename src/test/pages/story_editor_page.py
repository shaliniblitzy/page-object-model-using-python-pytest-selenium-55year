"""
Page object for the Story Editor page in the Storydoc application.
Implements the Page Object Model pattern to encapsulate interactions with the story editor UI, 
providing methods for creating, editing, and saving stories. Also includes functionality for 
selecting templates, editing content, and sharing stories.
"""

import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from .base_page import BasePage
from ..locators.story_editor_locators import StoryEditorLocators
from .share_dialog_page import ShareDialogPage
from ..config.timeout_config import STORY_CREATION_TIMEOUT, get_timeout
from ..utilities.wait_helper import WaitUtils
from ..utilities.logger import log_info, log_error, log_debug


class StoryEditorPage(BasePage):
    """
    Page object representing the Story Editor page in the Storydoc application,
    providing methods for creating and editing stories.
    """
    
    def __init__(self, driver):
        """
        Initialize a new StoryEditorPage instance
        
        Args:
            driver: WebDriver instance
        """
        # Call parent class constructor with driver
        super().__init__(driver, page_name="Story Editor")
        
        # Set URL for the story editor page
        self.url = "https://editor-staging.storydoc.com/editor"
        
        # Set editor timeout from configuration
        self.editor_timeout = get_timeout("story_creation", STORY_CREATION_TIMEOUT)
        
        log_info("Initialized Story Editor page object")
    
    def is_loaded(self):
        """
        Check if the Story Editor page is fully loaded
        
        Returns:
            bool: True if the page is loaded, False otherwise
        """
        # Check if the key elements of the editor are visible
        title_input_visible = self.is_element_visible(StoryEditorLocators.STORY_TITLE_INPUT)
        templates_visible = self.is_element_visible(StoryEditorLocators.TEMPLATE_OPTIONS)
        editor_visible = self.is_element_visible(StoryEditorLocators.CONTENT_EDITOR)
        
        # Return True only if all elements are visible
        result = title_input_visible and templates_visible and editor_visible
        
        log_info(f"Story Editor page is {'loaded' if result else 'not fully loaded'}")
        return result
    
    def wait_for_editor_load(self, timeout=None):
        """
        Wait for the Story Editor page to fully load
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if the editor loaded within the timeout, False otherwise
        """
        if timeout is None:
            timeout = self.editor_timeout
        
        log_info(f"Waiting for Story Editor to load (timeout: {timeout}s)")
        
        try:
            # Wait for the page to be ready first
            self.wait_for_page_ready(timeout)
            
            # Wait for title input field to be visible
            title_input = self.wait_for_element(
                StoryEditorLocators.STORY_TITLE_INPUT, 
                timeout=timeout
            )
            
            # Wait for template options to be visible
            templates = self.wait_for_element(
                StoryEditorLocators.TEMPLATE_OPTIONS, 
                timeout=timeout
            )
            
            # Wait for content editor to be visible
            editor = self.wait_for_element(
                StoryEditorLocators.CONTENT_EDITOR, 
                timeout=timeout
            )
            
            # Return True if all elements are found
            result = title_input is not None and templates is not None and editor is not None
            
            log_info(f"Story Editor page {'loaded successfully' if result else 'failed to load completely'}")
            return result
            
        except TimeoutException as e:
            log_error(f"Timeout waiting for Story Editor to load: {str(e)}")
            self.take_screenshot("story_editor_load_timeout")
            return False
        except Exception as e:
            log_error(f"Error waiting for Story Editor to load: {str(e)}")
            self.take_screenshot("story_editor_load_error")
            return False
    
    def enter_story_title(self, title):
        """
        Enter the title for the story
        
        Args:
            title: Title to enter
            
        Returns:
            bool: True if title was entered successfully, False otherwise
        """
        log_info(f"Entering story title: {title}")
        
        try:
            # Input text in the title field
            result = self.input_text(StoryEditorLocators.STORY_TITLE_INPUT, title)
            
            if result:
                log_info(f"Successfully entered story title: {title}")
            else:
                log_error(f"Failed to enter story title: {title}")
            
            return result
        except Exception as e:
            log_error(f"Error entering story title: {str(e)}")
            return False
    
    def get_story_title(self):
        """
        Get the current story title
        
        Returns:
            str: Current story title or empty string if not found
        """
        log_info("Getting current story title")
        
        try:
            # Get the title input element
            title_element = self.wait_for_element(StoryEditorLocators.STORY_TITLE_INPUT)
            
            if title_element:
                # Get the value attribute which contains the title
                title = title_element.get_attribute("value")
                log_info(f"Current story title: {title}")
                return title
            
            log_error("Story title element not found")
            return ""
        except Exception as e:
            log_error(f"Error getting story title: {str(e)}")
            return ""
    
    def is_template_available(self, template_name):
        """
        Check if a specific template is available for selection
        
        Args:
            template_name: Name of the template to check
            
        Returns:
            bool: True if template is available, False otherwise
        """
        log_info(f"Checking if template '{template_name}' is available")
        
        # Get all available templates
        templates = self.get_available_templates()
        
        # Check if the specified template is in the list
        is_available = template_name in templates
        
        log_info(f"Template '{template_name}' is {'available' if is_available else 'not available'}")
        return is_available
    
    def get_available_templates(self):
        """
        Get list of available templates
        
        Returns:
            list: List of template names or empty list if none found
        """
        log_info("Getting available templates")
        
        try:
            # Wait for the template options to be visible
            self.wait_for_element(StoryEditorLocators.TEMPLATE_OPTIONS)
            
            # Find all template elements
            template_elements = self.find_elements(StoryEditorLocators.TEMPLATE_ITEM)
            
            # Extract template names
            templates = []
            for element in template_elements:
                # Try to get name from aria-label or text content
                name = element.get_attribute("aria-label") or element.text.strip()
                if name:
                    templates.append(name)
            
            log_info(f"Found {len(templates)} available templates")
            return templates
        except Exception as e:
            log_error(f"Error getting available templates: {str(e)}")
            return []
    
    def select_template(self, template_name):
        """
        Select a template for the story
        
        Args:
            template_name: Name of the template to select
            
        Returns:
            bool: True if template was selected successfully, False otherwise
        """
        log_info(f"Selecting template: {template_name}")
        
        try:
            # Check if the template is available
            if not self.is_template_available(template_name):
                log_error(f"Template '{template_name}' is not available")
                return False
            
            # Find all template elements
            template_elements = self.find_elements(StoryEditorLocators.TEMPLATE_ITEM)
            
            # Find and click the template with matching name
            for element in template_elements:
                # Get name from aria-label or text content
                name = element.get_attribute("aria-label") or element.text.strip()
                
                if name == template_name:
                    # Scroll to the element and click it
                    self.scroll_to_element(element)
                    element.click()
                    
                    # Wait for the template to be selected
                    if self.wait_for_element(StoryEditorLocators.SELECTED_TEMPLATE, timeout=5):
                        log_info(f"Successfully selected template: {template_name}")
                        return True
            
            # If we reach here, template was not found or not selected
            log_error(f"Failed to select template: {template_name}")
            return False
            
        except Exception as e:
            log_error(f"Error selecting template: {str(e)}")
            self.take_screenshot("template_selection_error")
            return False
    
    def get_selected_template(self):
        """
        Get the currently selected template
        
        Returns:
            str: Name of selected template or None if no selection
        """
        log_info("Getting currently selected template")
        
        try:
            # Try to find the selected template element
            selected_element = self.wait_for_element(StoryEditorLocators.SELECTED_TEMPLATE, timeout=2)
            
            if selected_element:
                # Get name from aria-label or text content
                name = selected_element.get_attribute("aria-label") or selected_element.text.strip()
                log_info(f"Currently selected template: {name}")
                return name
            
            log_info("No template currently selected")
            return None
        except TimeoutException:
            # Not an error, just means no template is selected
            log_info("No template currently selected")
            return None
        except Exception as e:
            log_error(f"Error getting selected template: {str(e)}")
            return None
    
    def input_content(self, content):
        """
        Enter content into the story editor
        
        Args:
            content: Content to enter
            
        Returns:
            bool: True if content was entered successfully, False otherwise
        """
        log_info("Entering content into story editor")
        
        try:
            # Wait for the content editor to be visible and clickable
            editor_element = self.wait_for_element(StoryEditorLocators.CONTENT_EDITOR)
            
            if editor_element:
                # Click to focus on the editor
                editor_element.click()
                
                # Clear existing content
                editor_element.clear()
                
                # Input the new content
                editor_element.send_keys(content)
                
                log_info("Successfully entered content")
                return True
            
            log_error("Content editor element not found")
            return False
        except Exception as e:
            log_error(f"Error entering content: {str(e)}")
            return False
    
    def get_content(self):
        """
        Get the current content from the story editor
        
        Returns:
            str: Current editor content or empty string if not found
        """
        log_info("Getting current editor content")
        
        try:
            # Get the content editor element
            editor_element = self.wait_for_element(StoryEditorLocators.CONTENT_EDITOR)
            
            if editor_element:
                # Get the text content
                content = editor_element.text
                log_info(f"Retrieved content (length: {len(content)} characters)")
                return content
            
            log_error("Content editor element not found")
            return ""
        except Exception as e:
            log_error(f"Error getting editor content: {str(e)}")
            return ""
    
    def save_story(self):
        """
        Save the current story
        
        Returns:
            bool: True if story was saved successfully, False otherwise
        """
        log_info("Saving story")
        
        try:
            # Click the save button
            save_result = self.click(StoryEditorLocators.SAVE_BUTTON)
            
            if not save_result:
                log_error("Failed to click save button")
                return False
            
            # Wait for the save operation to complete (success message or timeout)
            save_success = self.wait_for_element(
                StoryEditorLocators.SAVE_SUCCESS_MESSAGE, 
                timeout=10
            ) is not None
            
            if save_success:
                log_info("Successfully saved story")
            else:
                log_error("Failed to save story - no success message appeared")
            
            return save_success
        except Exception as e:
            log_error(f"Error saving story: {str(e)}")
            self.take_screenshot("save_story_error")
            return False
    
    def is_story_saved(self):
        """
        Check if the story was saved successfully
        
        Returns:
            bool: True if save success message is visible, False otherwise
        """
        log_info("Checking if story is saved")
        
        # Check if save success message is visible
        is_saved = self.is_element_visible(StoryEditorLocators.SAVE_SUCCESS_MESSAGE)
        
        log_info(f"Story is {'saved' if is_saved else 'not saved'}")
        return is_saved
    
    def click_share_button(self):
        """
        Click the Share button to open the sharing dialog
        
        Returns:
            ShareDialogPage: ShareDialogPage instance if dialog appears, None otherwise
        """
        log_info("Clicking share button")
        
        try:
            # Click the share button
            share_result = self.click(StoryEditorLocators.SHARE_BUTTON)
            
            if not share_result:
                log_error("Failed to click share button")
                return None
            
            # Wait a moment for the dialog to appear
            time.sleep(1)
            
            # Create and return a new ShareDialogPage instance
            share_dialog = ShareDialogPage(self.driver)
            
            # Check if the dialog is open
            if share_dialog.is_dialog_open():
                log_info("Successfully opened share dialog")
                return share_dialog
            else:
                log_error("Share dialog did not appear after clicking share button")
                return None
        except Exception as e:
            log_error(f"Error clicking share button: {str(e)}")
            self.take_screenshot("share_button_error")
            return None
    
    def click_preview_button(self):
        """
        Click the Preview button to preview the story
        
        Returns:
            bool: True if preview opens successfully, False otherwise
        """
        log_info("Clicking preview button")
        
        try:
            # Click the preview button
            preview_result = self.click(StoryEditorLocators.PREVIEW_BUTTON)
            
            if not preview_result:
                log_error("Failed to click preview button")
                return False
            
            # For a preview, we likely need to wait for a new window or iframe
            # This depends on how the preview is implemented
            # For now, simply return the click result
            log_info("Successfully clicked preview button")
            return True
        except Exception as e:
            log_error(f"Error clicking preview button: {str(e)}")
            return False
    
    def create_story(self, title, template_name=None, content=None):
        """
        Complete the entire story creation process
        
        Args:
            title: Title for the story
            template_name: Optional template to select
            content: Optional content to enter
            
        Returns:
            bool: True if story was created successfully, False otherwise
        """
        log_info(f"Creating story with title: {title}")
        
        try:
            # Wait for the editor to load
            if not self.wait_for_editor_load():
                log_error("Editor did not load properly, cannot create story")
                return False
            
            # Enter the story title
            if not self.enter_story_title(title):
                log_error("Failed to enter story title")
                return False
            
            # Select template if specified
            if template_name and not self.select_template(template_name):
                log_error(f"Failed to select template: {template_name}")
                # Continue anyway, as template selection might be optional
            
            # Enter content if specified
            if content and not self.input_content(content):
                log_error("Failed to enter content")
                # Continue anyway, as content might be added later
            
            # Save the story
            if not self.save_story():
                log_error("Failed to save story")
                return False
            
            # Check if save was successful
            if not self.is_story_saved():
                log_error("Story was not saved successfully")
                return False
            
            log_info(f"Successfully created story: {title}")
            return True
        except Exception as e:
            log_error(f"Error creating story: {str(e)}")
            self.take_screenshot("create_story_error")
            return False
    
    def share_story(self, recipient_email, message=None):
        """
        Share the current story
        
        Args:
            recipient_email: Email address to share with
            message: Optional personal message
            
        Returns:
            bool: True if story was shared successfully, False otherwise
        """
        log_info(f"Sharing story with recipient: {recipient_email}")
        
        try:
            # Ensure story is saved first
            if not self.is_story_saved():
                log_info("Story not saved, saving before sharing")
                if not self.save_story():
                    log_error("Failed to save story before sharing")
                    return False
            
            # Click the share button to open share dialog
            share_dialog = self.click_share_button()
            
            if not share_dialog:
                log_error("Failed to open share dialog")
                return False
            
            # Use the share dialog to complete the sharing process
            sharing_result = share_dialog.complete_sharing(recipient_email, message)
            
            if sharing_result:
                log_info(f"Successfully shared story with {recipient_email}")
            else:
                log_error(f"Failed to share story with {recipient_email}")
            
            return sharing_result
        except Exception as e:
            log_error(f"Error sharing story: {str(e)}")
            self.take_screenshot("share_story_error")
            return False