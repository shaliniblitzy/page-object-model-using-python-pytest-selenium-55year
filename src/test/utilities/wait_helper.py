"""
Provides waiting and synchronization utilities for browser interactions in the Storydoc test automation framework.

Implements various waiting strategies using Selenium WebDriverWait and expected conditions to handle timing issues 
and improve test reliability. Also includes custom expected conditions for more complex waiting scenarios.
"""

import time
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union, Pattern

import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotVisibleException,
    ElementNotInteractableException
)
from selenium.webdriver.remote.webelement import WebElement

# Import internal modules
from ..config.timeout_config import (
    DEFAULT_TIMEOUT,
    ELEMENT_TIMEOUT,
    ELEMENT_CLICKABLE_TIMEOUT,
    ELEMENT_PRESENCE_TIMEOUT,
    ELEMENT_DISAPPEAR_TIMEOUT,
    POLLING_INTERVAL,
    MAX_RETRY_COUNT
)
from .logger import log_info, log_debug, log_error, log_warning

# JavaScript snippets for checking page readiness
JS_PAGE_READY_STATE = "return document.readyState === 'complete';"
JS_JQUERY_READY = "return typeof jQuery !== 'undefined' && jQuery.active === 0;"
JS_ANGULAR_READY = "return typeof angular === 'undefined' || !angular.element(document).injector() || !angular.element(document).injector().get('$http').pendingRequests.length;"
JS_DOM_READY = "return (typeof jQuery !== 'undefined' && jQuery.active === 0) || document.readyState === 'complete';"


