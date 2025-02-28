"""
Provides enhanced assertion utilities for the Storydoc test automation framework with additional features like automatic screenshot capture on failure, detailed error messages, and timeout handling for conditional assertions.
"""

import logging
import time
import re
from typing import Any, Callable, Dict, Iterable, List, Optional, Pattern, Tuple, Union

import pytest
from selenium.common.exceptions import TimeoutException

# Import internal modules
from .wait_helper import wait_for_condition, wait_for_element_state
from .screenshot_manager import take_screenshot_with_selenium
from ..config.timeout_config import DEFAULT_TIMEOUT, ELEMENT_TIMEOUT, POLLING_INTERVAL

# Set up logger
logger = logging.getLogger(__name__)

def assert_true(condition: bool, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a condition is true with custom error message and optional screenshot capture
    
    Args:
        condition: Condition to evaluate
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If condition is False
    """
    logger.info(f"Asserting condition is True: {message}")
    
    if not condition:
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_true_failure")
            message = f"{message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {message}")
        pytest.fail(message)

def assert_false(condition: bool, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a condition is false with custom error message and optional screenshot capture
    
    Args:
        condition: Condition to evaluate
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If condition is True
    """
    logger.info(f"Asserting condition is False: {message}")
    
    if condition:
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_false_failure")
            message = f"{message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {message}")
        pytest.fail(message)

def assert_equal(actual: Any, expected: Any, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that two values are equal with custom error message and optional screenshot capture
    
    Args:
        actual: Actual value
        expected: Expected value
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If values are not equal
    """
    logger.info(f"Asserting {actual} equals {expected}: {message}")
    
    if actual != expected:
        detailed_message = f"{message}\nExpected: {expected}\nActual: {actual}"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_equal_failure")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_not_equal(actual: Any, expected: Any, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that two values are not equal with custom error message and optional screenshot capture
    
    Args:
        actual: Actual value
        expected: Expected value
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If values are equal
    """
    logger.info(f"Asserting {actual} does not equal {expected}: {message}")
    
    if actual == expected:
        detailed_message = f"{message}\nExpected: {actual} to not equal {expected}"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_not_equal_failure")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_in(member: Any, container: Iterable, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a value is in a collection with custom error message and optional screenshot capture
    
    Args:
        member: Value to check for
        container: Collection to check in
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If member is not in container
    """
    logger.info(f"Asserting {member} is in {container}: {message}")
    
    if member not in container:
        detailed_message = f"{message}\nExpected: {member} to be in {container}"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_in_failure")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_not_in(member: Any, container: Iterable, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a value is not in a collection with custom error message and optional screenshot capture
    
    Args:
        member: Value to check for
        container: Collection to check in
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If member is in container
    """
    logger.info(f"Asserting {member} is not in {container}: {message}")
    
    if member in container:
        detailed_message = f"{message}\nExpected: {member} to not be in {container}"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"assert_not_in_failure")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_element_visible(driver, locator: Tuple, element_name: str, take_screenshot: bool = True, timeout: int = None) -> None:
    """
    Assert that a web element is visible on the page with custom timeout
    
    Args:
        driver: WebDriver instance
        locator: Locator tuple (By strategy, value)
        element_name: Name of the element for reporting
        take_screenshot: Whether to take a screenshot on failure
        timeout: Timeout in seconds (default: ELEMENT_TIMEOUT)
    
    Raises:
        AssertionError: If element is not visible within timeout
    """
    logger.info(f"Asserting element {element_name} is visible: {locator}")
    
    if timeout is None:
        timeout = ELEMENT_TIMEOUT
    
    element = wait_for_element_state(driver, locator, 'visible', timeout)
    
    if element is None:
        detailed_message = f"Element {element_name} not visible after {timeout} seconds: {locator}"
        
        if take_screenshot:
            screenshot_path = take_screenshot_with_selenium(driver, f"element_not_visible_{element_name}")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_element_not_visible(driver, locator: Tuple, element_name: str, take_screenshot: bool = True, timeout: int = None) -> None:
    """
    Assert that a web element is not visible on the page with custom timeout
    
    Args:
        driver: WebDriver instance
        locator: Locator tuple (By strategy, value)
        element_name: Name of the element for reporting
        take_screenshot: Whether to take a screenshot on failure
        timeout: Timeout in seconds (default: ELEMENT_TIMEOUT)
    
    Raises:
        AssertionError: If element is visible after timeout
    """
    logger.info(f"Asserting element {element_name} is not visible: {locator}")
    
    if timeout is None:
        timeout = ELEMENT_TIMEOUT
    
    result = wait_for_element_state(driver, locator, 'invisible', timeout)
    
    # wait_for_element_state returns None for both failure and invisibility
    # For invisibility, we need to check if any element is found and visible
    try:
        element = driver.find_element(*locator)
        if element.is_displayed():
            detailed_message = f"Element {element_name} is still visible after {timeout} seconds: {locator}"
            
            if take_screenshot:
                screenshot_path = take_screenshot_with_selenium(driver, f"element_still_visible_{element_name}")
                detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
            
            logger.error(f"Assertion failed: {detailed_message}")
            pytest.fail(detailed_message)
    except:
        # Element not found or not visible, which is the expected case
        pass

