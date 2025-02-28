"""
Initialization file for the config package in the Storydoc test automation framework.

This module exports and provides centralized access to configuration constants,
functions, and utilities from various configuration modules.
"""

import logging  # built-in

# Import all configuration modules to expose their contents
from .constants import *
from .timeout_config import *
from .browser_config import *
from .environment_config import *
from .mailinator_config import *

# Import specific functions and classes from the main config module
from .config import initialize, get_config, set_config, load_test_data, Config

# Set the version of the config package
__version__ = "1.0.0"

# Configure logger for the config package
logger = logging.getLogger(__name__)

def initialize_config(env_file: str = None) -> bool:
    """
    Initializes the configuration for the test framework
    
    Args:
        env_file: Path to the environment file (.env)
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info("Initializing configuration for the test framework")
    result = initialize(env_file)
    logger.info("Configuration initialization completed")
    return result