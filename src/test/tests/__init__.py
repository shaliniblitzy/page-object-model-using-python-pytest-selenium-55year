"""
Initialization file for the tests package that provides test discovery and organization for the Storydoc automation framework.
This file exposes test modules for all core application workflows including user registration, authentication, story creation, and story sharing, establishing common test constants and providing documentation.
"""

import pytest  # pytest 7.3+
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.tests import user_registration  # src/test/tests/user_registration/__init__.py
from src.test.tests import user_authentication  # src/test/tests/user_authentication/__init__.py
from src.test.tests import story_creation  # src/test/tests/story_creation/__init__.py
from src.test.tests import story_sharing  # src/test/tests/story_sharing/__init__.py
from src.test.tests import performance  # src/test/tests/performance/__init__.py
from src.test.tests import end_to_end  # src/test/tests/end_to_end/__init__.py

VERSION = "1.0.0"
TESTS_PACKAGE_NAME = "Storydoc Automation Test Suite"
REGISTRATION_TIMEOUT = 30
AUTHENTICATION_TIMEOUT = 20
STORY_CREATION_TIMEOUT = 45
STORY_SHARING_TIMEOUT = 60
FULL_WORKFLOW_TIMEOUT = 180
TEST_MODULES = [user_registration, user_authentication, story_creation, story_sharing, performance, end_to_end]


def initialize_test_suite():
    """
    Initializes the test suite by loading all test modules and logging initialization information
    
    Returns:
        bool: True if initialization was successful
    """
    log_info("Initializing test suite")
    log_info(f"Version: {VERSION}")
    log_info(f"Loaded test modules: {[module.__name__ for module in TEST_MODULES]}")
    return True