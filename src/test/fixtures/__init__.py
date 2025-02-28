"""
Package initialization file for the fixtures package in the Storydoc test automation framework.
This file makes the fixture modules accessible as a Python package and may expose commonly used fixtures for simplified imports within the testing framework.
"""

# Import browser fixtures
from .browser_fixtures import browser  # pytest:7.3+
from .browser_fixtures import headless_browser  # pytest:7.3+
from .browser_fixtures import chrome_browser  # pytest:7.3+
from .browser_fixtures import firefox_browser  # pytest:7.3+
from .browser_fixtures import edge_browser  # pytest:7.3+

# Import user fixtures
from .user_fixtures import test_user  # pytest:7.3+
from .user_fixtures import registered_user  # pytest:7.3+
from .user_fixtures import authenticated_user  # pytest:7.3+

__all__ = [
    "browser",
    "headless_browser",
    "chrome_browser",
    "firefox_browser",
    "edge_browser",
    "test_user",
    "registered_user",
    "authenticated_user",
]