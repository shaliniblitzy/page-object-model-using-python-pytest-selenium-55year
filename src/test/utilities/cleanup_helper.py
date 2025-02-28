"""
Utility module for cleaning up test resources and managing test environment state.

Provides functions to clean up browser sessions, temporary files, test data, and other resources
after test execution to maintain a clean test environment.
"""

import os
import shutil
import glob
import time
from pathlib import Path

# Import internal utilities
from .driver_factory import DriverFactory
from .email_helper import EmailHelper
from .config_manager import get_config
from .logger import log_info, log_debug, log_error

# Registry to track resources that need cleanup
_cleanup_registry = []


def register_for_cleanup(resource, cleanup_type, cleanup_function):
    """
    Registers a resource for cleanup at the end of test execution
    
    Args:
        resource: The resource to clean up
        cleanup_type: Type of resource for logging purposes
        cleanup_function: Function to call for cleanup
        
    Returns:
        bool: True if resource was registered successfully, False otherwise
    """
    try:
        entry = {
            'resource': resource,
            'type': cleanup_type,
            'cleanup_function': cleanup_function
        }
        _cleanup_registry.append(entry)
        log_debug(f"Registered {cleanup_type} resource for cleanup")
        return True
    except Exception as e:
        log_error(f"Failed to register resource for cleanup: {str(e)}")
        return False


def cleanup_registered_resources():
    """
    Cleans up all registered resources
    
    Returns:
        dict: Summary of cleanup operations with success/failure counts
    """
    success_count = 0
    failure_count = 0
    
    log_info("Cleaning up registered resources")
    
    # Process registry in reverse order (LIFO)
    for entry in reversed(_cleanup_registry):
        try:
            resource = entry.get('resource')
            cleanup_type = entry.get('type', 'unknown')
            cleanup_function = entry.get('cleanup_function')
            
            if cleanup_function and callable(cleanup_function):
                cleanup_function(resource)
                log_debug(f"Successfully cleaned up {cleanup_type} resource")
                success_count += 1
            else:
                log_error(f"Invalid cleanup function for {cleanup_type} resource")
                failure_count += 1
                
        except Exception as e:
            log_error(f"Error cleaning up {entry.get('type', 'unknown')} resource: {str(e)}")
            failure_count += 1
    
    # Clear the registry after cleanup
    _cleanup_registry.clear()
    
    return {
        'success': success_count,
        'failure': failure_count
    }


def cleanup_drivers():
    """
    Cleans up all active WebDriver instances
    
    Returns:
        bool: True if all drivers were cleaned up successfully, False otherwise
    """
    log_info("Cleaning up WebDriver instances")
    
    try:
        DriverFactory.quit_all_drivers()
        log_info("Successfully cleaned up all WebDriver instances")
        return True
    except Exception as e:
        log_error(f"Error cleaning up WebDriver instances: {str(e)}")
        return False


def cleanup_temp_files(directory=None, pattern="*.*", recursive=False):
    """
    Cleans up temporary files created during test execution
    
    Args:
        directory: Directory containing temp files (default: from config)
        pattern: File pattern to match for cleanup
        recursive: Whether to look in subdirectories
        
    Returns:
        int: Number of files cleaned up
    """
    # Get temp directory from config if not provided
    if not directory:
        directory = get_config("temp_dir", "temp")
    
    log_info(f"Cleaning up temporary files in {directory} with pattern '{pattern}'")
    
    # Check if directory exists
    if not os.path.exists(directory):
        log_info(f"Directory {directory} does not exist for cleanup")
        return 0
    
    # Find files matching pattern
    if recursive:
        search_pattern = os.path.join(directory, "**", pattern)
        files = glob.glob(search_pattern, recursive=True)
    else:
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)
    
    # Remove each file
    removed_count = 0
    for file_path in files:
        try:
            os.remove(file_path)
            removed_count += 1
            log_debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            log_error(f"Failed to remove temporary file {file_path}: {str(e)}")
    
    log_info(f"Removed {removed_count} temporary files")
    return removed_count


