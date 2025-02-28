"""
Module providing pytest fixtures for performance monitoring and measurement in the Storydoc test automation framework.
These fixtures facilitate the collection, analysis, and reporting of performance metrics for different test scenarios.
"""

import pytest
import time
import datetime
import os
from typing import Callable, Dict, Optional

# Internal imports
from ..utilities.performance_monitor import (
    PerformanceMonitor, PerformanceContext, DEFAULT_REPORT_PATH
)
from ..utilities.timing_helper import (
    Timer, TimingContext, get_formatted_time, is_within_sla
)
from ..config.sla_config import OPERATION_SLAS, TEST_TYPE_SLAS
from ..utilities.logger import get_logger

# Set up logger
logger = get_logger(__name__)


@pytest.fixture(scope='function')
def performance_monitor():
    """
    Pytest fixture that provides a PerformanceMonitor instance for measuring test performance
    
    Returns:
        PerformanceMonitor: Instance of PerformanceMonitor for recording performance metrics
    """
    # Initialize a new PerformanceMonitor instance
    monitor = PerformanceMonitor()
    logger.info("Starting performance monitoring for test")
    
    # Yield the PerformanceMonitor instance to the test
    yield monitor
    
    # After test completes, log performance statistics
    logger.info("Performance monitoring completed")
    
    # Clear performance data to avoid affecting other tests
    monitor.clear_performance_data()


@pytest.fixture(scope='session')
def session_performance_monitor():
    """
    Pytest fixture that provides a PerformanceMonitor instance with session scope
    
    Returns:
        PerformanceMonitor: Instance of PerformanceMonitor for recording performance metrics across the entire test session
    """
    # Initialize a new PerformanceMonitor instance
    monitor = PerformanceMonitor()
    logger.info("Starting session performance monitoring")
    
    # Yield the PerformanceMonitor instance to all tests in the session
    yield monitor
    
    # After all tests complete, generate a comprehensive performance report
    report_path = monitor.generate_report(report_name="session_performance_report")
    logger.info(f"Session performance report generated: {report_path}")
    
    # Log session performance statistics
    summary = monitor.get_performance_summary()
    logger.info(f"Session performance summary: {len(summary)} categories recorded")


@pytest.fixture(scope='class')
def class_performance_monitor():
    """
    Pytest fixture that provides a PerformanceMonitor instance with class scope
    
    Returns:
        PerformanceMonitor: Instance of PerformanceMonitor for recording performance metrics across all tests in a class
    """
    # Initialize a new PerformanceMonitor instance
    monitor = PerformanceMonitor()
    logger.info("Starting class performance monitoring")
    
    # Yield the PerformanceMonitor instance to all tests in the class
    yield monitor
    
    # After all tests in class complete, generate a class-level performance report
    report_path = monitor.generate_report(report_name="class_performance_report")
    logger.info(f"Class performance report generated: {report_path}")
    
    # Log class performance statistics
    summary = monitor.get_performance_summary()
    logger.info(f"Class performance summary: {len(summary)} categories recorded")


@pytest.fixture(scope='function')
def performance_timer():
    """
    Pytest fixture that provides a Timer instance for manual timing measurements
    
    Returns:
        Timer: Instance of Timer for precise timing measurements
    """
    # Initialize a new Timer instance with a name based on the test name
    timer = Timer(name="test_timer")
    
    # Yield the Timer instance to the test
    yield timer
    
    # After test completes, ensure timer is stopped if still running
    if timer.running:
        timer.stop()


@pytest.fixture(scope='function')
def performance_context(request):
    """
    Pytest fixture that provides a TimingContext for timing specific operations
    
    Args:
        request: pytest.FixtureRequest
        
    Returns:
        function: Factory function that returns a TimingContext instance
    """
    # Define a factory function that creates a TimingContext with specified parameters
    def create_timing_context(operation_name, category=None, log_result=True, notify_callbacks=True):
        """
        Creates a TimingContext for measuring operation execution time
        
        Args:
            operation_name: Name of the operation being timed
            category: Category for the operation (default: derived from test name)
            log_result: Whether to log the timing result
            notify_callbacks: Whether to notify timing callbacks
            
        Returns:
            TimingContext: Context manager for timing operations
        """
        # Use test name as category if not specified
        if category is None:
            category = request.node.name
            
        # Create and return a TimingContext
        return TimingContext(operation_name, category, log_result, notify_callbacks)
    
    # Return the factory function to the test
    return create_timing_context


@pytest.fixture(scope='session')
def performance_report(session_performance_monitor):
    """
    Pytest fixture that provides a function to generate performance reports
    
    Args:
        session_performance_monitor: PerformanceMonitor
        
    Returns:
        function: Function that generates and returns a performance report
    """
    # Define a function that generates a performance report
    def generate_report(name=None, path=None):
        """
        Generates a performance report using the session performance monitor
        
        Args:
            name: Name for the report file (default: auto-generated)
            path: Path where the report should be saved (default: DEFAULT_REPORT_PATH)
            
        Returns:
            str: Path to the generated report file
        """
        return session_performance_monitor.generate_report(report_name=name, report_path=path)
    
    # Return the function to the test
    return generate_report


