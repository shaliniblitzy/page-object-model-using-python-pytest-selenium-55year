"""
Factory class for creating and managing WebDriver instances for browser automation in the Storydoc test automation framework.

Provides a unified interface for initializing different browser drivers with appropriate configuration settings
and implements patterns for driver lifecycle management.
"""

import os  # standard library
import datetime  # standard library
from typing import Dict, Any, Optional, Union  # standard library

import selenium.webdriver as webdriver  # selenium 4.10+
from selenium.webdriver.support.ui import WebDriverWait  # selenium 4.10+
from selenium.webdriver.support import expected_conditions as EC  # selenium 4.10+
from selenium.webdriver.chrome.service import Service as ChromeService  # selenium 4.10+
from selenium.webdriver.firefox.service import Service as FirefoxService  # selenium 4.10+
from selenium.webdriver.edge.service import Service as EdgeService  # selenium 4.10+
from selenium.common.exceptions import WebDriverException  # selenium 4.10+

from webdriver_manager.chrome import ChromeDriverManager  # webdriver-manager 4.0+
from webdriver_manager.firefox import GeckoDriverManager  # webdriver-manager 4.0+
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # webdriver-manager 4.0+

# Import internal constants and utilities
from ..config.constants import BROWSERS, TIMEOUTS
from ..config.browser_config import get_browser_options
from .config_manager import get_config
from .logger import log_info, log_debug, log_error
from .wait_helper import WaitUtils

# Dictionary to store active driver instances
_driver_instances = {}

# Map browser types to their respective driver managers
_DRIVER_MANAGERS = {
    BROWSERS['CHROME']: ChromeDriverManager,
    BROWSERS['FIREFOX']: GeckoDriverManager,
    BROWSERS['EDGE']: EdgeChromiumDriverManager
}

# Map browser types to their respective service classes
_DRIVER_SERVICES = {
    BROWSERS['CHROME']: ChromeService,
    BROWSERS['FIREFOX']: FirefoxService,
    BROWSERS['EDGE']: EdgeService
}

# Map browser types to their respective WebDriver classes
_WEBDRIVER_CLASSES = {
    BROWSERS['CHROME']: webdriver.Chrome,
    BROWSERS['FIREFOX']: webdriver.Firefox,
    BROWSERS['EDGE']: webdriver.Edge
}

def get_driver(browser_type: str = None, headless: bool = None, browser_options: Dict[str, Any] = None) -> webdriver.WebDriver:
    """
    Creates and returns a WebDriver instance for the specified browser type.
    
    Args:
        browser_type: Type of browser to create a driver for ('chrome', 'firefox', 'edge')
        headless: Whether to run the browser in headless mode
        browser_options: Additional browser-specific options
        
    Returns:
        WebDriver instance configured according to specifications
    """
    # Set default browser_type to Chrome if not provided
    if browser_type is None:
        browser_type = BROWSERS.get('CHROME', 'chrome')
        
    # Set default headless mode from configuration if not provided
    if headless is None:
        headless = get_config('headless_mode', False)
    
    log_info(f"Creating {browser_type} WebDriver instance (headless: {headless})")
    
    try:
        # Get browser options
        options = browser_options if browser_options is not None else get_browser_options(browser_type, headless)
        
        # Get the appropriate driver manager
        driver_manager = _DRIVER_MANAGERS.get(browser_type)
        if not driver_manager:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # Get the appropriate service class
        service_class = _DRIVER_SERVICES.get(browser_type)
        if not service_class:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # Get the appropriate WebDriver class
        driver_class = _WEBDRIVER_CLASSES.get(browser_type)
        if not driver_class:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # Install driver and create service
        service = service_class(driver_manager().install())
        
        # Create WebDriver instance
        driver = driver_class(service=service, options=options)
        
        # Configure WebDriver timeouts
        driver.set_page_load_timeout(TIMEOUTS['PAGE_LOAD'])
        driver.set_script_timeout(TIMEOUTS['SCRIPT'])
        
        # Maximize window if not in headless mode
        if not headless:
            driver.maximize_window()
        
        # Store driver instance for tracking
        session_id = driver.session_id
        _driver_instances[session_id] = driver
        
        log_info(f"Created {browser_type} WebDriver instance with session ID: {session_id}")
        return driver
    
    except WebDriverException as e:
        log_error(f"Failed to create {browser_type} WebDriver: {str(e)}")
        raise
    
    except Exception as e:
        log_error(f"Unexpected error creating {browser_type} WebDriver: {str(e)}")
        raise

def quit_driver(driver: webdriver.WebDriver) -> bool:
    """
    Quits the WebDriver instance and cleans up resources.
    
    Args:
        driver: WebDriver instance to quit
        
    Returns:
        True if driver was successfully quit, False otherwise
    """
    if driver is None:
        log_debug("Cannot quit driver: driver is None")
        return False
    
    try:
        # Get session ID before quitting
        session_id = driver.session_id
        
        # Quit the driver
        driver.quit()
        
        # Remove from tracking dictionary
        if session_id in _driver_instances:
            del _driver_instances[session_id]
        
        log_info(f"Quit WebDriver session: {session_id}")
        return True
    
    except Exception as e:
        log_error(f"Error quitting WebDriver: {str(e)}")
        return False

