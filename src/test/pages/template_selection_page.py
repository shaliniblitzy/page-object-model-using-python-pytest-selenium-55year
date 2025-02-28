"""
Page object for the template selection page in the Storydoc application, following the Page Object Model pattern.
Provides methods for interacting with the template selection interface, including displaying templates, 
filtering, searching, and selecting templates for story creation.
"""

import time
from typing import List, Optional
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from .base_page import BasePage
from ..locators.template_selection_locators import TemplateSelectionLocators
from .story_editor_page import StoryEditorPage
from ..config.timeout_config import get_page_timeout
from ..utilities.logger import log_info, log_error, log_debug


class TemplateSelectionPage(BasePage):
    """
    Page object representing the template selection page in the Storydoc application,
    providing methods for interacting with the template selection interface.
    """

    def __init__(self, driver):
        """
        Initialize a new TemplateSelectionPage instance

        Args:
            driver: WebDriver instance
        """
        # Call parent class constructor with driver
        super().__init__(driver)
        
        # Set URL for the template selection page
        self.url = "https://editor-staging.storydoc.com/templates"
        
        # Set template selection timeout from configuration
        self.template_selection_timeout = get_page_timeout('load')
        
        # Log page initialization
        log_info("Initialized Template Selection page object")

    def is_loaded(self) -> bool:
        """
        Check if the template selection page is fully loaded

        Returns:
            True if the page is loaded, False otherwise
        """
        # Check if template section is visible
        template_section_visible = self.is_element_visible(TemplateSelectionLocators.TEMPLATE_SECTION)
        
        # Check if template options are visible
        template_options_visible = self.is_element_visible(TemplateSelectionLocators.TEMPLATE_OPTIONS)
        
        # Return True if all elements are visible, False otherwise
        result = template_section_visible and template_options_visible
        
        # Log result of page load check
        log_info(f"Template Selection page is {'loaded' if result else 'not fully loaded'}")
        
        return result

    def wait_for_templates_to_load(self, timeout: float = None) -> bool:
        """
        Wait for templates to load completely

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if templates loaded within the timeout, False otherwise
        """
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.template_selection_timeout
        
        try:
            # Wait for loading indicator to disappear if it's present
            if self.is_element_visible(TemplateSelectionLocators.LOADING_INDICATOR):
                self.wait_for_element_to_disappear(TemplateSelectionLocators.LOADING_INDICATOR, timeout)
            
            # Wait for template items to be visible
            template_items = self.wait_for_element(TemplateSelectionLocators.TEMPLATE_ITEM, timeout)
            
            # Return True if template items are visible
            if template_items:
                log_info("Templates loaded successfully")
                return True
            
            # Return False if template items are not visible
            log_error("Templates failed to load within the timeout")
            return False
            
        except TimeoutException as e:
            # Log timeout error
            log_error(f"Timeout waiting for templates to load: {str(e)}")
            # Take screenshot for debugging
            self.take_screenshot("templates_load_timeout")
            return False
        except Exception as e:
            # Log any other errors
            log_error(f"Error waiting for templates to load: {str(e)}")
            # Take screenshot for debugging
            self.take_screenshot("templates_load_error")
            return False

    def get_available_templates(self) -> List[str]:
        """
        Get a list of all available templates

        Returns:
            List of template names available for selection
        """
        # First make sure templates are loaded
        if not self.wait_for_templates_to_load():
            log_error("Could not get available templates, templates not loaded")
            return []
        
        try:
            # Find all template items
            template_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_ITEM)
            
            # Extract template names from each item
            template_names = []
            for item in template_items:
                try:
                    # Try to find the template name element within the template item
                    name_element = item.find_element(*TemplateSelectionLocators.TEMPLATE_NAME)
                    # Get the text from the name element
                    name = name_element.text.strip()
                    if name:
                        template_names.append(name)
                except NoSuchElementException:
                    # If name element not found, try getting text directly from the item
                    name = item.text.strip()
                    if name:
                        template_names.append(name)
                except Exception as e:
                    # Log any other errors and continue with the next item
                    log_debug(f"Error extracting template name: {str(e)}")
                    continue
            
            # Log the number of templates found
            log_info(f"Found {len(template_names)} available templates")
            return template_names
            
        except Exception as e:
            # Log any errors and return empty list
            log_error(f"Error getting available templates: {str(e)}")
            return []

    def search_templates(self, search_text: str) -> bool:
        """
        Search for templates using the search input

        Args:
            search_text: Search text to filter templates

        Returns:
            True if search was performed successfully, False otherwise
        """
        # Log search attempt
        log_info(f"Searching templates with text: '{search_text}'")
        
        try:
            # Input the search text into the search field
            result = self.input_text(TemplateSelectionLocators.SEARCH_TEMPLATES_INPUT, search_text)
            
            if not result:
                log_error(f"Failed to enter search text: '{search_text}'")
                return False
            
            # Wait for loading indicator to appear (search in progress)
            if self.is_element_visible(TemplateSelectionLocators.LOADING_INDICATOR):
                # Then wait for it to disappear (search completed)
                result = self.wait_for_element_to_disappear(TemplateSelectionLocators.LOADING_INDICATOR, 10)
                
                if not result:
                    log_error("Search operation timed out, loading indicator didn't disappear")
                    return False
            
            # Wait a moment for search results to update
            time.sleep(1)
            
            # Return True as search was performed successfully
            log_info(f"Successfully performed search with text: '{search_text}'")
            return True
            
        except Exception as e:
            # Log any errors and return False
            log_error(f"Error performing search: {str(e)}")
            return False

    def select_template_by_name(self, template_name: str) -> Optional[StoryEditorPage]:
        """
        Select a template by its name

        Args:
            template_name: Name of the template to select

        Returns:
            StoryEditorPage instance if template selected successfully, None otherwise
        """
        # Log template selection attempt
        log_info(f"Selecting template by name: '{template_name}'")
        
        try:
            # Make sure templates are loaded
            if not self.wait_for_templates_to_load():
                log_error("Could not select template, templates not loaded")
                return None
            
            # Find all template items
            template_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_ITEM)
            
            # If no template items found, return None
            if not template_items:
                log_error("No template items found")
                return None
            
            # Variable to store the found template item
            template_item = None
            
            # Find the template with the specified name
            for item in template_items:
                try:
                    # Try to find the template name element within the template item
                    name_element = item.find_element(*TemplateSelectionLocators.TEMPLATE_NAME)
                    # Get the text from the name element
                    name = name_element.text.strip()
                    
                    # If the name matches, store the item and break the loop
                    if name == template_name:
                        template_item = item
                        break
                except NoSuchElementException:
                    # If name element not found, try getting text directly from the item
                    name = item.text.strip()
                    
                    # If the name matches, store the item and break the loop
                    if name == template_name:
                        template_item = item
                        break
                except Exception as e:
                    # Log any other errors and continue with the next item
                    log_debug(f"Error checking template name: {str(e)}")
                    continue
            
            # If template not found, return None
            if not template_item:
                log_error(f"Template not found with name: '{template_name}'")
                return None
            
            # Find the select button within the template item
            try:
                select_button = template_item.find_element(*TemplateSelectionLocators.SELECT_TEMPLATE_BUTTON)
            except NoSuchElementException:
                # If select button not found, try clicking the template item itself
                select_button = template_item
            
            # Scroll to the select button to ensure it's in view
            self.scroll_to_element(select_button)
            
            # Click the select button
            select_button.click()
            
            # Wait for navigation to the story editor page
            time.sleep(2)
            
            # Create and return a new StoryEditorPage instance
            story_editor_page = StoryEditorPage(self.driver)
            
            # Check if navigation to story editor was successful
            if story_editor_page.is_loaded():
                log_info(f"Successfully selected template: '{template_name}'")
                return story_editor_page
            
            # If navigation wasn't successful, return None
            log_error(f"Failed to navigate to Story Editor after selecting template: '{template_name}'")
            return None
            
        except Exception as e:
            # Log any errors and return None
            log_error(f"Error selecting template by name: {str(e)}")
            # Take screenshot for debugging
            self.take_screenshot("select_template_error")
            return None

    def select_template_by_index(self, index: int) -> Optional[StoryEditorPage]:
        """
        Select a template by its index in the template list

        Args:
            index: Index of the template to select (0-based)

        Returns:
            StoryEditorPage instance if template selected successfully, None otherwise
        """
        # Log template selection attempt
        log_info(f"Selecting template by index: {index}")
        
        try:
            # Make sure templates are loaded
            if not self.wait_for_templates_to_load():
                log_error("Could not select template, templates not loaded")
                return None
            
            # Find all template items
            template_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_ITEM)
            
            # If no template items found, return None
            if not template_items:
                log_error("No template items found")
                return None
            
            # Check if index is valid
            if index < 0 or index >= len(template_items):
                log_error(f"Invalid template index: {index}, valid range is 0-{len(template_items)-1}")
                return None
            
            # Get the template item at the specified index
            template_item = template_items[index]
            
            # Find the select button within the template item
            try:
                select_button = template_item.find_element(*TemplateSelectionLocators.SELECT_TEMPLATE_BUTTON)
            except NoSuchElementException:
                # If select button not found, try clicking the template item itself
                select_button = template_item
            
            # Scroll to the select button to ensure it's in view
            self.scroll_to_element(select_button)
            
            # Click the select button
            select_button.click()
            
            # Wait for navigation to the story editor page
            time.sleep(2)
            
            # Create and return a new StoryEditorPage instance
            story_editor_page = StoryEditorPage(self.driver)
            
            # Check if navigation to story editor was successful
            if story_editor_page.is_loaded():
                log_info(f"Successfully selected template at index: {index}")
                return story_editor_page
            
            # If navigation wasn't successful, return None
            log_error(f"Failed to navigate to Story Editor after selecting template at index: {index}")
            return None
            
        except Exception as e:
            # Log any errors and return None
            log_error(f"Error selecting template by index: {str(e)}")
            # Take screenshot for debugging
            self.take_screenshot("select_template_index_error")
            return None

    def filter_templates_by_category(self, category_name: str) -> bool:
        """
        Filter templates by selecting a category

        Args:
            category_name: Name of the category to filter by

        Returns:
            True if category filter was applied successfully, False otherwise
        """
        # Log category filter attempt
        log_info(f"Filtering templates by category: '{category_name}'")
        
        try:
            # Find all category items
            category_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_CATEGORY_ITEM)
            
            # If no category items found, return False
            if not category_items:
                log_error("No category items found")
                return False
            
            # Variable to store the found category item
            category_item = None
            
            # Find the category with the specified name
            for item in category_items:
                name = item.text.strip()
                
                # If the name matches, store the item and break the loop
                if name == category_name:
                    category_item = item
                    break
            
            # If category not found, return False
            if not category_item:
                log_error(f"Category not found with name: '{category_name}'")
                return False
            
            # Scroll to the category item to ensure it's in view
            self.scroll_to_element(category_item)
            
            # Click the category item
            category_item.click()
            
            # Wait for loading indicator to appear and then disappear
            if self.is_element_visible(TemplateSelectionLocators.LOADING_INDICATOR):
                result = self.wait_for_element_to_disappear(TemplateSelectionLocators.LOADING_INDICATOR, 10)
                
                if not result:
                    log_error("Filter operation timed out, loading indicator didn't disappear")
                    return False
            
            # Wait a moment for templates to update
            time.sleep(1)
            
            # Return True as filter was applied successfully
            log_info(f"Successfully filtered templates by category: '{category_name}'")
            return True
            
        except Exception as e:
            # Log any errors and return False
            log_error(f"Error filtering templates by category: {str(e)}")
            return False

    def get_template_description(self, template_name: str) -> str:
        """
        Get the description of a template by its name

        Args:
            template_name: Name of the template

        Returns:
            Template description if found, empty string otherwise
        """
        # Log description retrieval attempt
        log_info(f"Getting description for template: '{template_name}'")
        
        try:
            # Make sure templates are loaded
            if not self.wait_for_templates_to_load():
                log_error("Could not get template description, templates not loaded")
                return ""
            
            # Find all template items
            template_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_ITEM)
            
            # If no template items found, return empty string
            if not template_items:
                log_error("No template items found")
                return ""
            
            # Variable to store the found template item
            template_item = None
            
            # Find the template with the specified name
            for item in template_items:
                try:
                    # Try to find the template name element within the template item
                    name_element = item.find_element(*TemplateSelectionLocators.TEMPLATE_NAME)
                    # Get the text from the name element
                    name = name_element.text.strip()
                    
                    # If the name matches, store the item and break the loop
                    if name == template_name:
                        template_item = item
                        break
                except NoSuchElementException:
                    # If name element not found, try getting text directly from the item
                    name = item.text.strip()
                    
                    # If the name matches, store the item and break the loop
                    if name == template_name:
                        template_item = item
                        break
                except Exception as e:
                    # Log any other errors and continue with the next item
                    log_debug(f"Error checking template name: {str(e)}")
                    continue
            
            # If template not found, return empty string
            if not template_item:
                log_error(f"Template not found with name: '{template_name}'")
                return ""
            
            # Try to find the description element within the template item
            try:
                description_element = template_item.find_element(*TemplateSelectionLocators.TEMPLATE_DESCRIPTION)
                # Get the text from the description element
                description = description_element.text.strip()
                
                # Log and return the description
                log_info(f"Found description for template '{template_name}': '{description}'")
                return description
            except NoSuchElementException:
                # If description element not found, return empty string
                log_error(f"Description element not found for template: '{template_name}'")
                return ""
            except Exception as e:
                # Log any other errors and return empty string
                log_error(f"Error getting template description: {str(e)}")
                return ""
            
        except Exception as e:
            # Log any errors and return empty string
            log_error(f"Error getting template description: {str(e)}")
            return ""

    def get_available_categories(self) -> List[str]:
        """
        Get a list of all available template categories

        Returns:
            List of category names available for filtering
        """
        # Log categories retrieval attempt
        log_info("Getting available template categories")
        
        try:
            # Find all category items
            category_items = self.find_elements(TemplateSelectionLocators.TEMPLATE_CATEGORY_ITEM)
            
            # Extract category names from each item
            category_names = [item.text.strip() for item in category_items if item.text.strip()]
            
            # Log the number of categories found
            log_info(f"Found {len(category_names)} available categories")
            return category_names
            
        except Exception as e:
            # Log any errors and return empty list
            log_error(f"Error getting available categories: {str(e)}")
            return []

    def is_template_available(self, template_name: str) -> bool:
        """
        Check if a specific template is available

        Args:
            template_name: Name of the template to check

        Returns:
            True if template is available, False otherwise
        """
        # Log template availability check
        log_info(f"Checking if template is available: '{template_name}'")
        
        # Get list of available templates
        templates = self.get_available_templates()
        
        # Check if the template is in the list
        is_available = template_name in templates
        
        # Log the result
        if is_available:
            log_info(f"Template '{template_name}' is available")
        else:
            log_info(f"Template '{template_name}' is not available")
        
        return is_available

    def select_blank_template(self) -> Optional[StoryEditorPage]:
        """
        Select the blank template option

        Returns:
            StoryEditorPage instance if blank template selected successfully, None otherwise
        """
        # Log blank template selection attempt
        log_info("Selecting blank template")
        
        # Try to select template with name "Blank"
        return self.select_template_by_name("Blank")

    def get_template_count(self) -> int:
        """
        Get the number of templates available

        Returns:
            Number of templates available
        """
        # Log template count retrieval attempt
        log_info("Getting template count")
        
        # Get list of available templates
        templates = self.get_available_templates()
        
        # Get the count
        count = len(templates)
        
        # Log the count
        log_info(f"Found {count} templates")
        
        return count