def cleanup_directory(directory, remove_directory=False):
    """
    Cleans up a directory by removing all its contents or the directory itself
    
    Args:
        directory: Directory to clean up
        remove_directory: Whether to remove the directory itself
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    log_info(f"Cleaning up directory: {directory}")
    
    # Check if directory exists
    if not os.path.exists(directory):
        log_info(f"Directory {directory} does not exist for cleanup")
        return True  # Already clean
    
    try:
        if remove_directory:
            # Remove directory and all contents
            shutil.rmtree(directory)
            log_info(f"Removed directory: {directory}")
        else:
            # Remove contents but keep directory
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    log_debug(f"Removed subdirectory: {item_path}")
                else:
                    os.remove(item_path)
                    log_debug(f"Removed file: {item_path}")
            log_info(f"Cleaned up contents of directory: {directory}")
        
        return True
    except Exception as e:
        log_error(f"Error cleaning up directory {directory}: {str(e)}")
        return False


def cleanup_screenshots(directory=None, keep_failure_screenshots=True):
    """
    Cleans up screenshot files from test execution
    
    Args:
        directory: Directory containing screenshots (default: from config)
        keep_failure_screenshots: Whether to keep screenshots related to failures
        
    Returns:
        int: Number of screenshots cleaned up
    """
    # Get screenshots directory from config if not provided
    if not directory:
        directory = get_config("screenshot_dir", "screenshots")
    
    log_info(f"Cleaning up screenshots in {directory}")
    
    # Check if directory exists
    if not os.path.exists(directory):
        log_info(f"Screenshots directory {directory} does not exist for cleanup")
        return 0
    
    # Find all screenshot files
    files = glob.glob(os.path.join(directory, "*.png"))
    
    # Filter files if keeping failure screenshots
    if keep_failure_screenshots:
        files_to_remove = [f for f in files if "failure_" not in os.path.basename(f)]
    else:
        files_to_remove = files
    
    # Remove each file
    removed_count = 0
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            removed_count += 1
            log_debug(f"Removed screenshot: {file_path}")
        except Exception as e:
            log_error(f"Failed to remove screenshot {file_path}: {str(e)}")
    
    log_info(f"Removed {removed_count} screenshots")
    return removed_count


def cleanup_logs(directory=None, keep_last_n=5, archive_logs=False):
    """
    Cleans up log files from test execution
    
    Args:
        directory: Directory containing logs (default: from config)
        keep_last_n: Number of most recent log files to keep
        archive_logs: Whether to move logs to archive directory instead of deleting
        
    Returns:
        int: Number of log files cleaned up
    """
    # Get logs directory from config if not provided
    if not directory:
        directory = get_config("log_dir", "logs")
    
    log_info(f"Cleaning up logs in {directory}")
    
    # Check if directory exists
    if not os.path.exists(directory):
        log_info(f"Logs directory {directory} does not exist for cleanup")
        return 0
    
    # Find all log files and sort by modification time (oldest first)
    files = glob.glob(os.path.join(directory, "*.log"))
    files.sort(key=os.path.getmtime)
    
    # Keep the most recent logs
    if keep_last_n > 0 and len(files) > keep_last_n:
        files_to_handle = files[:-keep_last_n]  # All except the last n
    else:
        files_to_handle = []
    
    # Handle each file (archive or delete)
    handled_count = 0
    for file_path in files_to_handle:
        try:
            if archive_logs:
                # Create archive directory if it doesn't exist
                archive_dir = os.path.join(directory, "archive")
                os.makedirs(archive_dir, exist_ok=True)
                
                # Move file to archive
                archive_path = os.path.join(archive_dir, os.path.basename(file_path))
                shutil.move(file_path, archive_path)
                log_debug(f"Archived log file: {file_path} -> {archive_path}")
            else:
                # Delete file
                os.remove(file_path)
                log_debug(f"Removed log file: {file_path}")
            
            handled_count += 1
        except Exception as e:
            log_error(f"Failed to handle log file {file_path}: {str(e)}")
    
    log_info(f"Handled {handled_count} log files")
    return handled_count


def cleanup_test_email_accounts():
    """
    Placeholder cleanup function for test email accounts (Mailinator doesn't support cleanup API)
    
    Returns:
        bool: Always returns True as actual cleanup can't be performed
    """
    log_info("Note: Mailinator doesn't support programmatic inbox cleanup")
    log_info("Mailinator automatically cleans up inboxes after a few hours")
    return True


def cleanup_after_test(clean_drivers=True, clean_screenshots=True, clean_temp_files=True):
    """
    Comprehensive cleanup after test execution
    
    Args:
        clean_drivers: Whether to clean up WebDriver instances
        clean_screenshots: Whether to clean up screenshots
        clean_temp_files: Whether to clean up temporary files
        
    Returns:
        dict: Summary of cleanup operations
    """
    log_info("Performing comprehensive cleanup after test execution")
    
    results = {
        'registered_resources': {},
        'drivers': False,
        'screenshots': 0,
        'temp_files': 0
    }
    
    # Clean up registered resources
    results['registered_resources'] = cleanup_registered_resources()
    
    # Clean up drivers if requested
    if clean_drivers:
        results['drivers'] = cleanup_drivers()
    
    # Clean up screenshots if requested
    if clean_screenshots:
        results['screenshots'] = cleanup_screenshots()
    
    # Clean up temporary files if requested
    if clean_temp_files:
        results['temp_files'] = cleanup_temp_files()
    
    log_info("Completed comprehensive cleanup")
    return results


class CleanupHelper:
    """
    Helper class that provides methods for cleaning up test resources
    """
    
    @staticmethod
    def register_for_cleanup(resource, cleanup_type, cleanup_function):
        """
        Static method to register a resource for cleanup
        
        Args:
            resource: The resource to clean up
            cleanup_type: Type of resource for logging purposes
            cleanup_function: Function to call for cleanup
            
        Returns:
            bool: True if resource was registered successfully
        """
        return register_for_cleanup(resource, cleanup_type, cleanup_function)
    
    @staticmethod
    def cleanup_registered_resources():
        """
        Static method to clean up all registered resources
        
        Returns:
            dict: Summary of cleanup operations
        """
        return cleanup_registered_resources()
    
    @staticmethod
    def cleanup_drivers():
        """
        Static method to clean up all WebDriver instances
        
        Returns:
            bool: True if all drivers were cleaned up successfully
        """
        return cleanup_drivers()
    
    @staticmethod
    def cleanup_temp_files(directory=None, pattern="*.*", recursive=False):
        """
        Static method to clean up temporary files
        
        Args:
            directory: Directory containing temp files
            pattern: File pattern to match for cleanup
            recursive: Whether to look in subdirectories
            
        Returns:
            int: Number of files cleaned up
        """
        return cleanup_temp_files(directory, pattern, recursive)
    
    @staticmethod
    def cleanup_directory(directory, remove_directory=False):
        """
        Static method to clean up a directory
        
        Args:
            directory: Directory to clean up
            remove_directory: Whether to remove the directory itself
            
        Returns:
            bool: True if cleanup was successful
        """
        return cleanup_directory(directory, remove_directory)
    
    @staticmethod
    def cleanup_screenshots(directory=None, keep_failure_screenshots=True):
        """
        Static method to clean up screenshot files
        
        Args:
            directory: Directory containing screenshots
            keep_failure_screenshots: Whether to keep screenshots related to failures
            
        Returns:
            int: Number of screenshots cleaned up
        """
        return cleanup_screenshots(directory, keep_failure_screenshots)
    
    @staticmethod
    def cleanup_logs(directory=None, keep_last_n=5, archive_logs=False):
        """
        Static method to clean up log files
        
        Args:
            directory: Directory containing logs
            keep_last_n: Number of most recent log files to keep
            archive_logs: Whether to move logs to archive directory instead of deleting
            
        Returns:
            int: Number of log files cleaned up
        """
        return cleanup_logs(directory, keep_last_n, archive_logs)
    
    @staticmethod
    def cleanup_after_test(clean_drivers=True, clean_screenshots=True, clean_temp_files=True):
        """
        Static method for comprehensive cleanup after test execution
        
        Args:
            clean_drivers: Whether to clean up WebDriver instances
            clean_screenshots: Whether to clean up screenshots
            clean_temp_files: Whether to clean up temporary files
            
        Returns:
            dict: Summary of cleanup operations
        """
        return cleanup_after_test(clean_drivers, clean_screenshots, clean_temp_files)


class CleanupContext:
    """
    Context manager for automatic resource cleanup
    """
    
    def __init__(self, resource, cleanup_function):
        """
        Initializes the cleanup context with a resource and cleanup function
        
        Args:
            resource: The resource to be managed
            cleanup_function: Function to call for cleanup
        """
        self._resource = resource
        self._cleanup_function = cleanup_function
    
    def __enter__(self):
        """
        Enter the context, return the resource
        
        Returns:
            The resource being managed
        """
        return self._resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context, clean up the resource
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception instance if an exception was raised
            exc_tb: Traceback if an exception was raised
            
        Returns:
            False to allow exceptions to propagate
        """
        try:
            if self._cleanup_function and callable(self._cleanup_function):
                self._cleanup_function(self._resource)
        except Exception as e:
            log_error(f"Error during context cleanup: {str(e)}")
        
        # Return False to allow exceptions to propagate
        return False