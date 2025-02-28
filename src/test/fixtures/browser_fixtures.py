"""
Provides pytest fixtures for browser initialization, configuration, and cleanup for the Storydoc test automation framework.
Implements fixtures with different scopes and browser types to support the various test scenarios.
"""

import pytest  # pytest 7.3+
import logging  # built-in
import os  # built-in
from typing import Optional  # built-in

# Import internal utilities and configurations
from ..utilities.driver_factory import DriverFactory
from ..utilities.screenshot_manager import ScreenshotManager
from ..config.constants import BROWSERS, TIMEOUTS
from ..config.browser_config import should_use_headless, get_browser_options
from ..utilities.wait_helper import WaitUtils

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def browser(request):
    """
    Pytest fixture that provides a configured WebDriver instance for tests with function scope
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.WebDriver: Configured WebDriver instance
    """
    # Retrieve browser_type from request config, marker, or default to BROWSERS['CHROME']
    browser_type = getattr(request.config, 'browser', None)
    if browser_type is None:
        browser_type = request.node.get_closest_marker('browser')
        browser_type = browser_type.args[0] if browser_type else BROWSERS['CHROME']

    # Retrieve headless mode from request config, marker, or use should_use_headless()
    headless = getattr(request.config, 'headless', None)
    if headless is None:
        headless_marker = request.node.get_closest_marker('headless')
        headless = headless_marker.args[0] if headless_marker else should_use_headless()

    logger.info(f"Creating {browser_type} browser for test: {request.node.name}")
    
    # Create WebDriver instance using DriverFactory.get_driver with browser_type and headless settings
    driver = DriverFactory.get_driver(browser_type=browser_type, headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield WebDriver instance to the test
    yield driver
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        screenshot_manager = ScreenshotManager()
        screenshot_manager.capture_failure_screenshot(driver, request.node.name)
    
    # Finally, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='session')
def browser_session(request):
    """
    Pytest fixture that provides a WebDriver instance with session scope (persists across all tests in the session)
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.WebDriver: Configured WebDriver instance
    """
    # Retrieve browser_type from request config or default to BROWSERS['CHROME']
    browser_type = getattr(request.config, 'browser', BROWSERS['CHROME'])
    
    # Retrieve headless mode from request config or use should_use_headless()
    headless = getattr(request.config, 'headless', should_use_headless())
    
    logger.info(f"Creating {browser_type} browser session")
    
    # Create WebDriver instance using DriverFactory.get_driver with browser_type and headless settings
    driver = DriverFactory.get_driver(browser_type=browser_type, headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield WebDriver instance to all tests in the session
    yield driver
    
    # After all tests complete, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='class')
def class_browser(request):
    """
    Pytest fixture that provides a WebDriver instance with class scope (persists across all tests in a class)
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.WebDriver: Configured WebDriver instance
    """
    # Retrieve browser_type from request config, marker, or default to BROWSERS['CHROME']
    browser_type = getattr(request.config, 'browser', None)
    if browser_type is None:
        browser_type = request.node.get_closest_marker('browser')
        browser_type = browser_type.args[0] if browser_type else BROWSERS['CHROME']
    
    # Retrieve headless mode from request config, marker, or use should_use_headless()
    headless = getattr(request.config, 'headless', None)
    if headless is None:
        headless_marker = request.node.get_closest_marker('headless')
        headless = headless_marker.args[0] if headless_marker else should_use_headless()
    
    logger.info(f"Creating {browser_type} browser for class")
    
    # Create WebDriver instance using DriverFactory.get_driver with browser_type and headless settings
    driver = DriverFactory.get_driver(browser_type=browser_type, headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield WebDriver instance to all tests in the class
    yield driver
    
    # After all tests in class complete, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='function')
def chrome_browser(request):
    """
    Pytest fixture that specifically provides a Chrome WebDriver instance
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.Chrome: Chrome WebDriver instance
    """
    # Retrieve headless mode from request config, marker, or use should_use_headless()
    headless = getattr(request.config, 'headless', None)
    if headless is None:
        headless_marker = request.node.get_closest_marker('headless')
        headless = headless_marker.args[0] if headless_marker else should_use_headless()
    
    logger.info(f"Creating Chrome browser for test: {request.node.name}")
    
    # Create Chrome WebDriver instance using DriverFactory.create_chrome_driver with headless setting
    driver = DriverFactory.create_chrome_driver(headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield Chrome WebDriver instance to the test
    yield driver
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        screenshot_manager = ScreenshotManager()
        screenshot_manager.capture_failure_screenshot(driver, request.node.name)
    
    # Finally, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='function')
def firefox_browser(request):
    """
    Pytest fixture that specifically provides a Firefox WebDriver instance
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.Firefox: Firefox WebDriver instance
    """
    # Retrieve headless mode from request config, marker, or use should_use_headless()
    headless = getattr(request.config, 'headless', None)
    if headless is None:
        headless_marker = request.node.get_closest_marker('headless')
        headless = headless_marker.args[0] if headless_marker else should_use_headless()
    
    logger.info(f"Creating Firefox browser for test: {request.node.name}")
    
    # Create Firefox WebDriver instance using DriverFactory.create_firefox_driver with headless setting
    driver = DriverFactory.create_firefox_driver(headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield Firefox WebDriver instance to the test
    yield driver
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        screenshot_manager = ScreenshotManager()
        screenshot_manager.capture_failure_screenshot(driver, request.node.name)
    
    # Finally, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='function')
def edge_browser(request):
    """
    Pytest fixture that specifically provides an Edge WebDriver instance
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.Edge: Edge WebDriver instance
    """
    # Retrieve headless mode from request config, marker, or use should_use_headless()
    headless = getattr(request.config, 'headless', None)
    if headless is None:
        headless_marker = request.node.get_closest_marker('headless')
        headless = headless_marker.args[0] if headless_marker else should_use_headless()
    
    logger.info(f"Creating Edge browser for test: {request.node.name}")
    
    # Create Edge WebDriver instance using DriverFactory.create_edge_driver with headless setting
    driver = DriverFactory.create_edge_driver(headless=headless)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield Edge WebDriver instance to the test
    yield driver
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        screenshot_manager = ScreenshotManager()
        screenshot_manager.capture_failure_screenshot(driver, request.node.name)
    
    # Finally, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='function')
def headless_browser(request):
    """
    Pytest fixture that provides a headless browser instance for faster test execution
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        webdriver.WebDriver: Headless WebDriver instance
    """
    # Retrieve browser_type from request config, marker, or default to BROWSERS['CHROME']
    browser_type = getattr(request.config, 'browser', None)
    if browser_type is None:
        browser_type = request.node.get_closest_marker('browser')
        browser_type = browser_type.args[0] if browser_type else BROWSERS['CHROME']
    
    logger.info(f"Creating headless {browser_type} browser")
    
    # Create WebDriver instance using DriverFactory.get_driver with browser_type and headless=True
    driver = DriverFactory.get_driver(browser_type=browser_type, headless=True)
    
    # Set implicit wait timeout from TIMEOUTS['DEFAULT']
    driver.implicitly_wait(TIMEOUTS['DEFAULT'])
    
    # Yield WebDriver instance to the test
    yield driver
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        screenshot_manager = ScreenshotManager()
        screenshot_manager.capture_failure_screenshot(driver, request.node.name)
    
    # Finally, quit the WebDriver instance
    DriverFactory.quit_driver(driver)


@pytest.fixture(scope='function')
def take_screenshot_on_failure(request, browser):
    """
    Pytest fixture that captures a screenshot when a test fails
    
    Args:
        request: pytest.FixtureRequest
        browser: webdriver.WebDriver
        
    Returns:
        None: No return value
    """
    # Initialize ScreenshotManager
    screenshot_manager = ScreenshotManager()
    
    # Yield to allow test execution
    yield
    
    # After test, check if test failed using request.node.report_call.failed
    if hasattr(request.node, 'report_call') and request.node.report_call.failed:
        test_name = request.node.name
        screenshot_manager.capture_failure_screenshot(browser, test_name)
        logger.info(f"Screenshot captured for failed test: {test_name}")