def assert_text_in_element(driver, locator: Tuple, expected_text: str, element_name: str, take_screenshot: bool = True, timeout: int = None) -> None:
    """
    Assert that an element contains expected text with custom timeout
    
    Args:
        driver: WebDriver instance
        locator: Locator tuple (By strategy, value)
        expected_text: Expected text content
        element_name: Name of the element for reporting
        take_screenshot: Whether to take a screenshot on failure
        timeout: Timeout in seconds (default: ELEMENT_TIMEOUT)
    
    Raises:
        AssertionError: If text is not found in element within timeout
    """
    logger.info(f"Asserting element {element_name} contains text '{expected_text}': {locator}")
    
    if timeout is None:
        timeout = ELEMENT_TIMEOUT
    
    # First ensure the element is visible
    element = wait_for_element_state(driver, locator, 'visible', timeout)
    
    if element is None:
        detailed_message = f"Element {element_name} not visible after {timeout} seconds: {locator}"
        
        if take_screenshot:
            screenshot_path = take_screenshot_with_selenium(driver, f"element_not_visible_for_text_{element_name}")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)
    
    # Get the element text
    actual_text = element.text
    
    # Check if expected text is in the element text
    if expected_text not in actual_text:
        detailed_message = f"Expected text '{expected_text}' not found in element {element_name}\nActual text: '{actual_text}'"
        
        if take_screenshot:
            screenshot_path = take_screenshot_with_selenium(driver, f"text_not_in_element_{element_name}")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_url_contains(driver, expected_substring: str, take_screenshot: bool = True, timeout: int = None) -> None:
    """
    Assert that the current URL contains expected substring with custom timeout
    
    Args:
        driver: WebDriver instance
        expected_substring: Expected substring in URL
        take_screenshot: Whether to take a screenshot on failure
        timeout: Timeout in seconds (default: DEFAULT_TIMEOUT)
    
    Raises:
        AssertionError: If URL does not contain substring within timeout
    """
    logger.info(f"Asserting URL contains '{expected_substring}'")
    
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    def check_url():
        current_url = driver.current_url
        return expected_substring in current_url
    
    result = wait_for_condition(check_url, timeout)
    
    if not result:
        current_url = driver.current_url
        detailed_message = f"URL does not contain '{expected_substring}' after {timeout} seconds\nActual URL: '{current_url}'"
        
        if take_screenshot:
            screenshot_path = take_screenshot_with_selenium(driver, f"url_does_not_contain_{expected_substring}")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_page_title(driver, expected_title: str, exact_match: bool = False, take_screenshot: bool = True, timeout: int = None) -> None:
    """
    Assert that the page title matches expected title with custom matching strategy
    
    Args:
        driver: WebDriver instance
        expected_title: Expected page title
        exact_match: Whether to require exact match or substring match
        take_screenshot: Whether to take a screenshot on failure
        timeout: Timeout in seconds (default: DEFAULT_TIMEOUT)
    
    Raises:
        AssertionError: If title does not match expectation within timeout
    """
    match_type = "exactly matches" if exact_match else "contains"
    logger.info(f"Asserting page title {match_type} '{expected_title}'")
    
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    def check_title():
        current_title = driver.title
        if exact_match:
            return current_title == expected_title
        else:
            return expected_title in current_title
    
    result = wait_for_condition(check_title, timeout)
    
    if not result:
        current_title = driver.title
        match_text = "match" if exact_match else "contain"
        detailed_message = f"Page title does not {match_text} '{expected_title}' after {timeout} seconds\nActual title: '{current_title}'"
        
        if take_screenshot:
            screenshot_path = take_screenshot_with_selenium(driver, f"title_mismatch")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_with_timeout(condition_function: Callable, message: str, timeout: int = None, poll_frequency: float = None, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a condition becomes true within a specified timeout
    
    Args:
        condition_function: Function that returns a boolean (True when condition is met)
        message: Error message if assertion fails
        timeout: Timeout in seconds (default: DEFAULT_TIMEOUT)
        poll_frequency: Polling frequency in seconds (default: POLLING_INTERVAL)
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If condition is not met within timeout
    """
    logger.info(f"Asserting condition with timeout: {message}")
    
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    if poll_frequency is None:
        poll_frequency = POLLING_INTERVAL
    
    result = wait_for_condition(condition_function, timeout, poll_frequency)
    
    if not result:
        detailed_message = f"{message} - Condition not met within {timeout} seconds"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"condition_timeout")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_matches_pattern(actual_string: str, pattern: str, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that a string matches a regular expression pattern
    
    Args:
        actual_string: String to check
        pattern: Regular expression pattern
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If string does not match pattern
    """
    logger.info(f"Asserting string matches pattern '{pattern}': {message}")
    
    # Compile pattern
    compiled_pattern = re.compile(pattern)
    
    # Check if pattern matches
    if not compiled_pattern.search(actual_string):
        detailed_message = f"{message}\nExpected string to match pattern: '{pattern}'\nActual string: '{actual_string}'"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"pattern_mismatch")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_response_status(response, expected_status: int, message: str, take_screenshot: bool = True, driver = None) -> None:
    """
    Assert that an HTTP response has the expected status code
    
    Args:
        response: HTTP response object with a status_code attribute
        expected_status: Expected status code
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Raises:
        AssertionError: If status code does not match
    """
    actual_status = response.status_code
    logger.info(f"Asserting response status code is {expected_status}: {message}")
    
    if actual_status != expected_status:
        detailed_message = f"{message}\nExpected status code: {expected_status}\nActual status code: {actual_status}"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"response_status_mismatch")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)

