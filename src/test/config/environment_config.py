"""
Configuration module for managing environment-specific settings such as URLs, credentials, 
and feature flags for the Storydoc test automation framework.
"""

import os
from enum import Enum
from dotenv import load_dotenv  # python-dotenv 1.0+

class Environment(Enum):
    """Enumeration of supported test environments"""
    STAGING = "staging"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    CI = "ci"

# Default environment
DEFAULT_ENV = Environment.STAGING

# Current environment (will be set during runtime)
current_environment = None

# Environment-specific URLs
environment_urls = {
    Environment.STAGING: 'https://editor-staging.storydoc.com',
    Environment.DEVELOPMENT: 'https://editor-dev.storydoc.com',
    Environment.PRODUCTION: 'https://editor.storydoc.com',
    Environment.CI: 'https://editor-staging.storydoc.com'
}

# Environment-specific API URLs
environment_api_urls = {
    Environment.STAGING: 'https://api-staging.storydoc.com',
    Environment.DEVELOPMENT: 'https://api-dev.storydoc.com',
    Environment.PRODUCTION: 'https://api.storydoc.com',
    Environment.CI: 'https://api-staging.storydoc.com'
}

# Environment-specific timeouts (in seconds)
environment_timeouts = {
    Environment.STAGING: 10,
    Environment.DEVELOPMENT: 20,
    Environment.PRODUCTION: 10,
    Environment.CI: 30
}

# Environment-specific headless mode settings
environment_headless = {
    Environment.STAGING: False,
    Environment.DEVELOPMENT: False,
    Environment.PRODUCTION: False,
    Environment.CI: True
}

# Environment-specific Mailinator domains
environment_mailinator_domains = {
    Environment.STAGING: 'mailinator.com',
    Environment.DEVELOPMENT: 'mailinator.com',
    Environment.PRODUCTION: 'mailinator.com',
    Environment.CI: 'mailinator.com'
}

def get_environment():
    """
    Returns the current environment setting from environment variables or default
    
    Returns:
        Environment: Current environment value
    """
    global current_environment
    
    # Check if current_environment is already set
    if current_environment is not None:
        return current_environment
    
    # Get environment name from environment variable 'TEST_ENV'
    env_name = os.environ.get('TEST_ENV', '').lower()
    
    # If environment variable is not set, return DEFAULT_ENV
    if not env_name:
        return DEFAULT_ENV
    
    # Convert string environment name to Environment enum
    try:
        # Try to match by enum value (string)
        for env in Environment:
            if env.value == env_name:
                current_environment = env
                return env
        
        # If no match by value, try to match by enum name
        current_environment = Environment[env_name.upper()]
        return current_environment
    except (KeyError, ValueError):
        # If invalid environment name, use default
        return DEFAULT_ENV

def set_environment(env):
    """
    Sets the current environment for the test run
    
    Args:
        env (Environment): Environment to set
        
    Returns:
        None
    """
    global current_environment
    current_environment = env

def load_environment_config(env_file_path):
    """
    Loads environment-specific configuration from .env file and environment variables
    
    Args:
        env_file_path (str): Path to .env file
    
    Returns:
        dict: Dictionary of environment configuration values
    """
    # Load the .env file using python-dotenv if env_file_path is provided
    if env_file_path:
        load_dotenv(env_file_path)
    
    # Get the current environment using get_environment()
    env = get_environment()
    
    # Build environment-specific configuration dictionary
    config = {
        'base_url': get_base_url(),
        'api_url': get_api_url(),
        'default_timeout': get_timeout(),
        'headless_mode': is_headless(),
        'mailinator_domain': get_mailinator_domain(),
        'is_ci': is_ci_environment()
    }
    
    return config

def get_base_url():
    """
    Returns the base URL for the current environment
    
    Returns:
        str: Base URL for the current environment
    """
    env = get_environment()
    
    # Return environment variable 'TEST_BASE_URL' if defined
    env_url = os.environ.get('TEST_BASE_URL')
    if env_url:
        return env_url
    
    # Otherwise, return the appropriate base URL for the environment
    return environment_urls.get(env)

def get_api_url():
    """
    Returns the API URL for the current environment
    
    Returns:
        str: API URL for the current environment
    """
    env = get_environment()
    
    # Return environment variable 'TEST_API_URL' if defined
    env_url = os.environ.get('TEST_API_URL')
    if env_url:
        return env_url
    
    # Otherwise, return the appropriate API URL for the environment
    return environment_api_urls.get(env)

def get_timeout():
    """
    Returns the default timeout for the current environment
    
    Returns:
        int: Default timeout in seconds for the current environment
    """
    env = get_environment()
    
    # Return environment variable 'TEST_TIMEOUT' as int if defined
    env_timeout = os.environ.get('TEST_TIMEOUT')
    if env_timeout:
        try:
            return int(env_timeout)
        except ValueError:
            pass
    
    # Otherwise, return the appropriate timeout for the environment
    return environment_timeouts.get(env)

def get_mailinator_domain():
    """
    Returns the Mailinator domain to use for the current environment
    
    Returns:
        str: Mailinator domain for the current environment
    """
    env = get_environment()
    
    # Return environment variable 'TEST_MAILINATOR_DOMAIN' if defined
    env_domain = os.environ.get('TEST_MAILINATOR_DOMAIN')
    if env_domain:
        return env_domain
    
    # Otherwise, return the appropriate Mailinator domain for the environment
    return environment_mailinator_domains.get(env)

def is_headless():
    """
    Determines if tests should run in headless mode based on environment settings
    
    Returns:
        bool: True if headless mode should be used, False otherwise
    """
    # Get headless mode setting from environment variable 'TEST_HEADLESS_MODE'
    env_headless = os.environ.get('TEST_HEADLESS_MODE')
    if env_headless is not None:
        return env_headless.lower() in ('true', '1', 'yes')
    
    # If not specified, use environment-specific default from environment_headless
    env = get_environment()
    return environment_headless.get(env, False)

def is_ci_environment():
    """
    Checks if tests are running in a CI environment
    
    Returns:
        bool: True if in CI environment, False otherwise
    """
    # Get current environment using get_environment()
    env = get_environment()
    
    # Return True if current environment is Environment.CI
    if env == Environment.CI:
        return True
    
    # Also check common CI environment variables like 'CI', 'JENKINS_URL', 'GITHUB_ACTIONS'
    ci_env_vars = ['CI', 'JENKINS_URL', 'GITHUB_ACTIONS', 'GITLAB_CI', 'TRAVIS']
    for var in ci_env_vars:
        if os.environ.get(var):
            return True
    
    return False