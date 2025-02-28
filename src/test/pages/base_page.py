"""
Base class for all page objects in the Storydoc automation framework.
Implements the Page Object Model pattern by providing common functionality
for page navigation, element interaction, waiting strategies, and error handling.
Serves as the foundation for all page-specific implementations.
"""

# Standard library imports
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# External imports - Selenium WebDriver (version 4.10+)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)

# Internal imports
from ..config.timeout_config import (
    DEFAULT_TIMEOUT,
    ELEMENT_TIMEOUT,
    ELEMENT_CLICKABLE_TIMEOUT,
    PAGE_LOAD_TIMEOUT
)
from ..utilities.wait_helper import WaitUtils
from ..utilities.screenshot_manager import ScreenshotManager
from ..utilities.logger import log_info, log_debug, log_error

# Element state constants
ELEMENT_STATE_VISIBLE = 'visible'
ELEMENT_STATE_CLICKABLE = 'clickable'
ELEMENT_STATE_PRESENT = 'present'
ELEMENT_STATE_INVISIBLE = 'invisible'

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 0.5


class BasePage:
    """
    Base class for all page objects in the test automation framework.
    Implements common page functionality following the Page Object Model pattern.
    """
    
    def __init__(self, driver: WebDriver, url: str = None, page_name: str = None):
        """
        Initialize a new page object with WebDriver instance
        
        Args:
            driver: WebDriver instance
            url: URL for this page
            page_name: Name of the page for logging purposes
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        self.url = url
        self.screenshot_manager = ScreenshotManager()
        self.page_name = page_name or self.__class__.__name__
        
        log_info(f"Initialized page object: {self.page_name}")
    
    def open(self) -> bool:
        """
        Open the page URL in the browser
        
        Returns:
            True if page opened successfully, False otherwise
        """
        if not self.url:
            log_error(f"Cannot open page {self.page_name}: URL not defined")
            return False
        
        try:
            log_info(f"Navigating to: {self.url}")
            self.driver.get(self.url)
            
            # Wait for page to be ready
            self.wait_for_page_ready()
            
            return True
        except Exception as e:
            log_error(f"Failed to open page {self.page_name}: {str(e)}")
            self.take_screenshot(f"page_open_failure_{self.page_name}")
            return False
    
    def get_title(self) -> str:
        """
        Get the current page title
        
        Returns:
            Current page title
        """
        return self.driver.title
    
    def get_url(self) -> str:
        """
        Get the current page URL
        
        Returns:
            Current page URL
        """
        return self.driver.current_url
    
    def find_element(self, locator: Tuple) -> WebElement:
        """
        Find a single element using the provided locator
        
        Args:
            locator: Tuple containing locator strategy and value
            
        Returns:
            The found element
        """
        log_debug(f"Finding element: {locator}")
        try:
            return self.driver.find_element(*locator)
        except NoSuchElementException as e:
            log_error(f"Element not found: {locator}")
            self.take_screenshot(f"element_not_found_{locator[1]}")
            raise e
    
    def find_elements(self, locator: Tuple) -> List[WebElement]:
        """
        Find multiple elements using the provided locator
        
        Args:
            locator: Tuple containing locator strategy and value
            
        Returns:
            List of WebElements
        """
        log_debug(f"Finding elements: {locator}")
        return self.driver.find_elements(*locator)
    
    def wait_for_element(self, locator: Tuple, state: str = ELEMENT_STATE_VISIBLE, 
                        timeout: float = None) -> Optional[WebElement]:
        """
        Wait for an element to be in the specified state
        
        Args:
            locator: Tuple containing locator strategy and value
            state: Desired element state ('visible', 'clickable', 'present', 'invisible')
            timeout: Maximum time to wait in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        # Use appropriate default timeout based on state if not provided
        if timeout is None:
            if state == ELEMENT_STATE_CLICKABLE:
                timeout = ELEMENT_CLICKABLE_TIMEOUT
            else:
                timeout = ELEMENT_TIMEOUT
                
        try:
            element = WaitUtils.wait_for_element_state(self.driver, locator, state, timeout)
            return element
        except TimeoutException:
            log_error(f"Timeout waiting for element {locator} to be {state}")
            self.take_screenshot(f"timeout_{state}_{locator[1]}")
            return None
    
    def wait_for_element_with_retry(self, locator: Tuple, state: str = ELEMENT_STATE_VISIBLE, 
                                  timeout: float = None, 
                                  retries: int = MAX_RETRIES) -> Optional[WebElement]:
        """
        Wait for an element with retry mechanism for flaky elements
        
        Args:
            locator: Tuple containing locator strategy and value
            state: Desired element state ('visible', 'clickable', 'present', 'invisible')
            timeout: Maximum time to wait in seconds for each attempt
            retries: Number of retry attempts
            
        Returns:
            WebElement if found, None otherwise
        """
        # Use appropriate default timeout based on state if not provided
        if timeout is None:
            if state == ELEMENT_STATE_CLICKABLE:
                timeout = ELEMENT_CLICKABLE_TIMEOUT
            else:
                timeout = ELEMENT_TIMEOUT
                
        element = WaitUtils.wait_for_element_with_retry(
            self.driver, locator, state, timeout, retries
        )
        
        if element is None and state != ELEMENT_STATE_INVISIBLE:
            log_error(f"Element {locator} not {state} after {retries} retries")
            self.take_screenshot(f"retry_failed_{state}_{locator[1]}")
        
        return element
    
    def is_element_present(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Check if an element is present in the DOM
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element is present, False otherwise
        """
        return self.wait_for_element(locator, ELEMENT_STATE_PRESENT, timeout) is not None
    
    def is_element_visible(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Check if an element is visible on the page
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element is visible, False otherwise
        """
        return self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout) is not None
    
    def is_element_clickable(self, locator: Tuple, timeout: float = ELEMENT_CLICKABLE_TIMEOUT) -> bool:
        """
        Check if an element is clickable
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element is clickable, False otherwise
        """
        return self.wait_for_element(locator, ELEMENT_STATE_CLICKABLE, timeout) is not None
    
    def click(self, locator: Tuple, wait_for_clickable: bool = True, 
             timeout: float = ELEMENT_CLICKABLE_TIMEOUT) -> bool:
        """
        Click on the element identified by the locator
        
        Args:
            locator: Tuple containing locator strategy and value
            wait_for_clickable: Whether to wait for element to be clickable
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if click was successful, False otherwise
        """
        log_debug(f"Clicking element: {locator}")
        try:
            # Wait for element based on wait_for_clickable flag
            if wait_for_clickable:
                element = self.wait_for_element(locator, ELEMENT_STATE_CLICKABLE, timeout)
            else:
                element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                element.click()
                return True
            return False
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            log_error(f"Failed to click element {locator}: {str(e)}")
            self.take_screenshot(f"click_failure_{locator[1]}")
            return False
    
    def input_text(self, locator: Tuple, text: str, clear_first: bool = True, 
                  timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Enter text into the element identified by the locator
        
        Args:
            locator: Tuple containing locator strategy and value
            text: Text to enter
            clear_first: Whether to clear the field first
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if text entry was successful, False otherwise
        """
        log_debug(f"Entering text '{text}' into element: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            log_error(f"Failed to enter text into element {locator}: {str(e)}")
            self.take_screenshot(f"input_failure_{locator[1]}")
            return False
    
    def get_text(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> str:
        """
        Get text from the element identified by the locator
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            Text of the element or empty string if not found
        """
        log_debug(f"Getting text from element: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                return element.text
            return ""
        except Exception as e:
            log_error(f"Failed to get text from element {locator}: {str(e)}")
            self.take_screenshot(f"get_text_failure_{locator[1]}")
            return ""
    
    def get_attribute(self, locator: Tuple, attribute: str, 
                     timeout: float = ELEMENT_TIMEOUT) -> Optional[str]:
        """
        Get attribute value from the element identified by the locator
        
        Args:
            locator: Tuple containing locator strategy and value
            attribute: Attribute to get
            timeout: Maximum time to wait in seconds
            
        Returns:
            Attribute value or None if not found
        """
        log_debug(f"Getting attribute '{attribute}' from element: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_PRESENT, timeout)
            
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            log_error(f"Failed to get attribute from element {locator}: {str(e)}")
            return None
    
    def select_dropdown_option(self, locator: Tuple, option_text: str, 
                              timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Select an option from a dropdown by visible text
        
        Args:
            locator: Tuple containing locator strategy and value
            option_text: Text of the option to select
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if selection was successful, False otherwise
        """
        log_debug(f"Selecting option '{option_text}' from dropdown: {locator}")
        try:
            from selenium.webdriver.support.ui import Select
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                select = Select(element)
                select.select_by_visible_text(option_text)
                return True
            return False
        except Exception as e:
            log_error(f"Failed to select option from dropdown {locator}: {str(e)}")
            self.take_screenshot(f"dropdown_failure_{locator[1]}")
            return False
    
    def check_checkbox(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Check a checkbox if it's not already checked
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if operation was successful, False otherwise
        """
        log_debug(f"Checking checkbox: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                if not element.is_selected():
                    element.click()
                return True
            return False
        except Exception as e:
            log_error(f"Failed to check checkbox {locator}: {str(e)}")
            self.take_screenshot(f"checkbox_failure_{locator[1]}")
            return False
    
    def uncheck_checkbox(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Uncheck a checkbox if it's checked
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if operation was successful, False otherwise
        """
        log_debug(f"Unchecking checkbox: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE, timeout)
            
            if element:
                if element.is_selected():
                    element.click()
                return True
            return False
        except Exception as e:
            log_error(f"Failed to uncheck checkbox {locator}: {str(e)}")
            self.take_screenshot(f"checkbox_failure_{locator[1]}")
            return False
    
    def wait_for_page_ready(self, timeout: float = PAGE_LOAD_TIMEOUT) -> bool:
        """
        Wait for page to be fully loaded and ready
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if page is ready, False otherwise
        """
        log_debug(f"Waiting for page {self.page_name} to be ready")
        try:
            return WaitUtils.wait_for_page_ready(self.driver, timeout)
        except TimeoutException:
            log_error(f"Timeout waiting for page {self.page_name} to be ready")
            return False
    
    def take_screenshot(self, filename: str) -> Optional[str]:
        """
        Capture a screenshot with the given filename
        
        Args:
            filename: Name for the screenshot file
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        return self.screenshot_manager.capture_screenshot(self.driver, filename)
    
    def take_element_screenshot(self, locator: Tuple, filename: str) -> Optional[str]:
        """
        Capture a screenshot highlighting a specific element
        
        Args:
            locator: Tuple containing locator strategy and value
            filename: Name for the screenshot file
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_VISIBLE)
            if element:
                return self.screenshot_manager.capture_element_screenshot(self.driver, element, filename)
            return None
        except Exception as e:
            log_error(f"Failed to capture element screenshot: {str(e)}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the current browser window
        
        Args:
            script: JavaScript to execute
            args: Arguments to pass to the script
            
        Returns:
            Result of the JavaScript execution
        """
        log_debug(f"Executing script: {script}")
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            log_error(f"Failed to execute script: {str(e)}")
            return None
    
    def scroll_to_element(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Scroll the page to bring an element into view
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if scroll was successful, False otherwise
        """
        log_debug(f"Scrolling to element: {locator}")
        try:
            element = self.wait_for_element(locator, ELEMENT_STATE_PRESENT, timeout)
            
            if element:
                self.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                return True
            return False
        except Exception as e:
            log_error(f"Failed to scroll to element {locator}: {str(e)}")
            return False
    
    def refresh_page(self) -> bool:
        """
        Refresh the current page
        
        Returns:
            True if refresh was successful, False otherwise
        """
        log_debug("Refreshing page")
        try:
            self.driver.refresh()
            self.wait_for_page_ready()
            return True
        except Exception as e:
            log_error(f"Failed to refresh page: {str(e)}")
            return False
    
    def navigate_back(self) -> bool:
        """
        Navigate to the previous page in the browser history
        
        Returns:
            True if navigation was successful, False otherwise
        """
        log_debug("Navigating back")
        try:
            self.driver.back()
            self.wait_for_page_ready()
            return True
        except Exception as e:
            log_error(f"Failed to navigate back: {str(e)}")
            return False
    
    def navigate_forward(self) -> bool:
        """
        Navigate to the next page in the browser history
        
        Returns:
            True if navigation was successful, False otherwise
        """
        log_debug("Navigating forward")
        try:
            self.driver.forward()
            self.wait_for_page_ready()
            return True
        except Exception as e:
            log_error(f"Failed to navigate forward: {str(e)}")
            return False
    
    def switch_to_frame(self, locator: Tuple, timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Switch to the specified iframe
        
        Args:
            locator: Tuple containing locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if switch was successful, False otherwise
        """
        log_debug(f"Switching to frame: {locator}")
        try:
            frame = self.wait_for_element(locator, ELEMENT_STATE_PRESENT, timeout)
            
            if frame:
                self.driver.switch_to.frame(frame)
                return True
            return False
        except Exception as e:
            log_error(f"Failed to switch to frame {locator}: {str(e)}")
            return False
    
    def switch_to_default_content(self) -> bool:
        """
        Switch back to the default content from an iframe
        
        Returns:
            True if switch was successful, False otherwise
        """
        log_debug("Switching to default content")
        try:
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            log_error(f"Failed to switch to default content: {str(e)}")
            return False
    
    def wait_for_url_contains(self, url_substring: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
        """
        Wait for the page URL to contain a specific string
        
        Args:
            url_substring: Substring to look for in URL
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if URL contains substring, False otherwise
        """
        log_debug(f"Waiting for URL to contain: {url_substring}")
        try:
            result = WebDriverWait(self.driver, timeout).until(
                EC.url_contains(url_substring)
            )
            return result
        except TimeoutException:
            log_error(f"Timeout waiting for URL to contain {url_substring}")
            return False