@pytest.fixture(scope='function', autouse=True)
def test_execution_timer(request, performance_monitor):
    """
    Pytest fixture that measures and records test execution time
    
    Args:
        request: pytest.FixtureRequest
        performance_monitor: PerformanceMonitor
        
    Returns:
        None: No return value
    """
    # Record the start time of the test
    start_time = time.time()
    
    # Yield to allow test to execute
    yield
    
    # Calculate the test execution time after test completes
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Get test name and nodeid
    test_name = request.node.name
    test_id = request.node.nodeid
    
    # Determine test type based on module or markers
    test_type = "general"
    
    # Check if test has markers that indicate its type
    for marker in request.node.iter_markers():
        if marker.name in TEST_TYPE_SLAS:
            test_type = marker.name
            break
    
    # If no marker found, try to determine from nodeid
    if test_type == "general":
        # Look for keywords in the nodeid that match test types
        for known_type in TEST_TYPE_SLAS.keys():
            if known_type.lower() in test_id.lower():
                test_type = known_type
                break
    
    # Record the test execution time using performance_monitor
    performance_monitor.record_test_execution_time(
        test_name=test_name,
        test_type=test_type,
        execution_time=execution_time,
        metadata={"nodeid": test_id}
    )
    
    # Check if the execution time meets SLA requirements
    if test_type in TEST_TYPE_SLAS:
        max_duration = TEST_TYPE_SLAS[test_type].get("maximum_duration")
        if execution_time > max_duration:
            logger.warning(
                f"Test execution time ({get_formatted_time(execution_time)}) "
                f"exceeds SLA threshold ({get_formatted_time(max_duration)}) "
                f"for test type {test_type}"
            )


@pytest.fixture(scope='function')
def page_load_timer(performance_monitor):
    """
    Pytest fixture that provides a utility for measuring page load times
    
    Args:
        performance_monitor: PerformanceMonitor
        
    Returns:
        function: Function for measuring page load time
    """
    def measure_page_load(page_object, navigate_method="navigate_to", **kwargs):
        """
        Measures the time it takes to load a page
        
        Args:
            page_object: Page object with navigation method
            navigate_method: Name of the navigation method (default: 'navigate_to')
            **kwargs: Arguments to pass to the navigation method
            
        Returns:
            float: Page load time in seconds
        """
        # Get the navigation method from the page object
        navigate_func = getattr(page_object, navigate_method)
        
        # Start a timer for the page load
        timer_id = performance_monitor.start_timer(
            name=f"{page_object.__class__.__name__}.{navigate_method}",
            category="page_load"
        )
        
        # Navigate to the page
        navigate_func(**kwargs)
        
        # Stop the timer and record the measurement
        load_time = performance_monitor.stop_timer(
            timer_id, 
            metadata={"page_class": page_object.__class__.__name__}
        )
        
        return load_time
    
    return measure_page_load


@pytest.fixture(scope='function')
def element_interaction_timer(performance_monitor):
    """
    Pytest fixture that provides a utility for measuring element interaction times
    
    Args:
        performance_monitor: PerformanceMonitor
        
    Returns:
        function: Function for measuring element interaction time
    """
    def measure_interaction(element_identifier, interaction_func, **kwargs):
        """
        Measures the time it takes to interact with an element
        
        Args:
            element_identifier: Identifier for the element (e.g., locator, name)
            interaction_func: Function to perform the interaction
            **kwargs: Arguments to pass to the interaction function
            
        Returns:
            tuple: (result of interaction, interaction time in seconds)
        """
        # Start a timer for the element interaction
        timer_id = performance_monitor.start_timer(
            name=element_identifier,
            category="element_interaction"
        )
        
        # Perform the interaction
        result = interaction_func(**kwargs)
        
        # Stop the timer and record the measurement
        interaction_time = performance_monitor.stop_timer(
            timer_id, 
            metadata={"function": interaction_func.__name__}
        )
        
        return result, interaction_time
    
    return measure_interaction


@pytest.fixture(scope='function')
def performance_threshold_validator():
    """
    Pytest fixture that provides a utility for validating performance against thresholds
    
    Returns:
        function: Function for validating performance against thresholds
    """
    def validate_performance(measured_time, threshold=None, operation_type=None, operation_name=None):
        """
        Validates that a measured time is within the specified threshold or SLA
        
        Args:
            measured_time: Measured time in seconds
            threshold: Explicit threshold in seconds (overrides SLA lookup)
            operation_type: Type of operation for SLA lookup
            operation_name: Name of the operation for context in logs
            
        Raises:
            AssertionError: If the measured time exceeds the threshold
        """
        # If explicit threshold is provided, use it
        if threshold is not None:
            is_valid = measured_time <= threshold
            threshold_str = get_formatted_time(threshold)
        # Otherwise, check against SLA if operation_type is provided
        elif operation_type is not None:
            is_valid = is_within_sla(measured_time, operation_type, operation_name or "")
            
            # Get the threshold from the SLA config for the error message
            if operation_type in OPERATION_SLAS:
                threshold = OPERATION_SLAS[operation_type].get("target_response_time")
                threshold_str = get_formatted_time(threshold)
            else:
                threshold_str = "SLA threshold"
        else:
            raise ValueError("Either threshold or operation_type must be provided")
        
        # Assert that the measured time is within the threshold
        assert is_valid, (
            f"Performance threshold exceeded: {get_formatted_time(measured_time)} > {threshold_str} "
            f"for {operation_name or operation_type or 'operation'}"
        )
        
        return is_valid
    
    return validate_performance