def wait_until(condition_function: Callable[[], bool], 
               timeout: float = DEFAULT_TIMEOUT, 
               poll_frequency: float = POLLING_INTERVAL,
               error_message: str = "Timeout waiting for condition") -> bool:
    """
    Generic wait function that waits until a condition is met
    
    Args:
        condition_function: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        error_message: Message to log if timeout occurs
        
    Returns:
        bool: True if condition was met within timeout, otherwise False
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if condition_function():
                return True
        except Exception as e:
            log_error(f"Error checking condition: {str(e)}")
        
        time.sleep(poll_frequency)
    
    log_warning(f"{error_message} after {timeout} seconds")
    return False


def wait_for_element_state(driver: webdriver.WebDriver, 
                           locator: Tuple[str, str], 
                           state: str = 'visible', 
                           timeout: float = None,
                           poll_frequency: float = POLLING_INTERVAL) -> Optional[WebElement]:
    """
    Wait for an element to be in a specific state (visible, clickable, present, invisible)
    
    Args:
        driver: WebDriver instance
        locator: Tuple of locator strategy and value (e.g., (By.ID, "element-id"))
        state: Desired element state ('visible', 'clickable', 'present', 'invisible', 'selected', 'not_selected')
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        WebElement if found, None otherwise
    """
    # Set default timeout based on state if not provided
    if timeout is None:
        if state == 'visible':
            timeout = ELEMENT_TIMEOUT
        elif state == 'clickable':
            timeout = ELEMENT_CLICKABLE_TIMEOUT
        elif state == 'present':
            timeout = ELEMENT_PRESENCE_TIMEOUT
        elif state == 'invisible':
            timeout = ELEMENT_DISAPPEAR_TIMEOUT
        else:
            timeout = DEFAULT_TIMEOUT
    
    # Select the appropriate expected condition based on state
    if state == 'visible':
        expected_condition = EC.visibility_of_element_located(locator)
        log_debug(f"Waiting for element to be visible: {locator}")
    elif state == 'clickable':
        expected_condition = EC.element_to_be_clickable(locator)
        log_debug(f"Waiting for element to be clickable: {locator}")
    elif state == 'present':
        expected_condition = EC.presence_of_element_located(locator)
        log_debug(f"Waiting for element to be present: {locator}")
    elif state == 'invisible':
        expected_condition = EC.invisibility_of_element_located(locator)
        log_debug(f"Waiting for element to be invisible: {locator}")
    elif state == 'selected':
        expected_condition = EC.element_to_be_selected(locator)
        log_debug(f"Waiting for element to be selected: {locator}")
    elif state == 'not_selected':
        expected_condition = EC.element_selection_state_to_be(locator, False)
        log_debug(f"Waiting for element to be not selected: {locator}")
    else:
        log_error(f"Invalid element state specified: {state}")
        return None
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        element = wait.until(expected_condition)
        
        # For invisibility, the element is not returned, so we return None
        if state == 'invisible':
            return None
        
        log_debug(f"Element {locator} is now in state: {state}")
        return element
    except TimeoutException:
        log_warning(f"Timeout waiting for element {locator} to be {state} after {timeout} seconds")
        return None
    except Exception as e:
        log_error(f"Error waiting for element {locator} to be {state}: {str(e)}")
        return None


def wait_with_exponential_backoff(condition_function: Callable[[], bool],
                                 initial_wait: float = 1.0,
                                 max_wait: float = 10.0,
                                 max_retries: int = 5,
                                 backoff_factor: float = 2.0) -> bool:
    """
    Wait with exponential backoff for a condition to be met
    
    Args:
        condition_function: Function that returns True when condition is met
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds for a single attempt
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to increase wait time by after each attempt
        
    Returns:
        bool: True if condition was met, otherwise False
    """
    wait_time = initial_wait
    
    for attempt in range(max_retries):
        try:
            if condition_function():
                return True
        except Exception as e:
            log_error(f"Error checking condition (attempt {attempt+1}/{max_retries}): {str(e)}")
        
        log_debug(f"Condition not met on attempt {attempt+1}/{max_retries}, waiting {wait_time:.2f} seconds")
        time.sleep(wait_time)
        
        # Increase wait time for next attempt, but cap at max_wait
        wait_time = min(wait_time * backoff_factor, max_wait)
    
    log_warning(f"Condition not met after {max_retries} attempts with exponential backoff")
    return False


def wait_for_page_ready(driver: webdriver.WebDriver,
                       timeout: float = DEFAULT_TIMEOUT,
                       poll_frequency: float = POLLING_INTERVAL) -> bool:
    """
    Wait for page to be fully loaded and ready
    
    Args:
        driver: WebDriver instance
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        bool: True if page is ready, False otherwise
    """
    log_debug("Waiting for page to be ready")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        
        # Wait for document.readyState to be 'complete'
        wait.until(lambda d: d.execute_script(JS_PAGE_READY_STATE))
        
        # Check for jQuery if available
        jquery_ready = driver.execute_script(JS_JQUERY_READY)
        
        # Check for Angular if available
        angular_ready = driver.execute_script(JS_ANGULAR_READY)
        
        log_debug("Page is ready")
        return True
    except TimeoutException:
        log_warning(f"Timeout waiting for page to be ready after {timeout} seconds")
        return False
    except Exception as e:
        log_error(f"Error waiting for page to be ready: {str(e)}")
        return False


def wait_for_element_with_retry(driver: webdriver.WebDriver,
                               locator: Tuple[str, str],
                               state: str = 'visible',
                               timeout: float = ELEMENT_TIMEOUT,
                               retries: int = MAX_RETRY_COUNT,
                               retry_delay: float = 1.0) -> Optional[WebElement]:
    """
    Wait for an element with retry mechanism for flaky elements
    
    Args:
        driver: WebDriver instance
        locator: Tuple of locator strategy and value (e.g., (By.ID, "element-id"))
        state: Desired element state ('visible', 'clickable', 'present', 'invisible')
        timeout: Maximum time to wait in seconds for each attempt
        retries: Number of retry attempts
        retry_delay: Time to wait between retries in seconds
        
    Returns:
        WebElement if found, None otherwise
    """
    retry_count = 0
    
    while retry_count < retries:
        element = wait_for_element_state(driver, locator, state, timeout, POLLING_INTERVAL)
        
        if element is not None or state == 'invisible':
            return element
        
        log_debug(f"Retry {retry_count + 1}/{retries} for element {locator} to be {state}")
        time.sleep(retry_delay)
        retry_count += 1
    
    log_warning(f"Element {locator} not {state} after {retries} retries")
    return None


def wait_for_elements(driver: webdriver.WebDriver,
                     locator: Tuple[str, str],
                     timeout: float = ELEMENT_TIMEOUT,
                     poll_frequency: float = POLLING_INTERVAL) -> List[WebElement]:
    """
    Wait for multiple elements to be present
    
    Args:
        driver: WebDriver instance
        locator: Tuple of locator strategy and value (e.g., (By.CSS_SELECTOR, ".item"))
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        List of WebElements if found, empty list otherwise
    """
    log_debug(f"Waiting for elements: {locator}")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        elements = wait.until(EC.presence_of_all_elements_located(locator))
        log_debug(f"Found {len(elements)} elements matching {locator}")
        return elements
    except TimeoutException:
        log_warning(f"Timeout waiting for elements {locator} after {timeout} seconds")
        return []
    except Exception as e:
        log_error(f"Error waiting for elements {locator}: {str(e)}")
        return []


def wait_for_page_url_contains(driver: webdriver.WebDriver,
                              url_substr: str,
                              timeout: float = DEFAULT_TIMEOUT,
                              poll_frequency: float = POLLING_INTERVAL) -> bool:
    """
    Wait for page URL to contain a specific string
    
    Args:
        driver: WebDriver instance
        url_substr: Substring to look for in URL
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        bool: True if URL contains substring, False otherwise
    """
    log_debug(f"Waiting for URL to contain: {url_substr}")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        result = wait.until(EC.url_contains(url_substr))
        log_debug(f"URL now contains: {url_substr}")
        return result
    except TimeoutException:
        log_warning(f"Timeout waiting for URL to contain {url_substr} after {timeout} seconds")
        return False
    except Exception as e:
        log_error(f"Error waiting for URL to contain {url_substr}: {str(e)}")
        return False


def wait_for_page_title_contains(driver: webdriver.WebDriver,
                                title_substr: str,
                                timeout: float = DEFAULT_TIMEOUT,
                                poll_frequency: float = POLLING_INTERVAL) -> bool:
    """
    Wait for page title to contain a specific string
    
    Args:
        driver: WebDriver instance
        title_substr: Substring to look for in title
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        bool: True if title contains substring, False otherwise
    """
    log_debug(f"Waiting for title to contain: {title_substr}")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        result = wait.until(EC.title_contains(title_substr))
        log_debug(f"Title now contains: {title_substr}")
        return result
    except TimeoutException:
        log_warning(f"Timeout waiting for title to contain {title_substr} after {timeout} seconds")
        return False
    except Exception as e:
        log_error(f"Error waiting for title to contain {title_substr}: {str(e)}")
        return False


def wait_for_text_in_element(driver: webdriver.WebDriver,
                            locator: Tuple[str, str],
                            text: str,
                            timeout: float = ELEMENT_TIMEOUT,
                            poll_frequency: float = POLLING_INTERVAL) -> bool:
    """
    Wait for element to contain a specific text
    
    Args:
        driver: WebDriver instance
        locator: Tuple of locator strategy and value (e.g., (By.ID, "element-id"))
        text: Text to look for in the element
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        bool: True if element contains text, False otherwise
    """
    log_debug(f"Waiting for element {locator} to contain text: {text}")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        result = wait.until(EC.text_to_be_present_in_element(locator, text))
        log_debug(f"Element {locator} now contains text: {text}")
        return result
    except TimeoutException:
        log_warning(f"Timeout waiting for element {locator} to contain text '{text}' after {timeout} seconds")
        return False
    except Exception as e:
        log_error(f"Error waiting for element {locator} to contain text '{text}': {str(e)}")
        return False


def wait_for_attribute_value(driver: webdriver.WebDriver,
                            locator: Tuple[str, str],
                            attribute: str,
                            value: str,
                            timeout: float = ELEMENT_TIMEOUT,
                            poll_frequency: float = POLLING_INTERVAL) -> bool:
    """
    Wait for element's attribute to have a specific value
    
    Args:
        driver: WebDriver instance
        locator: Tuple of locator strategy and value (e.g., (By.ID, "element-id"))
        attribute: Name of the attribute to check
        value: Expected value of the attribute
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        bool: True if attribute has expected value, False otherwise
    """
    log_debug(f"Waiting for element {locator} to have attribute {attribute}='{value}'")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        result = wait.until(CustomExpectedConditions.element_contains_attribute(locator, attribute, value))
        log_debug(f"Element {locator} now has attribute {attribute}='{value}'")
        return result
    except TimeoutException:
        log_warning(f"Timeout waiting for element {locator} to have attribute {attribute}='{value}' after {timeout} seconds")
        return False
    except Exception as e:
        log_error(f"Error waiting for element {locator} to have attribute {attribute}='{value}': {str(e)}")
        return False


def wait_for_alert(driver: webdriver.WebDriver,
                  timeout: float = DEFAULT_TIMEOUT,
                  poll_frequency: float = POLLING_INTERVAL) -> Optional[webdriver.Alert]:
    """
    Wait for an alert to be present
    
    Args:
        driver: WebDriver instance
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        
    Returns:
        Alert object if present, None otherwise
    """
    log_debug("Waiting for alert to be present")
    
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        alert = wait.until(EC.alert_is_present())
        log_debug("Alert is now present")
        return alert
    except TimeoutException:
        log_warning(f"Timeout waiting for alert after {timeout} seconds")
        return None
    except Exception as e:
        log_error(f"Error waiting for alert: {str(e)}")
        return None


class WaitUtils:
    """
    Utility class for handling waiting operations in Selenium WebDriver
    """
    
    @staticmethod
    def wait_for_element_state(driver: webdriver.WebDriver,
                              locator: Tuple[str, str],
                              state: str = 'visible',
                              timeout: float = ELEMENT_TIMEOUT) -> Optional[WebElement]:
        """
        Static method for waiting for element state
        
        Args:
            driver: WebDriver instance
            locator: Tuple of locator strategy and value
            state: Desired element state ('visible', 'clickable', 'present', 'invisible')
            timeout: Maximum time to wait in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        return wait_for_element_state(driver, locator, state, timeout)
    
    @staticmethod
    def wait_for_page_ready(driver: webdriver.WebDriver,
                           timeout: float = DEFAULT_TIMEOUT) -> bool:
        """
        Static method for waiting for page to be ready
        
        Args:
            driver: WebDriver instance
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if page is ready, False otherwise
        """
        return wait_for_page_ready(driver, timeout)
    
    @staticmethod
    def wait_for_element_with_retry(driver: webdriver.WebDriver,
                                   locator: Tuple[str, str],
                                   state: str = 'visible',
                                   timeout: float = ELEMENT_TIMEOUT,
                                   retries: int = MAX_RETRY_COUNT) -> Optional[WebElement]:
        """
        Static method for waiting for element with retry mechanism
        
        Args:
            driver: WebDriver instance
            locator: Tuple of locator strategy and value
            state: Desired element state ('visible', 'clickable', 'present', 'invisible')
            timeout: Maximum time to wait in seconds for each attempt
            retries: Number of retry attempts
            
        Returns:
            WebElement if found, None otherwise
        """
        return wait_for_element_with_retry(driver, locator, state, timeout, retries)
    
    @staticmethod
    def wait_for_elements(driver: webdriver.WebDriver,
                         locator: Tuple[str, str],
                         timeout: float = ELEMENT_TIMEOUT) -> List[WebElement]:
        """
        Static method for waiting for multiple elements
        
        Args:
            driver: WebDriver instance
            locator: Tuple of locator strategy and value
            timeout: Maximum time to wait in seconds
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        return wait_for_elements(driver, locator, timeout)
    
    @staticmethod
    def wait_for_text_in_element(driver: webdriver.WebDriver,
                                locator: Tuple[str, str],
                                text: str,
                                timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Static method for waiting for text in element
        
        Args:
            driver: WebDriver instance
            locator: Tuple of locator strategy and value
            text: Text to look for in the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if element contains text, False otherwise
        """
        return wait_for_text_in_element(driver, locator, text, timeout)
    
    @staticmethod
    def wait_for_attribute_value(driver: webdriver.WebDriver,
                                locator: Tuple[str, str],
                                attribute: str,
                                value: str,
                                timeout: float = ELEMENT_TIMEOUT) -> bool:
        """
        Static method for waiting for attribute value
        
        Args:
            driver: WebDriver instance
            locator: Tuple of locator strategy and value
            attribute: Name of the attribute to check
            value: Expected value of the attribute
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if attribute has expected value, False otherwise
        """
        return wait_for_attribute_value(driver, locator, attribute, value, timeout)


