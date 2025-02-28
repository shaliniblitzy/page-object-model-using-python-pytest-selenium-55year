"""
Test module that measures and validates page load times for various pages in the Storydoc application.
Ensures page navigation operations meet the defined Service Level Agreement (SLA) requirements
and provides performance metrics for reporting.
"""

import pytest  # pytest latest
import time  # time built-in
from typing import Any, Dict, Optional  # typing built-in

# Internal imports
from ..utilities.performance_monitor import record_page_load_time, PerformanceMonitor
from ..utilities.timing_helper import Timer, get_formatted_time, is_within_sla
from ..config.sla_config import is_within_operation_sla, OPERATION_SLAS
from ..config.timeout_config import PAGE_LOAD_TIMEOUT
from ..utilities.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_page_load_time(page_object: Any, page_name: str) -> float:
    """
    Helper function to measure page load time for a specific page navigation
    
    Args:
        page_object: Page object to navigate to
        page_name: Name of the page for logging and metrics
        
    Returns:
        float: Page load time in seconds
    """
    logger.info(f"Measuring page load time for: {page_name}")
    
    # Create timer for measuring page load
    timer = Timer(name=f"{page_name}_load", category="page_load")
    
    # Start the timer
    timer.start()
    
    # Call the open() method on the page object to navigate to the page
    page_object.open()
    
    # Wait for the page to be fully loaded
    page_object.is_loaded()
    
    # Stop the timer and get the elapsed time
    load_time = timer.stop()
    
    # Log the measured page load time
    logger.info(f"Page load time for {page_name}: {get_formatted_time(load_time)}")
    
    # Record the page load time in the performance monitor
    record_page_load_time(page_name, load_time, {"page": page_name})
    
    # Return the measured load time
    return load_time


def assert_page_load_time_within_sla(page_name: str, load_time: float) -> None:
    """
    Helper function to assert that page load time is within SLA requirements
    
    Args:
        page_name: Name of the page being tested
        load_time: Measured load time in seconds
    """
    # Check if the load_time is within SLA for page navigation operation
    is_compliant = is_within_operation_sla("page_navigation", load_time)
    
    # Log the SLA compliance result
    if is_compliant:
        logger.info(f"Page load time for {page_name} is within SLA")
    else:
        target_time = OPERATION_SLAS["page_navigation"]["target_response_time"]
        logger.warning(f"Page load time for {page_name} ({get_formatted_time(load_time)}) exceeds SLA ({get_formatted_time(target_time)})")
    
    # Assert that load_time is within SLA with descriptive error message if it fails
    assert is_compliant, f"Page load time for {page_name} ({get_formatted_time(load_time)}) exceeds SLA"


