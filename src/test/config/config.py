"""
Central configuration module for the Storydoc test automation framework.

This module provides a unified interface for accessing configuration settings from various sources.
It initializes and manages configuration parameters for browser settings, timeouts, URLs, email
verification, and other test execution parameters.
"""

import os
import json
import logging
import pathlib
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dotenv import load_dotenv

# Import constants and timeout configurations
from .constants import *
from .timeout_config import *

# Version of the configuration module
__version__ = "1.0.0"

# Global configuration dictionary
_config_data = {}

# Default environment file path
DEFAULT_ENV_FILE = ".env"

# Default environment (staging, production, etc.)
DEFAULT_ENVIRONMENT = "staging"

# Module logger
_logger = logging.getLogger(__name__)


def _log_info(message: str) -> None:
    """
    Internal logging function for information messages
    
    Args:
        message: Message to log
    """
    _logger.info(message)


def _log_error(message: str) -> None:
    """
    Internal logging function for error messages
    
    Args:
        message: Message to log
    """
    _logger.error(message)


def _log_debug(message: str) -> None:
    """
    Internal logging function for debug messages
    
    Args:
        message: Message to log
    """
    _logger.debug(message)


def _load_from_env_file(env_file: str) -> bool:
    """
    Load configuration from .env file
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        load_dotenv(env_file)
        _log_info(f"Loaded configuration from {env_file}")
        return True
    except Exception as e:
        _log_error(f"Failed to load configuration from {env_file}: {str(e)}")
        return False


def _load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables
    
    Returns:
        Configuration dictionary with all settings
    """
    config = {}
    
    # Base URL and environment
    config["base_url"] = os.getenv("TEST_BASE_URL", URLS.get("BASE", "https://editor-staging.storydoc.com"))
    config["environment"] = os.getenv("TEST_ENVIRONMENT", DEFAULT_ENVIRONMENT)
    
    # Browser settings
    config["browser_type"] = os.getenv("TEST_BROWSER_TYPE", BROWSERS.get("CHROME", "chrome"))
    config["headless_mode"] = os.getenv("TEST_HEADLESS_MODE", "false").lower() == "true"
    
    # Timeout settings
    config["default_timeout"] = int(os.getenv("TEST_DEFAULT_TIMEOUT", str(DEFAULT_TIMEOUT)))
    config["element_timeout"] = int(os.getenv("TEST_ELEMENT_TIMEOUT", str(ELEMENT_TIMEOUT)))
    config["page_load_timeout"] = int(os.getenv("TEST_PAGE_LOAD_TIMEOUT", str(PAGE_LOAD_TIMEOUT)))
    config["email_timeout"] = int(os.getenv("TEST_EMAIL_TIMEOUT", str(EMAIL_DELIVERY_TIMEOUT)))
    config["email_polling_interval"] = int(os.getenv("TEST_EMAIL_POLLING_INTERVAL", str(EMAIL_POLLING_INTERVAL)))
    
    # Email verification settings
    config["mailinator_domain"] = os.getenv("TEST_MAILINATOR_DOMAIN", "mailinator.com")
    config["mailinator_api_key"] = os.getenv("TEST_MAILINATOR_API_KEY", "")
    config["mailinator_api_url"] = os.getenv("TEST_MAILINATOR_API_URL", MAILINATOR.get("BASE_URL", "https://api.mailinator.com/api/v2"))
    
    # Test execution settings
    config["retry_attempts"] = int(os.getenv("TEST_RETRY_ATTEMPTS", "3"))
    config["retry_delay"] = int(os.getenv("TEST_RETRY_DELAY", "2"))
    
    # File paths
    config["data_dir"] = os.getenv("TEST_DATA_DIR", str(Path(__file__).parent.parent / "data"))
    config["screenshot_dir"] = os.getenv("TEST_SCREENSHOT_DIR", str(Path(__file__).parent.parent / "reports" / "screenshots"))
    config["report_dir"] = os.getenv("TEST_REPORT_DIR", str(Path(__file__).parent.parent / "reports"))
    config["log_dir"] = os.getenv("TEST_LOG_DIR", str(Path(__file__).parent.parent / "reports" / "logs"))
    
    return config


