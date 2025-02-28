"""
Utility for managing screenshots during test execution.

This module provides methods to capture, name, and save screenshots for test failures and debugging purposes.
It handles directory creation, standardized naming conventions, and cleanup of old screenshots.
"""

import os
import datetime
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# Internal imports
from ..utilities.config_manager import get_config
from ..utilities.timing_helper import format_timestamp
from ..utilities.logger import get_logger


class ScreenshotManager:
    """Manages the capture, naming, and storage of screenshots during test execution"""

    def __init__(self, screenshot_dir: str = None, create_dirs: bool = True):
        """
        Initialize the ScreenshotManager with configuration settings
        
        Args:
            screenshot_dir: Directory for storing screenshots, defaults to configuration value
            create_dirs: Whether to create directories if they don't exist
        """
        # Initialize logger
        self.logger = get_logger()
        
        # Get screenshot directory from parameters or configuration
        self.screenshot_dir = screenshot_dir or get_config("screenshot_dir") 
        self.create_dirs = create_dirs
        self.config_manager = None

        # Create the screenshot directory if it doesn't exist and create_dirs is True
        if self.create_dirs:
            self.create_directory(self.screenshot_dir)

    def capture_screenshot(self, driver: WebDriver, filename: str = None, subfolder: str = None) -> Optional[str]:
        """
        Capture a screenshot using the provided WebDriver instance
        
        Args:
            driver: WebDriver instance to use for capturing screenshot
            filename: Optional filename for the screenshot, will generate one if not provided
            subfolder: Optional subfolder within screenshot_dir to save the screenshot
            
        Returns:
            Path to the saved screenshot file or None if failed
        """
        # Validate driver
        if driver is None:
            self.logger.error("Cannot capture screenshot: WebDriver instance is None")
            return None
        
        # Generate filename if not provided
        if not filename:
            filename = self.generate_screenshot_filename("screenshot")
        
        # Get the full file path
        file_path = self.get_screenshot_path(filename, subfolder)
        
        try:
            # Capture screenshot
            driver.save_screenshot(file_path)
            self.logger.info(f"Screenshot captured: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {str(e)}")
            return None

    def capture_failure_screenshot(self, driver: WebDriver, test_name: str, 
                                error_message: str = None) -> Optional[str]:
        """
        Capture a screenshot for a test failure with standardized naming
        
        Args:
            driver: WebDriver instance to use for capturing screenshot
            test_name: Name of the test that failed
            error_message: Optional error message for context
            
        Returns:
            Path to the saved screenshot file or None if failed
        """
        # Generate a failure-specific filename
        timestamp = format_timestamp("%Y%m%d_%H%M%S") 
        
        # Sanitize test_name to remove invalid characters
        test_name = "".join(c if c.isalnum() else "_" for c in test_name)
        
        filename = f"failure_{test_name}_{timestamp}.png"
        
        # Capture the screenshot in a 'failures' subfolder
        screenshot_path = self.capture_screenshot(driver, filename, "failures")
        
        if screenshot_path:
            # Log the failure with error message if provided
            error_context = f" - Error: {error_message}" if error_message else ""
            self.logger.error(f"Failure screenshot captured for '{test_name}'{error_context}: {screenshot_path}")
        
        return screenshot_path

    def capture_element_screenshot(self, driver: WebDriver, element: WebElement, 
                                filename: str = None) -> Optional[str]:
        """
        Capture a screenshot highlighting a specific element (if supported by the driver)
        
        Args:
            driver: WebDriver instance to use for capturing screenshot
            element: WebElement to highlight in the screenshot
            filename: Optional filename for the screenshot
            
        Returns:
            Path to the saved screenshot file or None if failed
        """
        # Validate driver and element
        if driver is None or element is None:
            self.logger.error("Cannot capture element screenshot: WebDriver or WebElement is None")
            return None
        
        try:
            # Generate filename if not provided
            if not filename:
                filename = self.generate_screenshot_filename("element")
            
            # Store original element style to restore later
            original_style = element.get_attribute("style")
            
            # Highlight the element with a red border
            driver.execute_script(
                "arguments[0].style.border='3px solid red';", element
            )
            
            # Take screenshot with the highlighted element
            file_path = self.get_screenshot_path(filename, "elements")
            driver.save_screenshot(file_path)
            
            # Restore original style
            driver.execute_script(
                f"arguments[0].style.border='{original_style}';", element
            )
            
            self.logger.info(f"Element screenshot captured: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to capture element screenshot: {str(e)}")
            return None

    def generate_screenshot_filename(self, base_name: str, extension: str = "png") -> str:
        """
        Generate a standardized filename for screenshots with timestamp
        
        Args:
            base_name: Base name for the screenshot file
            extension: File extension (default: png)
            
        Returns:
            Generated filename
        """
        # Generate timestamp using the imported format_timestamp function
        timestamp = format_timestamp("%Y%m%d_%H%M%S")
        
        # Sanitize base_name to remove invalid characters
        base_name = "".join(c if c.isalnum() or c == "_" else "_" for c in base_name)
        
        # Add file extension if not included
        if not extension.startswith("."):
            extension = f".{extension}"
        
        if not base_name.endswith(extension):
            filename = f"{base_name}_{timestamp}{extension}"
        else:
            # If extension is already in base_name, insert timestamp before extension
            filename = f"{base_name[:-len(extension)]}_{timestamp}{extension}"
        
        return filename

    def get_screenshot_path(self, filename: str, subfolder: str = None) -> str:
        """
        Get the full path for a screenshot file
        
        Args:
            filename: Filename for the screenshot
            subfolder: Optional subfolder within screenshot_dir
            
        Returns:
            Full path to the screenshot file
        """
        # Determine directory path
        if subfolder:
            directory = os.path.join(self.screenshot_dir, subfolder)
            # Create directory if it doesn't exist
            if self.create_dirs:
                self.create_directory(directory)
        else:
            directory = self.screenshot_dir
        
        # Combine directory and filename
        file_path = os.path.join(directory, filename)
        
        return file_path

    def create_directory(self, directory_path: str) -> bool:
        """
        Create a directory if it doesn't exist
        
        Args:
            directory_path: Path to the directory to create
            
        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                self.logger.info(f"Created directory: {directory_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory_path}: {str(e)}")
            return False

    def clean_old_screenshots(self, days: int = 7) -> int:
        """
        Clean screenshots older than the specified age
        
        Args:
            days: Number of days old a screenshot must be to be deleted
            
        Returns:
            Number of files deleted
        """
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        deleted_count = 0
        
        # Walk through screenshot directory and all subdirectories
        for root, _, files in os.walk(self.screenshot_dir):
            for file in files:
                # Only process image files
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    
                    # Check file modification time
                    mod_time = os.path.getmtime(file_path)
                    
                    # Delete if older than cutoff date
                    if mod_time < cutoff_timestamp:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to delete old screenshot {file_path}: {str(e)}")
        
        self.logger.info(f"Cleaned {deleted_count} old screenshots")
        return deleted_count