class TestPageLoadTime:
    """
    Test class for measuring and validating page load times across the Storydoc application
    """
    
    def test_signup_page_load_time(self, signup_page):
        """
        Test to measure and validate the load time of the signup page
        
        Args:
            signup_page: Signup page object fixture
        """
        logger.info("Starting test: test_signup_page_load_time")
        
        # Measure page load time
        load_time = measure_page_load_time(signup_page, "signup_page")
        
        # Validate that the measured load time is within SLA requirements
        assert_page_load_time_within_sla("signup_page", load_time)
        
        logger.info("Completed test: test_signup_page_load_time")
    
    def test_signin_page_load_time(self, signin_page):
        """
        Test to measure and validate the load time of the signin page
        
        Args:
            signin_page: Signin page object fixture
        """
        logger.info("Starting test: test_signin_page_load_time")
        
        # Measure page load time
        load_time = measure_page_load_time(signin_page, "signin_page")
        
        # Validate that the measured load time is within SLA requirements
        assert_page_load_time_within_sla("signin_page", load_time)
        
        logger.info("Completed test: test_signin_page_load_time")
    
    def test_dashboard_page_load_time(self, dashboard_page, authenticated_user):
        """
        Test to measure and validate the load time of the dashboard page
        
        Args:
            dashboard_page: Dashboard page object fixture
            authenticated_user: Authenticated user fixture for accessing the dashboard
        """
        logger.info("Starting test: test_dashboard_page_load_time")
        
        # Measure page load time
        load_time = measure_page_load_time(dashboard_page, "dashboard_page")
        
        # Validate that the measured load time is within SLA requirements
        assert_page_load_time_within_sla("dashboard_page", load_time)
        
        logger.info("Completed test: test_dashboard_page_load_time")
    
    def test_story_editor_page_load_time(self, story_editor_page, authenticated_user):
        """
        Test to measure and validate the load time of the story editor page
        
        Args:
            story_editor_page: Story editor page object fixture
            authenticated_user: Authenticated user fixture for accessing the story editor
        """
        logger.info("Starting test: test_story_editor_page_load_time")
        
        # Measure page load time
        load_time = measure_page_load_time(story_editor_page, "story_editor_page")
        
        # Validate that the measured load time is within SLA requirements
        assert_page_load_time_within_sla("story_editor_page", load_time)
        
        logger.info("Completed test: test_story_editor_page_load_time")
    
    def test_sequential_page_navigation(self, signup_page, signin_page, dashboard_page, story_editor_page):
        """
        Test to measure load times for sequential navigation through multiple pages
        
        Args:
            signup_page: Signup page object fixture
            signin_page: Signin page object fixture
            dashboard_page: Dashboard page object fixture
            story_editor_page: Story editor page object fixture
        """
        logger.info("Starting test: test_sequential_page_navigation")
        
        # Measure load time for signup page
        signup_load_time = measure_page_load_time(signup_page, "signup_page")
        
        # Measure load time for signin page
        signin_load_time = measure_page_load_time(signin_page, "signin_page")
        
        # Authenticate user (simulate login)
        logger.info("Simulating user authentication")
        
        # Measure load time for dashboard page
        dashboard_load_time = measure_page_load_time(dashboard_page, "dashboard_page")
        
        # Measure load time for story editor page
        editor_load_time = measure_page_load_time(story_editor_page, "story_editor_page")
        
        # Calculate total navigation time
        total_time = signup_load_time + signin_load_time + dashboard_load_time + editor_load_time
        logger.info(f"Total navigation time: {get_formatted_time(total_time)}")
        
        # Assert that each page load is within SLA requirements
        assert_page_load_time_within_sla("signup_page", signup_load_time)
        assert_page_load_time_within_sla("signin_page", signin_load_time)
        assert_page_load_time_within_sla("dashboard_page", dashboard_load_time)
        assert_page_load_time_within_sla("story_editor_page", editor_load_time)
        
        # Assert that total navigation time is within reasonable limits
        reasonable_total = 4 * OPERATION_SLAS["page_navigation"]["target_response_time"]
        assert total_time <= reasonable_total, f"Total navigation time ({get_formatted_time(total_time)}) exceeds reasonable limit"
        
        logger.info(f"Completed test: test_sequential_page_navigation with summary of all page load times")
    
    def test_page_load_with_cache_comparison(self, signin_page):
        """
        Test to compare cold vs warm cache page load times
        
        Args:
            signin_page: Signin page object fixture
        """
        logger.info("Starting test: test_page_load_with_cache_comparison")
        
        # Measure initial (cold) page load time
        cold_load_time = measure_page_load_time(signin_page, "signin_page_cold")
        
        # Clear browser cookies but maintain cache
        signin_page.driver.delete_all_cookies()
        
        # Measure second (warm) page load time
        warm_load_time = measure_page_load_time(signin_page, "signin_page_warm")
        
        # Calculate and log the difference between cold and warm loads
        improvement = cold_load_time - warm_load_time
        improvement_percent = (improvement / cold_load_time) * 100 if cold_load_time > 0 else 0
        
        logger.info(f"Cold load: {get_formatted_time(cold_load_time)}, Warm load: {get_formatted_time(warm_load_time)}")
        logger.info(f"Cache improvement: {get_formatted_time(improvement)} ({improvement_percent:.2f}%)")
        
        # Assert that both load times are within SLA requirements
        assert_page_load_time_within_sla("signin_page_cold", cold_load_time)
        assert_page_load_time_within_sla("signin_page_warm", warm_load_time)
        
        # Assert that warm load is faster than cold load
        assert warm_load_time < cold_load_time, "Warm cache load time should be faster than cold load time"
        
        logger.info("Completed test: test_page_load_with_cache_comparison with comparison results")