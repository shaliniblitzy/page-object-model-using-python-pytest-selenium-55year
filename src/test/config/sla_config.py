"""
Configuration file defining Service Level Agreement (SLA) parameters for various operations
and test types in the Storydoc test automation framework.

This file provides:
1. SLA definitions for common operations like page navigation and element interactions
2. SLA definitions for test types like user registration and story creation
3. Helper functions to work with these SLA configurations
"""

# SLA configurations for various operations
OPERATION_SLAS = {
    "page_navigation": {
        "target_response_time": 5,  # seconds
        "timeout": 10,  # seconds
        "retry_strategy": {
            "retry_count": 1,
            "strategy": "simple"  # simple, exponential_backoff, etc.
        }
    },
    "element_interaction": {
        "target_response_time": 2,  # seconds
        "timeout": 5,  # seconds
        "retry_strategy": {
            "retry_count": 2,
            "strategy": "simple"
        }
    },
    "form_submission": {
        "target_response_time": 3,  # seconds
        "timeout": 10,  # seconds
        "retry_strategy": {
            "retry_count": 1,
            "strategy": "simple"
        }
    },
    "email_delivery": {
        "target_response_time": 30,  # seconds
        "timeout": 60,  # seconds
        "retry_strategy": {
            "retry_count": 12,  # Poll every 5 seconds for a minute
            "strategy": "polling",
            "polling_interval": 5  # seconds
        }
    },
    "test_execution": {
        "target_response_time": 300,  # 5 minutes
        "timeout": 600,  # 10 minutes
        "retry_strategy": {
            "retry_count": 0,
            "strategy": "none"
        }
    }
}

# SLA configurations for various test types
TEST_TYPE_SLAS = {
    "user_registration": {
        "maximum_duration": 30,  # seconds
        "success_rate": 98,  # percentage
        "reporting_latency": 1  # minute
    },
    "user_authentication": {
        "maximum_duration": 20,  # seconds
        "success_rate": 99,  # percentage
        "reporting_latency": 1  # minute
    },
    "story_creation": {
        "maximum_duration": 45,  # seconds
        "success_rate": 95,  # percentage
        "reporting_latency": 1  # minute
    },
    "story_sharing": {
        "maximum_duration": 60,  # seconds
        "success_rate": 95,  # percentage
        "reporting_latency": 1  # minute
    },
    "full_workflow": {
        "maximum_duration": 180,  # 3 minutes
        "success_rate": 90,  # percentage
        "reporting_latency": 5  # minutes
    }
}

# Flag to enable/disable SLA compliance reporting
SLA_REPORTING_ENABLED = True


def get_operation_sla(operation_type):
    """
    Returns the SLA configuration for a specific operation type.
    
    Args:
        operation_type (str): The type of operation (e.g., 'page_navigation', 'element_interaction')
        
    Returns:
        dict: SLA configuration for the specified operation type
        
    Raises:
        ValueError: If the operation_type is not found in the OPERATION_SLAS dictionary
    """
    if operation_type in OPERATION_SLAS:
        return OPERATION_SLAS[operation_type]
    else:
        raise ValueError(f"Unknown operation type: {operation_type}. "
                        f"Available types: {', '.join(OPERATION_SLAS.keys())}")


def get_test_type_sla(test_type):
    """
    Returns the SLA configuration for a specific test type.
    
    Args:
        test_type (str): The type of test (e.g., 'user_registration', 'story_creation')
        
    Returns:
        dict: SLA configuration for the specified test type
        
    Raises:
        ValueError: If the test_type is not found in the TEST_TYPE_SLAS dictionary
    """
    if test_type in TEST_TYPE_SLAS:
        return TEST_TYPE_SLAS[test_type]
    else:
        raise ValueError(f"Unknown test type: {test_type}. "
                        f"Available types: {', '.join(TEST_TYPE_SLAS.keys())}")


def is_within_operation_sla(operation_type, duration):
    """
    Checks if a measured duration is within the target SLA for a specific operation.
    
    Args:
        operation_type (str): The type of operation
        duration (float): The measured duration in seconds
        
    Returns:
        bool: True if the duration is within the target SLA, False otherwise
    """
    sla_config = get_operation_sla(operation_type)
    return duration <= sla_config["target_response_time"]


def is_within_test_type_sla(test_type, duration):
    """
    Checks if a test execution duration is within the maximum duration SLA for a specific test type.
    
    Args:
        test_type (str): The type of test
        duration (float): The measured duration in seconds
        
    Returns:
        bool: True if the duration is within the maximum duration SLA, False otherwise
    """
    sla_config = get_test_type_sla(test_type)
    return duration <= sla_config["maximum_duration"]


def get_retry_strategy(operation_type):
    """
    Returns the retry strategy for a specific operation type.
    
    Args:
        operation_type (str): The type of operation
        
    Returns:
        dict: Retry strategy configuration including retry count and strategy
    """
    sla_config = get_operation_sla(operation_type)
    return sla_config["retry_strategy"]


def get_timeout(operation_type):
    """
    Returns the timeout value for a specific operation type.
    
    Args:
        operation_type (str): The type of operation
        
    Returns:
        int: Timeout value in seconds
    """
    sla_config = get_operation_sla(operation_type)
    return sla_config["timeout"]