"""
Configuration module for browser settings in the Storydoc test automation framework.

This module defines browser constants, options, and helper functions for configuring
WebDriver instances across different browsers.
"""

import os
import logging
from typing import Union, Dict, Any

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from .constants import BROWSERS, TIMEOUTS

# Default browser settings
DEFAULT_BROWSER = BROWSERS.get('CHROME', 'chrome')
DEFAULT_WINDOW_WIDTH = 1920
DEFAULT_WINDOW_HEIGHT = 1080

# Browser-specific command line arguments
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-popup-blocking'
]

FIREFOX_OPTIONS = [
    '--width=1920',
    '--height=1080',
    '--private'
]

EDGE_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions'
]

# Mapping of browser types to their options
BROWSER_ARGUMENTS = {
    BROWSERS['CHROME']: CHROME_OPTIONS,
    BROWSERS['FIREFOX']: FIREFOX_OPTIONS,
    BROWSERS['EDGE']: EDGE_OPTIONS
}

# Default implicit wait timeout (0 means no implicit wait)
IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '0'))

# Logger for this module
logger = logging.getLogger(__name__)


def should_use_headless() -> bool:
    """
    Determine if browser should be run in headless mode based on environment settings.
    
    Returns:
        bool: True if headless mode should be used, False otherwise
    """
    headless_mode = os.getenv('HEADLESS_MODE', 'false').lower()
    return headless_mode in ('true', '1', 'yes')


def get_browser_options(browser_type: str = None, headless: bool = None) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions]:
    """
    Generate browser-specific options based on browser type and configuration.
    
    Args:
        browser_type: Type of browser (chrome, firefox, edge)
        headless: Whether to run browser in headless mode
    
    Returns:
        Browser-specific options object
    """
    # Set defaults if not provided
    browser_type = browser_type or DEFAULT_BROWSER
    if headless is None:
        headless = should_use_headless()
    
    # Create browser-specific options
    if browser_type == BROWSERS['CHROME']:
        options = ChromeOptions()
        
        # Add browser-specific arguments
        for arg in BROWSER_ARGUMENTS.get(browser_type, []):
            options.add_argument(arg)
        
        # Add headless mode if needed
        if headless:
            # Use new headless mode for Chrome version 109+
            options.add_argument('--headless=new')
        
        # Set window size for consistent viewport
        options.add_argument(f'--window-size={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}')
        
    elif browser_type == BROWSERS['FIREFOX']:
        options = FirefoxOptions()
        
        # Add browser-specific arguments
        for arg in BROWSER_ARGUMENTS.get(browser_type, []):
            options.add_argument(arg)
        
        # Add headless mode if needed
        if headless:
            options.add_argument('--headless')
        
    elif browser_type == BROWSERS['EDGE']:
        options = EdgeOptions()
        
        # Add browser-specific arguments
        for arg in BROWSER_ARGUMENTS.get(browser_type, []):
            options.add_argument(arg)
        
        # Add headless mode if needed
        if headless:
            options.add_argument('--headless')
        
        # Set window size for consistent viewport
        options.add_argument(f'--window-size={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}')
        
    else:
        logger.warning(f"Unsupported browser type: {browser_type}. Using Chrome options as fallback.")
        options = ChromeOptions()
        
        # Add default Chrome arguments
        for arg in CHROME_OPTIONS:
            options.add_argument(arg)
        
        # Add headless mode if needed
        if headless:
            options.add_argument('--headless=new')
        
        # Set window size for consistent viewport
        options.add_argument(f'--window-size={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}')
    
    return options


def get_browser_name(browser_type: str) -> str:
    """
    Get human-readable browser name for logging and reporting.
    
    Args:
        browser_type: Browser type string
    
    Returns:
        Human-readable browser name
    """
    if browser_type == BROWSERS['CHROME']:
        return 'Google Chrome'
    elif browser_type == BROWSERS['FIREFOX']:
        return 'Mozilla Firefox'
    elif browser_type == BROWSERS['EDGE']:
        return 'Microsoft Edge'
    else:
        return browser_type


def get_browser_timeout_settings() -> Dict[str, int]:
    """
    Get timeout settings for browser configuration.
    
    Returns:
        Dictionary with page_load_timeout, script_timeout, and implicit_wait values
    """
    return {
        'page_load_timeout': int(os.getenv('PAGE_LOAD_TIMEOUT', TIMEOUTS.get('PAGE_LOAD', 30))),
        'script_timeout': int(os.getenv('SCRIPT_TIMEOUT', TIMEOUTS.get('SCRIPT', 30))),
        'implicit_wait': IMPLICIT_WAIT
    }


def validate_browser_type(browser_type: str) -> bool:
    """
    Validate if provided browser type is supported.
    
    Args:
        browser_type: Browser type to validate
    
    Returns:
        True if browser type is supported, False otherwise
    """
    if browser_type in BROWSERS.values():
        return True
    
    logger.warning(f"Unsupported browser type: {browser_type}. Supported types: {', '.join(BROWSERS.values())}")
    return False


def get_driver_preferences(browser_type: str) -> Dict[str, Any]:
    """
    Get browser-specific preferences for WebDriver.
    
    Args:
        browser_type: Type of browser
    
    Returns:
        Dictionary with browser preferences
    """
    prefs = {}
    
    if browser_type == BROWSERS['CHROME']:
        # Chrome preferences
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': os.getenv('DOWNLOAD_PATH', os.getcwd()),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
    elif browser_type == BROWSERS['FIREFOX']:
        # Firefox preferences
        prefs = {
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir': os.getenv('DOWNLOAD_PATH', os.getcwd()),
            'browser.helperApps.neverAsk.saveToDisk': 'application/pdf,application/x-pdf',
            'browser.privatebrowsing.autostart': True
        }
    elif browser_type == BROWSERS['EDGE']:
        # Edge preferences
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': os.getenv('DOWNLOAD_PATH', os.getcwd()),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False
        }
    
    return prefs