def quit_all_drivers() -> None:
    """
    Quits all active WebDriver instances.
    """
    log_info("Quitting all active WebDriver instances")
    
    # Create a copy of the keys to avoid modification during iteration
    session_ids = list(_driver_instances.keys())
    
    for session_id in session_ids:
        try:
            driver = _driver_instances.get(session_id)
            if driver:
                log_debug(f"Quitting WebDriver session: {session_id}")
                quit_driver(driver)
        except Exception as e:
            log_error(f"Error quitting WebDriver session {session_id}: {str(e)}")

def create_chrome_driver(headless: bool = None, chrome_options: Dict[str, Any] = None) -> webdriver.Chrome:
    """
    Creates a Chrome WebDriver instance with specified options.
    
    Args:
        headless: Whether to run Chrome in headless mode
        chrome_options: Additional Chrome-specific options
        
    Returns:
        Chrome WebDriver instance
    """
    return get_driver(BROWSERS['CHROME'], headless, chrome_options)

def create_firefox_driver(headless: bool = None, firefox_options: Dict[str, Any] = None) -> webdriver.Firefox:
    """
    Creates a Firefox WebDriver instance with specified options.
    
    Args:
        headless: Whether to run Firefox in headless mode
        firefox_options: Additional Firefox-specific options
        
    Returns:
        Firefox WebDriver instance
    """
    return get_driver(BROWSERS['FIREFOX'], headless, firefox_options)

def create_edge_driver(headless: bool = None, edge_options: Dict[str, Any] = None) -> webdriver.Edge:
    """
    Creates an Edge WebDriver instance with specified options.
    
    Args:
        headless: Whether to run Edge in headless mode
        edge_options: Additional Edge-specific options
        
    Returns:
        Edge WebDriver instance
    """
    return get_driver(BROWSERS['EDGE'], headless, edge_options)

def is_driver_alive(driver: webdriver.WebDriver) -> bool:
    """
    Checks if a WebDriver instance is still alive and usable.
    
    Args:
        driver: WebDriver instance to check
        
    Returns:
        True if driver is alive, False otherwise
    """
    if driver is None:
        return False
    
    try:
        # Try to get the current URL as a simple check
        _ = driver.current_url
        log_debug(f"WebDriver session {driver.session_id} is alive")
        return True
    except Exception:
        log_debug(f"WebDriver session is not alive")
        return False

def take_screenshot(driver: webdriver.WebDriver, file_name: str = None) -> Optional[str]:
    """
    Takes a screenshot using the provided WebDriver instance.
    
    Args:
        driver: WebDriver instance to use for taking screenshot
        file_name: Optional file name for the screenshot
        
    Returns:
        Path to the saved screenshot file
    """
    if not is_driver_alive(driver):
        log_error("Cannot take screenshot: WebDriver is not alive")
        return None
    
    try:
        # Generate a file name with timestamp if not provided
        if file_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"screenshot_{timestamp}.png"
        elif not file_name.endswith('.png'):
            file_name = f"{file_name}.png"
        
        # Get screenshots directory from configuration
        screenshots_dir = get_config('screenshot_dir', 'screenshots')
        
        # Ensure directory exists
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Full path to the screenshot file
        file_path = os.path.join(screenshots_dir, file_name)
        
        # Take screenshot
        driver.save_screenshot(file_path)
        
        log_info(f"Screenshot saved to {file_path}")
        return file_path
    
    except Exception as e:
        log_error(f"Error taking screenshot: {str(e)}")
        return None

def refresh_driver(driver: webdriver.WebDriver) -> webdriver.WebDriver:
    """
    Refreshes the WebDriver session when it becomes stale.
    
    Args:
        driver: WebDriver instance to refresh
        
    Returns:
        Refreshed WebDriver instance or original if refresh failed
    """
    if is_driver_alive(driver):
        log_debug("Driver is already alive, no need to refresh")
        return driver
    
    log_info("Refreshing stale WebDriver session")
    
    try:
        # Extract browser type and options from original driver if possible
        browser_type = None
        headless = None
        
        if hasattr(driver, '_browser_type'):
            browser_type = driver._browser_type
        
        if hasattr(driver, '_headless'):
            headless = driver._headless
        
        # Create new driver with same configuration
        new_driver = get_driver(browser_type, headless)
        
        log_info(f"Successfully refreshed WebDriver session")
        return new_driver
    
    except Exception as e:
        log_error(f"Failed to refresh WebDriver session: {str(e)}")
        return driver

