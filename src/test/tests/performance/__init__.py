"""
Initialization module for the performance testing package that defines common imports, constants,
and utility functions for performance tests. This module makes performance testing components
and decorators available to all test modules in the package.
"""

import pytest  # pytest 7.3+

# Import performance monitoring utilities
from ...utilities.performance_monitor import (
    PerformanceMonitor,
    PerformanceContext,
    monitor_performance
)

# Import timing utilities
from ...utilities.timing_helper import Timer, TimingContext

# Import SLA configurations
from ...config.sla_config import (
    OPERATION_SLAS,
    TEST_TYPE_SLAS,
    is_within_operation_sla,
    is_within_test_type_sla
)

# Import performance fixtures
from ...fixtures.performance_fixtures import (
    performance_monitor,
    page_load_timer,
    element_interaction_timer
)

# Define performance thresholds
PAGE_LOAD_THRESHOLD = 5.0
ELEMENT_INTERACTION_THRESHOLD = 2.0
FORM_SUBMISSION_THRESHOLD = 3.0
EMAIL_DELIVERY_THRESHOLD = 30.0
TEST_EXECUTION_THRESHOLDS = {
    "user_registration": 30.0,
    "user_authentication": 20.0,
    "story_creation": 45.0,
    "story_sharing": 60.0,
    "full_workflow": 180.0
}


def measure_with_timer(callable, operation_type, metadata=None):
    """
    Utility function that measures execution time of a callable and checks SLA compliance
    
    Args:
        callable: Function or operation to measure
        operation_type: Type of operation for SLA compliance checking
        metadata: Additional metadata about the operation
        
    Returns:
        Tuple containing (result, elapsed_time)
    """
    if metadata is None:
        metadata = {}
    
    # Initialize a Timer instance
    timer = Timer(name=getattr(callable, "__name__", "anonymous_function"), 
                  category=operation_type)
    
    # Start the timer
    timer.start()
    
    # Execute the operation and store the result
    result = callable()
    
    # Stop timer and get the elapsed time
    elapsed_time = timer.stop(store_result=False)
    
    # Check if the operation meets SLA requirements
    is_compliant = is_within_operation_sla(operation_type, elapsed_time)
    metadata["sla_compliant"] = is_compliant
    metadata["operation_type"] = operation_type
    
    # Return a tuple of (operation_result, elapsed_time)
    return result, elapsed_time