def assert_performance(operation: Callable, time_limit_seconds: float, operation_name: str, take_screenshot: bool = True, driver = None) -> Any:
    """
    Assert that an operation completes within a specified time limit
    
    Args:
        operation: Function to execute and time
        time_limit_seconds: Maximum acceptable execution time in seconds
        operation_name: Name of the operation for reporting
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
    
    Returns:
        Result of the operation if assertion passes
    
    Raises:
        AssertionError: If operation exceeds time limit
    """
    logger.info(f"Asserting performance of '{operation_name}' completes within {time_limit_seconds} seconds")
    
    start_time = time.time()
    result = operation()
    end_time = time.time()
    
    duration = end_time - start_time
    
    if duration > time_limit_seconds:
        detailed_message = f"Performance assertion failed: Operation '{operation_name}' took {duration:.2f} seconds, exceeding limit of {time_limit_seconds} seconds"
        
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"performance_failure_{operation_name}")
            detailed_message = f"{detailed_message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Assertion failed: {detailed_message}")
        pytest.fail(detailed_message)
    
    logger.info(f"Performance assertion passed: Operation '{operation_name}' completed in {duration:.2f} seconds (limit: {time_limit_seconds} seconds)")
    return result

def soft_assert(condition: bool, message: str, take_screenshot: bool = True, driver = None, failure_list: List = None) -> bool:
    """
    Make an assertion that collects failures rather than raising exceptions immediately
    
    Args:
        condition: Condition to evaluate
        message: Error message if assertion fails
        take_screenshot: Whether to take a screenshot on failure
        driver: WebDriver instance for taking screenshots
        failure_list: List to collect failure messages
    
    Returns:
        True if assertion passes, False if it fails
    """
    logger.info(f"Soft asserting condition: {message}")
    
    if not condition:
        if take_screenshot and driver:
            screenshot_path = take_screenshot_with_selenium(driver, f"soft_assert_failure")
            message = f"{message} (Screenshot: {screenshot_path})"
        
        logger.error(f"Soft assertion failed: {message}")
        
        if failure_list is not None:
            failure_list.append(message)
        
        return False
    
    return True

