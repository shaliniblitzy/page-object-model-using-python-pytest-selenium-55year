"""
Configuration manager utility for the Storydoc test automation framework.

This module provides a centralized interface for accessing configuration settings
from various sources, including environment variables, .env files, and default values.
Implements a singleton pattern to ensure consistent configuration across the test framework.
"""

import os
import json
import pathlib
import logging
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv  # python-dotenv 1.0+

# Import configuration constants and environment configuration
from ..config.constants import (
    TIMEOUTS, URLS, BROWSERS, MAILINATOR,
    DATA_DIR, REPORTS_DIR, SCREENSHOTS_DIR
)
from ..config.environment_config import Environment, get_environment, load_environment_config

# Module version
__version__ = "1.0.0"

# Singleton instance
_config_instance = None

# Default configuration values
DEFAULT_ENV_FILE = ".env"
DEFAULT_ENVIRONMENT = "staging"

# Setup logger
logger = logging.getLogger(__name__)


def _ensure_directory_exists(directory_path: pathlib.Path) -> bool:
    """
    Ensures that a directory exists, creating it if necessary
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        bool: True if directory exists or was created, False on error
    """
    try:
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def get_instance() -> 'ConfigManager':
    """
    Gets the singleton instance of the ConfigManager class
    
    Returns:
        ConfigManager: The singleton ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def get_config(key: str, default: Any = None) -> Any:
    """
    Gets a configuration value by key with an optional default value
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found
        
    Returns:
        Any: Configuration value or default if not found
    """
    return get_instance().get(key, default)


def set_config(key: str, value: Any) -> None:
    """
    Sets a configuration value by key
    
    Args:
        key: Configuration key to set
        value: Value to set
    """
    get_instance().set(key, value)


def initialize(env_file: str = DEFAULT_ENV_FILE, environment: str = DEFAULT_ENVIRONMENT) -> bool:
    """
    Initializes the configuration system with the specified environment file and environment
    
    Args:
        env_file: Path to the environment file
        environment: Environment to use (staging, development, production)
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    return get_instance().initialize(env_file, environment)


def load_test_data(file_name: str) -> Dict[str, Any]:
    """
    Loads test data from a JSON file in the data directory
    
    Args:
        file_name: Name of the JSON file (with or without .json extension)
        
    Returns:
        dict: Test data as a dictionary
    """
    return get_instance().load_test_data(file_name)


def create_directories() -> bool:
    """
    Creates necessary directories for test execution
    
    Returns:
        bool: True if all directories were created successfully, False otherwise
    """
    return get_instance().create_directories()


def reset() -> None:
    """
    Resets the configuration manager to its initial state for testing
    """
    global _config_instance
    _config_instance = None
    logger.info("Configuration manager has been reset")


