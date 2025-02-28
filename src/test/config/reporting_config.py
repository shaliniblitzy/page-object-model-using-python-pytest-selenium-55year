"""
Configuration settings for test reporting functionality.

This module provides configuration classes and utilities for managing test reports,
screenshots, logs, and performance metrics. It defines paths, formats, and options
for various reporting aspects of the test automation framework.
"""

import os
from datetime import datetime

# Import base directory constant for report storage
from .constants import REPORTS_DIR as REPORT_BASE_DIR

# Directory paths for different types of reports
REPORT_DIR = os.path.join(REPORT_BASE_DIR, 'html')
SCREENSHOT_DIR = os.path.join(REPORT_BASE_DIR, 'screenshots')
LOG_DIR = os.path.join(REPORT_BASE_DIR, 'logs')
PERFORMANCE_DIR = os.path.join(REPORT_BASE_DIR, 'performance')


class ReportingConfig:
    """
    Configuration class for test reporting settings including paths, formats, and options.
    
    This class provides properties and methods to access and manage reporting configuration
    for test execution, including HTML reports, screenshots, logs, and performance metrics.
    """
    
    def __init__(self):
        """Initialize reporting configuration with default options."""
        # Set default HTML report options
        self._html_report_options = {
            'title': 'Storydoc Automation Test Report',
            'description': 'Test execution results for Storydoc application',
            'theme': 'light',
            'report_name': 'storydoc_test_report',
            'add_timestamp': True,
            'include_screenshots': True
        }
        
        # Set default screenshot options
        self._screenshot_options = {
            'format': 'png',
            'take_on_failure': True,
            'take_on_error': True,
            'add_timestamp': True,
            'width': 1920,
            'height': 1080
        }
        
        # Set default logging options
        self._logging_options = {
            'level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'file_logging': True,
            'console_logging': True,
            'add_timestamp': True
        }
        
        # Set default performance report options
        self._performance_options = {
            'enabled': True,
            'collect_page_load_times': True,
            'collect_element_interaction_times': True,
            'collect_resource_usage': True,
            'report_format': 'json',
            'add_timestamp': True
        }
        
        # Create necessary directories if they don't exist
        self.ensure_directories_exist()
    
    @property
    def html_report_options(self):
        """HTML report configuration options."""
        return self._html_report_options
    
    @property
    def screenshot_options(self):
        """Screenshot configuration options."""
        return self._screenshot_options
    
    @property
    def logging_options(self):
        """Logging configuration options."""
        return self._logging_options
    
    @property
    def performance_options(self):
        """Performance reporting configuration options."""
        return self._performance_options
    
    def get_html_report_path(self, prefix: str) -> str:
        """
        Get the HTML report file path with timestamp.
        
        Args:
            prefix: Prefix for the report filename
            
        Returns:
            Absolute path to the HTML report file with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.html"
        return os.path.join(REPORT_DIR, filename)
    
    def get_screenshot_path(self, test_name: str) -> str:
        """
        Get the screenshot file path with timestamp.
        
        Args:
            test_name: Name of the test for the screenshot filename
            
        Returns:
            Absolute path to the screenshot file with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        return os.path.join(SCREENSHOT_DIR, filename)
    
    def get_log_file_path(self, prefix: str) -> str:
        """
        Get the log file path with timestamp.
        
        Args:
            prefix: Prefix for the log filename
            
        Returns:
            Absolute path to the log file with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.log"
        return os.path.join(LOG_DIR, filename)
    
    def get_performance_report_path(self, test_type: str) -> str:
        """
        Get the performance report file path with timestamp.
        
        Args:
            test_type: Type of test for the performance report filename
            
        Returns:
            Absolute path to the performance report file with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_{test_type}_{timestamp}.json"
        return os.path.join(PERFORMANCE_DIR, filename)
    
    def ensure_directories_exist(self) -> bool:
        """
        Ensure all report directories exist, creating them if necessary.
        
        Returns:
            True if all directories exist or were created successfully
        """
        try:
            # Check and create HTML report directory if it doesn't exist
            os.makedirs(REPORT_DIR, exist_ok=True)
            
            # Check and create screenshot directory if it doesn't exist
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            
            # Check and create log directory if it doesn't exist
            os.makedirs(LOG_DIR, exist_ok=True)
            
            # Check and create performance directory if it doesn't exist
            os.makedirs(PERFORMANCE_DIR, exist_ok=True)
            
            # Return True if all directories exist
            return True
        except Exception as e:
            print(f"Error creating report directories: {e}")
            return False