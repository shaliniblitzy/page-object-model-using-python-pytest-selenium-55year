"""
Initialization file for the utilities package that provides convenient imports of
all helper modules for the Storydoc test automation framework.

This file enables easier imports of utility classes and functions throughout the test codebase.
"""

# Version number
__version__ = "1.0.0"

# Import utilities
from .config_manager import ConfigManager
from .driver_factory import DriverFactory, get_driver as create_driver, quit_driver
from .email_helper import EmailHelper

# Create alias for generate_email_address as generate_random_email
def generate_random_email(prefix=None):
    """Generate a random email address for testing purposes."""
    helper = EmailHelper()
    return helper.generate_email_address(prefix)

# Import wait utilities
from .wait_helper import WaitUtils, CustomExpectedConditions, wait_for_element_state

# Create specialized wait functions
def wait_for_element_present(driver, locator, timeout=None):
    """Wait for element to be present in the DOM."""
    return wait_for_element_state(driver, locator, state='present', timeout=timeout)

def wait_for_element_visible(driver, locator, timeout=None):
    """Wait for element to be visible."""
    return wait_for_element_state(driver, locator, state='visible', timeout=timeout)

def wait_for_element_clickable(driver, locator, timeout=None):
    """Wait for element to be clickable."""
    return wait_for_element_state(driver, locator, state='clickable', timeout=timeout)

# Define public API
__all__ = [
    "ConfigManager",
    "DriverFactory",
    "EmailHelper",
    "WaitUtils",
    "CustomExpectedConditions",
    "create_driver",
    "quit_driver",
    "generate_random_email",
    "wait_for_element_present",
    "wait_for_element_visible",
    "wait_for_element_clickable"
]