def create_directories() -> bool:
    """
    Create necessary directories for test artifacts
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get directory paths from configuration
        screenshot_dir = Path(get_config("screenshot_dir"))
        report_dir = Path(get_config("report_dir"))
        log_dir = Path(get_config("log_dir"))
        data_dir = Path(get_config("data_dir"))
        
        # Create directories if they don't exist
        for directory in [screenshot_dir, report_dir, log_dir, data_dir]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                _log_debug(f"Created directory: {directory}")
        
        _log_info("Created necessary directories for test artifacts")
        return True
    except Exception as e:
        _log_error(f"Failed to create directories: {str(e)}")
        return False


def initialize(env_file: Optional[str] = None, environment: Optional[str] = None) -> bool:
    """
    Initializes the configuration system for the test framework
    
    Args:
        env_file: Path to the .env file (default: DEFAULT_ENV_FILE)
        environment: Environment to use (default: DEFAULT_ENVIRONMENT)
        
    Returns:
        True if initialization was successful, False otherwise
    """
    global _config_data
    
    _log_info("Initializing configuration")
    
    # Set defaults if not provided
    if env_file is None:
        env_file = DEFAULT_ENV_FILE
    
    if environment is None:
        environment = DEFAULT_ENVIRONMENT
    
    # Load from .env file
    _load_from_env_file(env_file)
    
    # Load configuration from environment variables
    _config_data = _load_config_from_env()
    
    # Set environment explicitly in configuration
    _config_data["environment"] = environment
    
    # Create necessary directories
    create_directories()
    
    _log_info("Configuration initialized successfully")
    return True


def get_config(key: str, default: Any = None) -> Any:
    """
    Gets a configuration value by key with an optional default value
    
    Args:
        key: Configuration key to retrieve
        default: Default value to return if key is not found
        
    Returns:
        Configuration value or default if not found
    """
    global _config_data
    
    # Initialize if not already done
    if not _config_data:
        initialize()
    
    return _config_data.get(key, default)


def set_config(key: str, value: Any) -> None:
    """
    Sets a configuration value by key
    
    Args:
        key: Configuration key to set
        value: Value to set
    """
    global _config_data
    
    # Initialize if not already done
    if not _config_data:
        initialize()
    
    _config_data[key] = value
    _log_debug(f"Updated configuration: {key} = {value}")


def load_test_data(file_name: str) -> Dict[str, Any]:
    """
    Loads test data from a JSON file
    
    Args:
        file_name: Name of the JSON file to load
        
    Returns:
        Test data as a dictionary
    """
    data_dir = get_config("data_dir")
    file_path = Path(data_dir) / file_name
    
    if not file_path.suffix:
        file_path = file_path.with_suffix(".json")
    
    try:
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
            _log_debug(f"Loaded test data from {file_path}")
            return data
        else:
            _log_error(f"Test data file not found: {file_path}")
            return {}
    except Exception as e:
        _log_error(f"Error loading test data from {file_path}: {str(e)}")
        return {}


def get_base_url() -> str:
    """
    Gets the base URL for the application under test
    
    Returns:
        Base URL for the application
    """
    return get_config("base_url", "https://editor-staging.storydoc.com")


def get_browser_config() -> Dict[str, Any]:
    """
    Gets browser configuration including type and options
    
    Returns:
        Browser configuration dictionary
    """
    return {
        "browser_type": get_config("browser_type", "chrome"),
        "headless": get_config("headless_mode", False)
    }


def get_timeout_config() -> Dict[str, int]:
    """
    Gets all timeout configuration as a dictionary
    
    Returns:
        Timeout configuration dictionary
    """
    return {
        "default_timeout": get_config("default_timeout", DEFAULT_TIMEOUT),
        "element_timeout": get_config("element_timeout", ELEMENT_TIMEOUT),
        "page_load_timeout": get_config("page_load_timeout", PAGE_LOAD_TIMEOUT),
        "email_timeout": get_config("email_timeout", EMAIL_DELIVERY_TIMEOUT),
        "email_polling_interval": get_config("email_polling_interval", EMAIL_POLLING_INTERVAL)
    }


def get_mailinator_config() -> Dict[str, str]:
    """
    Gets Mailinator configuration for email testing
    
    Returns:
        Mailinator configuration dictionary
    """
    return {
        "domain": get_config("mailinator_domain", "mailinator.com"),
        "api_key": get_config("mailinator_api_key", ""),
        "api_url": get_config("mailinator_api_url", "https://api.mailinator.com/api/v2")
    }


def reload_config() -> bool:
    """
    Reloads the configuration from environment variables and .env file
    
    Returns:
        True if reload was successful, False otherwise
    """
    global _config_data
    
    _log_info("Reloading configuration")
    
    # Get current env_file and environment
    env_file = get_config("env_file", DEFAULT_ENV_FILE)
    environment = get_config("environment", DEFAULT_ENVIRONMENT)
    
    # Store previous configuration in case of failure
    previous_config = _config_data.copy()
    
    try:
        # Call initialize to reload configuration
        result = initialize(env_file, environment)
        
        if result:
            _log_info("Configuration reloaded successfully")
            return True
        else:
            _log_error("Failed to reload configuration, restoring previous configuration")
            _config_data = previous_config
            return False
    except Exception as e:
        _log_error(f"Error reloading configuration: {str(e)}")
        _config_data = previous_config
        return False


class Config:
    """
    Class providing access to all configuration settings with property getters
    """
    
    def __init__(self):
        """
        Initializes the Config class and ensures configuration is loaded
        """
        global _config_data
        
        # Initialize configuration if not already done
        if not _config_data:
            initialize()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a configuration value by key with an optional default value
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if not found
        """
        return get_config(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Sets a configuration value by key
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        set_config(key, value)
    
    def load_data(self, file_name: str) -> Dict[str, Any]:
        """
        Loads test data from a JSON file
        
        Args:
            file_name: Name of the JSON file to load
            
        Returns:
            Test data as a dictionary
        """
        return load_test_data(file_name)
    
    def reload(self) -> bool:
        """
        Reloads the configuration
        
        Returns:
            True if reload was successful
        """
        return reload_config()
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Returns the entire configuration as a dictionary
        
        Returns:
            Complete configuration dictionary
        """
        global _config_data
        return _config_data.copy()
    
    @property
    def base_url(self) -> str:
        """Base URL of the application under test"""
        return get_base_url()
    
    @property
    def browser(self) -> Dict[str, Any]:
        """Browser configuration"""
        return get_browser_config()
    
    @property
    def timeouts(self) -> Dict[str, int]:
        """Timeout configuration"""
        return get_timeout_config()
    
    @property
    def mailinator(self) -> Dict[str, str]:
        """Mailinator configuration"""
        return get_mailinator_config()
    
    @property
    def environment(self) -> str:
        """Current environment"""
        return get_config("environment", DEFAULT_ENVIRONMENT)
    
    @property
    def headless_mode(self) -> bool:
        """Whether to run browsers in headless mode"""
        return get_config("headless_mode", False)
    
    @property
    def retry_attempts(self) -> int:
        """Number of retry attempts for flaky operations"""
        return get_config("retry_attempts", 3)
    
    @property
    def screenshot_dir(self) -> str:
        """Directory for storing screenshots"""
        return get_config("screenshot_dir")
    
    @property
    def report_dir(self) -> str:
        """Directory for storing test reports"""
        return get_config("report_dir")