class CustomExpectedConditions:
    """
    Custom expected conditions for WebDriverWait that extend standard Selenium conditions
    """
    
    @staticmethod
    def element_contains_attribute(locator: Tuple[str, str], attribute: str, value: str):
        """
        Condition for element to have a specific attribute value
        
        Args:
            locator: Tuple of locator strategy and value
            attribute: Name of the attribute to check
            value: Expected value of the attribute
            
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            try:
                element = driver.find_element(*locator)
                attribute_value = element.get_attribute(attribute)
                return attribute_value == value
            except (StaleElementReferenceException, NoSuchElementException):
                return False
        
        return _predicate
    
    @staticmethod
    def element_has_css_class(locator: Tuple[str, str], css_class: str):
        """
        Condition for element to have a specific CSS class
        
        Args:
            locator: Tuple of locator strategy and value
            css_class: CSS class to check for
            
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            try:
                element = driver.find_element(*locator)
                classes = element.get_attribute("class").split()
                return css_class in classes
            except (StaleElementReferenceException, NoSuchElementException):
                return False
        
        return _predicate
    
    @staticmethod
    def element_text_matches(locator: Tuple[str, str], pattern: Pattern):
        """
        Condition for element text to match a regular expression pattern
        
        Args:
            locator: Tuple of locator strategy and value
            pattern: Compiled regular expression pattern to match against
            
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            try:
                element = driver.find_element(*locator)
                text = element.text
                return bool(pattern.match(text))
            except (StaleElementReferenceException, NoSuchElementException):
                return False
        
        return _predicate
    
    @staticmethod
    def staleness_of(element: WebElement):
        """
        Condition for an element to become stale (no longer attached to DOM)
        
        Args:
            element: WebElement to check
            
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            try:
                # Check if element is still attached to the DOM
                element.is_enabled()
                return False
            except StaleElementReferenceException:
                return True
        
        return _predicate
    
    @staticmethod
    def any_element_visible(locators: List[Tuple[str, str]]):
        """
        Condition for any of multiple elements to be visible
        
        Args:
            locators: List of locator tuples
            
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            for locator in locators:
                try:
                    element = driver.find_element(*locator)
                    if element.is_displayed():
                        return element
                except (NoSuchElementException, StaleElementReferenceException):
                    continue
            return False
        
        return _predicate
    
    @staticmethod
    def page_has_no_js_errors():
        """
        Condition for page to have no JavaScript errors
        
        Returns:
            Callable condition function for WebDriverWait
        """
        def _predicate(driver):
            try:
                js_errors = driver.execute_script(
                    "return window.jsErrors || [];"
                )
                return len(js_errors) == 0
            except Exception:
                return False
        
        return _predicate