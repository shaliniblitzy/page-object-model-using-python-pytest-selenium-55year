"""
Timeout configuration module for Storydoc test automation framework.

This module defines standardized timeout values for various operations including
page loading, element interactions, form submissions, email verification, and test
execution timeouts. These timeouts are critical for ensuring test reliability and
compliance with defined SLAs.

All timeout values are in seconds unless otherwise specified.
"""

import os  # standard library

# Default timeout values
DEFAULT_TIMEOUT = 10  # Default timeout in seconds for most operations
PAGE_LOAD_TIMEOUT = 10  # Maximum time to wait for page to load in seconds
ELEMENT_TIMEOUT = 5  # Maximum time to wait for an element to be visible
ELEMENT_CLICKABLE_TIMEOUT = 5  # Maximum time to wait for an element to be clickable
ELEMENT_PRESENCE_TIMEOUT = 5  # Maximum time to wait for an element to be present in DOM
ELEMENT_DISAPPEAR_TIMEOUT = 5  # Maximum time to wait for an element to disappear
FORM_SUBMISSION_TIMEOUT = 10  # Maximum time to wait for form submission to complete

# SLA-defined workflow timeouts
USER_REGISTRATION_TIMEOUT = 30  # Maximum time for user registration process as per SLA
USER_AUTHENTICATION_TIMEOUT = 20  # Maximum time for user authentication process as per SLA
STORY_CREATION_TIMEOUT = 45  # Maximum time for story creation process as per SLA
STORY_SHARING_TIMEOUT = 60  # Maximum time for story sharing process as per SLA
WORKFLOW_TIMEOUT = 180  # Maximum time for full workflow (3 minutes) as per SLA

# Email verification timeouts
EMAIL_DELIVERY_TIMEOUT = 60  # Maximum time to wait for email delivery
EMAIL_POLLING_INTERVAL = 5  # Time between checks for email delivery

# Retry settings
RETRY_TIMEOUT = 3  # Default timeout between retries for flaky operations
MAX_RETRY_COUNT = 3  # Maximum number of retry attempts for flaky operations

# Wait settings
EXPLICIT_WAIT_TIMEOUT = 10  # Default timeout for explicit waits
POLLING_INTERVAL = 0.5  # Default polling interval for waits in seconds


def get_timeout(timeout_name: str, default_value: int) -> int:
    """
    Gets a timeout value, with optional environment variable override.
    
    Args:
        timeout_name: Name of the timeout setting
        default_value: Default value to use if no override exists
        
    Returns:
        The timeout value from environment variable or default
    """
    # Convert timeout_name to uppercase for environment variable naming convention
    timeout_name_upper = timeout_name.upper()
    
    # Create environment variable name like 'TEST_TIMEOUT_<TIMEOUT_NAME>'
    env_var_name = f"TEST_TIMEOUT_{timeout_name_upper}"
    
    # Try to get the value from environment variable
    env_value = os.environ.get(env_var_name)
    
    # If environment variable exists, convert to int and return
    if env_value is not None:
        try:
            return int(env_value)
        except ValueError:
            # If conversion fails, return the default value
            return default_value
    
    # Otherwise return the provided default_value
    return default_value


def get_element_timeout(element_operation: str) -> int:
    """
    Gets the appropriate element timeout based on operation type.
    
    Args:
        element_operation: Type of element operation ('visible', 'clickable', 'present', 'disappear')
        
    Returns:
        Timeout value for the specified element operation
    """
    if element_operation == 'visible':
        return ELEMENT_TIMEOUT
    elif element_operation == 'clickable':
        return ELEMENT_CLICKABLE_TIMEOUT
    elif element_operation == 'present':
        return ELEMENT_PRESENCE_TIMEOUT
    elif element_operation == 'disappear':
        return ELEMENT_DISAPPEAR_TIMEOUT
    else:
        return DEFAULT_TIMEOUT


def get_page_timeout(page_operation: str) -> int:
    """
    Gets the appropriate page timeout based on operation type.
    
    Args:
        page_operation: Type of page operation ('load', 'form_submission')
        
    Returns:
        Timeout value for the specified page operation
    """
    if page_operation == 'load':
        return PAGE_LOAD_TIMEOUT
    elif page_operation == 'form_submission':
        return FORM_SUBMISSION_TIMEOUT
    else:
        return DEFAULT_TIMEOUT


def get_email_timeout(email_operation: str) -> int:
    """
    Gets the appropriate email timeout based on operation type.
    
    Args:
        email_operation: Type of email operation ('delivery', 'polling')
        
    Returns:
        Timeout value for the specified email operation
    """
    if email_operation == 'delivery':
        return EMAIL_DELIVERY_TIMEOUT
    elif email_operation == 'polling':
        return EMAIL_POLLING_INTERVAL
    else:
        return DEFAULT_TIMEOUT


def get_workflow_timeout(workflow_name: str) -> int:
    """
    Gets the timeout for a specific workflow operation.
    
    Args:
        workflow_name: Name of the workflow ('registration', 'authentication', 
                      'story_creation', 'story_sharing', 'complete')
        
    Returns:
        Timeout value for the specified workflow
    """
    if workflow_name == 'registration':
        return USER_REGISTRATION_TIMEOUT
    elif workflow_name == 'authentication':
        return USER_AUTHENTICATION_TIMEOUT
    elif workflow_name == 'story_creation':
        return STORY_CREATION_TIMEOUT
    elif workflow_name == 'story_sharing':
        return STORY_SHARING_TIMEOUT
    elif workflow_name == 'complete':
        return WORKFLOW_TIMEOUT
    else:
        return DEFAULT_TIMEOUT