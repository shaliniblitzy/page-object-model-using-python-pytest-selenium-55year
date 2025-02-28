"""
Main initialization file for the Storydoc test automation framework, serving as the entry point
for the entire test package. This file provides a centralized point for importing key components,
initializing the framework, and exposing essential modules and utilities for testing the Storydoc
application's core workflows.
"""

import os  # built-in
import sys  # built-in

from .utilities.logger import initialize_logger, log_info, log_error
from .config.config import Config
from .config import initialize_config

# Framework version and name
__version__ = "1.0.0"
FRAMEWORK_NAME = "Storydoc Automation Framework"

# Root directory of the test package
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialization state flags
CONFIG_INITIALIZED = False
LOGGER_INITIALIZED = False


def initialize_framework(env_file=".env", log_to_console=True, log_to_file=True):
    """
    Initializes the test automation framework by setting up logging and configuration
    
    Args:
        env_file (str): Path to environment file for configuration
        log_to_console (bool): Whether to output logs to console
        log_to_file (bool): Whether to output logs to file
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    global CONFIG_INITIALIZED, LOGGER_INITIALIZED
    
    try:
        # Initialize logger with appropriate settings
        logger = initialize_logger(
            console_output=log_to_console,
            file_output=log_to_file
        )
        LOGGER_INITIALIZED = True
        
        # Initialize configuration with environment file
        CONFIG_INITIALIZED = initialize_config(env_file)
        
        # Log framework initialization information
        log_info(f"Initialized {FRAMEWORK_NAME} v{__version__}")
        log_info(f"Test root directory: {ROOT_DIR}")
        
        return CONFIG_INITIALIZED and LOGGER_INITIALIZED
    except Exception as e:
        # If logger is initialized, use it to log the error
        if LOGGER_INITIALIZED:
            log_error(f"Framework initialization error: {str(e)}", exception=e)
        else:
            # Fallback to printing the error if logger is not initialized
            print(f"Framework initialization error: {str(e)}")
        return False


def get_version():
    """
    Returns the current version of the test automation framework
    
    Returns:
        str: Version string
    """
    return __version__


# Export key components
__all__ = [
    "__version__",
    "FRAMEWORK_NAME",
    "ROOT_DIR",
    "initialize_framework",
    "get_version",
    "Config"
]