class ConfigManager:
    """
    Configuration manager class that handles loading, storing, and retrieving configuration values
    """
    
    def __init__(self):
        """
        Initializes a new ConfigManager instance
        """
        self._config: Dict[str, Any] = {}
        self._initialized = False
        logger.info("Created new ConfigManager instance")
    
    def initialize(self, env_file: str = DEFAULT_ENV_FILE, environment: str = DEFAULT_ENVIRONMENT) -> bool:
        """
        Initializes the configuration with the specified environment file and environment
        
        Args:
            env_file: Path to the environment file
            environment: Environment to use (staging, development, production)
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        logger.info(f"Initializing configuration with env_file={env_file}, environment={environment}")
        
        try:
            # Load environment variables from .env file
            if env_file and pathlib.Path(env_file).exists():
                load_dotenv(env_file)
                logger.info(f"Loaded environment variables from {env_file}")
            
            # Load environment-specific configuration
            env_config = load_environment_config(env_file)
            
            # Update configuration with environment-specific settings
            self._config.update(env_config)
            
            # Set the environment in the configuration
            self._config['environment'] = environment
            
            # Create necessary directories
            self.create_directories()
            
            # Mark as initialized
            self._initialized = True
            logger.info("Configuration initialization completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a configuration value by key with an optional default value
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key is not found
            
        Returns:
            Any: Configuration value or default if not found
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Check if key exists in configuration
        if key in self._config:
            return self._config[key]
        
        # Check if key exists in environment variables
        env_value = os.environ.get(f"TEST_{key.upper()}")
        if env_value is not None:
            return env_value
        
        # Return default value if key not found
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Sets a configuration value by key
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Update configuration with new value
        self._config[key] = value
        logger.info(f"Set configuration value {key}={value}")
    
    def load_test_data(self, file_name: str) -> Dict[str, Any]:
        """
        Loads test data from a JSON file in the data directory
        
        Args:
            file_name: Name of the JSON file (with or without .json extension)
            
        Returns:
            dict: Test data as a dictionary
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Add .json extension if not present
        if not file_name.endswith('.json'):
            file_name += '.json'
        
        # Construct path to data file
        data_file_path = DATA_DIR / file_name
        
        try:
            # Check if file exists
            if data_file_path.exists():
                # Load and parse JSON data
                with open(data_file_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded test data from {data_file_path}")
                return data
            else:
                logger.error(f"Test data file not found: {data_file_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load test data from {data_file_path}: {str(e)}")
            return {}
    
    def create_directories(self) -> bool:
        """
        Creates necessary directories for test execution
        
        Returns:
            bool: True if all directories were created successfully, False otherwise
        """
        # Create reports directory
        reports_success = _ensure_directory_exists(REPORTS_DIR)
        
        # Create screenshots directory
        screenshots_success = _ensure_directory_exists(SCREENSHOTS_DIR)
        
        # Add any other required directories here
        
        return reports_success and screenshots_success
    
    def get_all(self) -> Dict[str, Any]:
        """
        Gets the entire configuration as a dictionary
        
        Returns:
            dict: Complete configuration dictionary
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Return a copy of the configuration to prevent modification
        return dict(self._config)
    
    def get_browser_config(self) -> Dict[str, Any]:
        """
        Gets browser configuration including type and options
        
        Returns:
            dict: Browser configuration dictionary
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Get browser type with default of 'chrome'
        browser_type = self.get('browser_type', BROWSERS.get('CHROME'))
        
        # Get headless mode setting
        headless = self.get('headless_mode', False)
        
        # Return browser configuration
        return {
            'browser_type': browser_type,
            'headless': headless
        }
    
    def get_timeout_config(self) -> Dict[str, int]:
        """
        Gets all timeout configuration as a dictionary
        
        Returns:
            dict: Timeout configuration dictionary
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Start with default timeouts
        timeouts = dict(TIMEOUTS)
        
        # Override with any custom timeout settings from configuration
        for key in timeouts:
            custom_value = self.get(f"timeout_{key.lower()}")
            if custom_value is not None:
                try:
                    timeouts[key] = int(custom_value)
                except (ValueError, TypeError):
                    # Keep default if conversion fails
                    pass
        
        return timeouts
    
    def get_mailinator_config(self) -> Dict[str, Any]:
        """
        Gets Mailinator configuration for email testing
        
        Returns:
            dict: Mailinator configuration dictionary
        """
        # Ensure configuration is initialized
        if not self._initialized:
            self.initialize()
        
        # Get mailinator domain with default from configuration
        domain = self.get('mailinator_domain', 'mailinator.com')
        
        # Get mailinator API key if available
        api_key = self.get('mailinator_api_key')
        
        # Get Mailinator API base URL
        base_url = MAILINATOR.get('BASE_URL')
        
        # Return mailinator configuration
        return {
            'domain': domain,
            'api_key': api_key,
            'base_url': base_url
        }
    
    def reset(self) -> None:
        """
        Resets the configuration to uninitialized state for testing
        """
        self._config = {}
        self._initialized = False
        logger.info("Configuration has been reset")