class DriverFactory:
    """
    Factory class for creating and managing WebDriver instances.
    """
    
    @staticmethod
    def get_driver(browser_type: str = None, headless: bool = None) -> webdriver.WebDriver:
        """
        Static method to get a WebDriver instance for the specified browser.
        
        Args:
            browser_type: Type of browser ('chrome', 'firefox', 'edge')
            headless: Whether to run in headless mode
            
        Returns:
            WebDriver instance
        """
        return get_driver(browser_type, headless)
    
    @staticmethod
    def quit_driver(driver: webdriver.WebDriver) -> bool:
        """
        Static method to quit a WebDriver instance.
        
        Args:
            driver: WebDriver instance to quit
            
        Returns:
            True if driver was successfully quit, False otherwise
        """
        return quit_driver(driver)
    
    @staticmethod
    def quit_all_drivers() -> None:
        """
        Static method to quit all active WebDriver instances.
        """
        quit_all_drivers()
    
    @staticmethod
    def create_chrome_driver(headless: bool = None) -> webdriver.Chrome:
        """
        Static method to create a Chrome WebDriver instance.
        
        Args:
            headless: Whether to run Chrome in headless mode
            
        Returns:
            Chrome WebDriver instance
        """
        return create_chrome_driver(headless)
    
    @staticmethod
    def create_firefox_driver(headless: bool = None) -> webdriver.Firefox:
        """
        Static method to create a Firefox WebDriver instance.
        
        Args:
            headless: Whether to run Firefox in headless mode
            
        Returns:
            Firefox WebDriver instance
        """
        return create_firefox_driver(headless)
    
    @staticmethod
    def create_edge_driver(headless: bool = None) -> webdriver.Edge:
        """
        Static method to create an Edge WebDriver instance.
        
        Args:
            headless: Whether to run Edge in headless mode
            
        Returns:
            Edge WebDriver instance
        """
        return create_edge_driver(headless)
    
    @staticmethod
    def is_driver_alive(driver: webdriver.WebDriver) -> bool:
        """
        Static method to check if a WebDriver instance is still alive.
        
        Args:
            driver: WebDriver instance to check
            
        Returns:
            True if driver is alive, False otherwise
        """
        return is_driver_alive(driver)
    
    @staticmethod
    def take_screenshot(driver: webdriver.WebDriver, file_name: str = None) -> Optional[str]:
        """
        Static method to take a screenshot with WebDriver.
        
        Args:
            driver: WebDriver instance to use
            file_name: Optional file name for the screenshot
            
        Returns:
            Path to the saved screenshot file
        """
        return take_screenshot(driver, file_name)
    
    @staticmethod
    def refresh_driver(driver: webdriver.WebDriver) -> webdriver.WebDriver:
        """
        Static method to refresh a WebDriver session.
        
        Args:
            driver: WebDriver instance to refresh
            
        Returns:
            Refreshed WebDriver instance
        """
        return refresh_driver(driver)

class WebDriverWrapper:
    """
    Wrapper class for WebDriver that adds utilities and context management.
    """
    
    def __init__(self, driver: webdriver.WebDriver, timeout: int = None):
        """
        Initialize the WebDriverWrapper with a WebDriver instance.
        
        Args:
            driver: WebDriver instance to wrap
            timeout: Default timeout for wait operations
        """
        self._driver = driver
        self._timeout = timeout or TIMEOUTS['DEFAULT']
        self._wait = WebDriverWait(driver, self._timeout)
        
        log_info(f"Created WebDriverWrapper with timeout {self._timeout}s")
    
    def __enter__(self):
        """
        Context manager entry method.
        
        Returns:
            Self instance for context management
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method that quits the driver.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception instance if an exception was raised
            exc_tb: Traceback if an exception was raised
        """
        self.quit()
        log_info("WebDriverWrapper context exited, driver quit")
    
    def quit(self):
        """
        Quits the WebDriver instance.
        """
        if self._driver:
            quit_driver(self._driver)
            self._driver = None
    
    def get_driver(self) -> webdriver.WebDriver:
        """
        Gets the underlying WebDriver instance.
        
        Returns:
            The wrapped WebDriver instance
        """
        return self._driver
    
    def get_wait(self) -> WebDriverWait:
        """
        Gets the WebDriverWait instance.
        
        Returns:
            The WebDriverWait instance
        """
        return self._wait
    
    def take_screenshot(self, file_name: str = None) -> Optional[str]:
        """
        Takes a screenshot with the wrapped WebDriver.
        
        Args:
            file_name: Optional file name for the screenshot
            
        Returns:
            Path to the saved screenshot file
        """
        return take_screenshot(self._driver, file_name)
    
    def wait_for_page_ready(self, timeout: int = None) -> bool:
        """
        Waits for page to be fully loaded.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            True if page is ready, False otherwise
        """
        timeout = timeout or self._timeout
        return WaitUtils.wait_for_page_ready(self._driver, timeout)