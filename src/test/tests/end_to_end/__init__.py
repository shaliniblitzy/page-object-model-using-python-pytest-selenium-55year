"""
Initialization file for the end-to-end tests package that defines test discovery and organization for comprehensive workflow tests validating complete user journeys through the Storydoc application, from registration to story sharing with email verification.
"""

import pytest  # pytest 7.3+
from src.test.utilities.logger import get_logger  # src/test/utilities/logger.py
from .test_user_journey import TestUserJourney  # src/test/tests/end_to_end/test_user_journey.py
from .test_story_lifecycle import TestStoryLifecycle  # src/test/tests/end_to_end/test_story_lifecycle.py
from .test_complete_workflow import TestCompleteWorkflow  # src/test/tests/end_to_end/test_complete_workflow.py

logger = get_logger()

TEST_MODULES = [TestUserJourney, TestStoryLifecycle, TestCompleteWorkflow]

MODULE_DESCRIPTIONS = {
    TestUserJourney: 'User journey through Storydoc application',
    TestStoryLifecycle: 'Lifecycle of a story from creation to sharing',
    TestCompleteWorkflow: 'Complete workflow from registration to sharing'
}


def get_end_to_end_test_modules():
    """Returns a list of all end-to-end test modules"""
    return TEST_MODULES


def get_module_description(module_name):
    """Returns the description for a specified test module"""
    if module_name in MODULE_DESCRIPTIONS:
        description = MODULE_DESCRIPTIONS[module_name]
        logger.info(f"Description found for module {module_name}: {description}")
        return description
    else:
        logger.warning(f"No description found for module {module_name}, using default description")
        return "No description available"


def pytest_configure(config):
    """pytest hook to configure the end-to-end test package"""
    config.addinivalue_line(
        "markers", "user_journey: mark test as part of user journey tests"
    )
    config.addinivalue_line(
        "markers", "story_lifecycle: mark test as part of story lifecycle tests"
    )
    config.addinivalue_line(
        "markers", "complete_workflow: mark test as part of complete workflow tests"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (to be deselected with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "email_verification: mark test that requires email verification"
    )
    config.addinivalue_line(
        "markers", "mailinator: mark test that uses mailinator service"
    )
    config.addinivalue_line(
        "markers", "sharing: mark test related to sharing functionality"
    )
    logger.info("Registered pytest markers for end-to-end tests")