def report_soft_assert_failures(failure_list: List, raise_exception: bool = True) -> bool:
    """
    Report all collected soft assertion failures at once
    
    Args:
        failure_list: List of failure messages
        raise_exception: Whether to raise an exception if failures exist
    
    Returns:
        True if no failures, False if failures were found
    
    Raises:
        AssertionError: If failures exist and raise_exception is True
    """
    if not failure_list:
        return True
    
    failure_count = len(failure_list)
    failure_message = f"Soft assertion failures ({failure_count}):\n" + "\n".join([f"- {failure}" for failure in failure_list])
    
    logger.error(failure_message)
    
    if raise_exception:
        pytest.fail(failure_message)
    
    return False

class SoftAssert:
    """
    Class that provides soft assertion capabilities for collecting multiple assertion failures
    """
    
    def __init__(self, driver=None):
        """
        Initialize the SoftAssert instance with an optional WebDriver
        
        Args:
            driver: WebDriver instance for taking screenshots
        """
        self._failures = []
        self._driver = driver
    
    def assert_true(self, condition: bool, message: str, take_screenshot: bool = True) -> bool:
        """
        Soft assert that a condition is true
        
        Args:
            condition: Condition to evaluate
            message: Error message if assertion fails
            take_screenshot: Whether to take a screenshot on failure
        
        Returns:
            True if assertion passes, False if it fails
        """
        return soft_assert(condition, message, take_screenshot, self._driver, self._failures)
    
    def assert_false(self, condition: bool, message: str, take_screenshot: bool = True) -> bool:
        """
        Soft assert that a condition is false
        
        Args:
            condition: Condition to evaluate
            message: Error message if assertion fails
            take_screenshot: Whether to take a screenshot on failure
        
        Returns:
            True if assertion passes, False if it fails
        """
        return soft_assert(not condition, message, take_screenshot, self._driver, self._failures)
    
    def assert_equal(self, actual: Any, expected: Any, message: str, take_screenshot: bool = True) -> bool:
        """
        Soft assert that two values are equal
        
        Args:
            actual: Actual value
            expected: Expected value
            message: Error message if assertion fails
            take_screenshot: Whether to take a screenshot on failure
        
        Returns:
            True if assertion passes, False if it fails
        """
        condition = actual == expected
        detailed_message = f"{message} (Expected: {expected}, Actual: {actual})"
        return soft_assert(condition, detailed_message, take_screenshot, self._driver, self._failures)
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str, take_screenshot: bool = True) -> bool:
        """
        Soft assert that two values are not equal
        
        Args:
            actual: Actual value
            expected: Expected value
            message: Error message if assertion fails
            take_screenshot: Whether to take a screenshot on failure
        
        Returns:
            True if assertion passes, False if it fails
        """
        condition = actual != expected
        detailed_message = f"{message} (Expected: {actual} to not equal {expected})"
        return soft_assert(condition, detailed_message, take_screenshot, self._driver, self._failures)
    
    def assert_element_visible(self, locator: Tuple, element_name: str, take_screenshot: bool = True, timeout: int = None) -> bool:
        """
        Soft assert that an element is visible
        
        Args:
            locator: Locator tuple (By strategy, value)
            element_name: Name of the element for reporting
            take_screenshot: Whether to take a screenshot on failure
            timeout: Timeout in seconds (default: ELEMENT_TIMEOUT)
        
        Returns:
            True if assertion passes, False if it fails
        """
        if timeout is None:
            timeout = ELEMENT_TIMEOUT
        
        try:
            element = wait_for_element_state(self._driver, locator, 'visible', timeout)
            condition = element is not None
        except:
            condition = False
        
        detailed_message = f"Element {element_name} should be visible: {locator}"
        return soft_assert(condition, detailed_message, take_screenshot, self._driver, self._failures)
    
    def assert_all(self, raise_exception: bool = True) -> bool:
        """
        Report all collected failures and optionally raise an exception
        
        Args:
            raise_exception: Whether to raise an exception if failures exist
        
        Returns:
            True if no failures, False if any assertions failed
        """
        result = report_soft_assert_failures(self._failures, raise_exception)
        self._failures = []
        return result
    
    def has_failures(self) -> bool:
        """
        Check if any soft assertions have failed
        
        Returns:
            True if failures exist, False otherwise
        """
        return len(self._failures) > 0
    
    def clear_failures(self) -> None:
        """
        Clear all collected assertion failures
        """
        self._failures = []