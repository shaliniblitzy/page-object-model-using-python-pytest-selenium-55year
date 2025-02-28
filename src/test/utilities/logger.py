"""
Configurable logging module for the Storydoc automation framework.

This module provides functions for logging test execution, errors, and integration with test reporting.
It supports configurable output formats, logging to both console and file, and adding test context.
"""

import logging
import os
import sys
import datetime
import inspect
import traceback
from colorama import init as colorama_init, Fore, Style

from ..config.constants import LOG_LEVEL, LOG_FORMAT, LOG_FILE_PATH
from ..config.config import get_config

# Initialize colorama for cross-platform colored terminal output
colorama_init()

# Global variables
LOGGER_INITIALIZED = False
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_LOG_FILE_PATH = "src/test/reports/logs/test_execution.log"

# Global logger instance
logger = logging.getLogger('storydoc_automation')


class ColoredFormatter(logging.Formatter):
    """Custom log formatter that adds colors to log messages based on log level."""
    
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }
    
    def __init__(self, fmt):
        """Initialize the colored formatter with the specified format string.
        
        Args:
            fmt: Format string for log messages
        """
        super().__init__(fmt)
    
    def format(self, record):
        """Format the log record with appropriate colors.
        
        Args:
            record: Log record to format
            
        Returns:
            str: Colored formatted log message
        """
        # Get the color for the log level
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        
        # Format the message using the parent class
        formatted_message = super().format(record)
        
        # Add color codes and reset at the end
        return f"{color}{formatted_message}{Style.RESET_ALL}"


class TestContextAdapter:
    """Adapter class that adds test context information to log messages."""
    
    def __init__(self, initial_context=None):
        """Initialize the adapter with an optional initial test context.
        
        Args:
            initial_context: Initial context dictionary
        """
        self.test_context = initial_context or {}
    
    def set_context(self, context):
        """Set or update the test context.
        
        Args:
            context: Context dictionary to set or update
        """
        self.test_context.update(context)
    
    def clear_context(self):
        """Clear the test context."""
        self.test_context = {}
    
    def get_context(self):
        """Return the current test context.
        
        Returns:
            dict: Current test context
        """
        return self.test_context.copy()
    
    def add_context_to_message(self, message):
        """Add test context information to the log message.
        
        Args:
            message: Original log message
            
        Returns:
            str: Message with context information
        """
        if not self.test_context:
            return message
        
        context_str = format_context(self.test_context)
        return f"{message} {context_str}"


def initialize_logger(
    log_level=None,
    log_format=None,
    log_file_path=None,
    console_output=True,
    file_output=True,
    use_colors=True
):
    """Initialize the logger with the specified configuration.
    
    Creates log directory if it doesn't exist.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format string for log messages
        log_file_path: Path to the log file
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file
        use_colors: Whether to use colors in console output
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global LOGGER_INITIALIZED, logger
    
    # Don't re-initialize if already initialized
    if LOGGER_INITIALIZED:
        return logger
    
    # Get log level from parameter, constant, config, or default
    if log_level is None:
        log_level = get_config("log_level", LOG_LEVEL) or DEFAULT_LOG_LEVEL
    
    # Convert string log level to logging constant if needed
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())
    
    # Get log format from parameter, constant, config, or default
    if log_format is None:
        log_format = get_config("log_format", LOG_FORMAT) or DEFAULT_LOG_FORMAT
    
    # Get log file path from parameter, constant, config, or default
    if log_file_path is None:
        log_file_path = get_config("log_file_path", LOG_FILE_PATH) or DEFAULT_LOG_FILE_PATH
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(level=log_level, format=log_format, handlers=[])
    
    # Configure our logger
    logger.setLevel(log_level)
    logger.propagate = False
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        if use_colors:
            console_handler.setFormatter(ColoredFormatter(log_format))
        else:
            console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if file_output:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    # Set initialized flag
    LOGGER_INITIALIZED = True
    
    return logger


def get_logger():
    """Returns the configured logger instance. Initializes the logger if not already initialized.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    global LOGGER_INITIALIZED, logger
    
    if not LOGGER_INITIALIZED:
        initialize_logger()
    
    return logger


def log_debug(message, context=None):
    """Logs a debug message with optional context information.
    
    Args:
        message: Message to log
        context: Optional context information
    """
    logger = get_logger()
    
    if context:
        message = f"{message} {format_context(context)}"
    
    logger.debug(message)


def log_info(message, context=None):
    """Logs an info message with optional context information.
    
    Args:
        message: Message to log
        context: Optional context information
    """
    logger = get_logger()
    
    if context:
        message = f"{message} {format_context(context)}"
    
    logger.info(message)


def log_warning(message, context=None):
    """Logs a warning message with optional context information.
    
    Args:
        message: Message to log
        context: Optional context information
    """
    logger = get_logger()
    
    if context:
        message = f"{message} {format_context(context)}"
    
    logger.warning(message)


def log_error(message, exception=None, context=None, include_traceback=True):
    """Logs an error message with exception details and optional context information.
    
    Args:
        message: Message to log
        exception: Optional exception that caused the error
        context: Optional context information
        include_traceback: Whether to include traceback in the log
    """
    logger = get_logger()
    
    # Add exception details if provided
    if exception:
        exception_name = type(exception).__name__
        exception_message = str(exception)
        message = f"{message} - {exception_name}: {exception_message}"
        
        # Add traceback if requested
        if include_traceback:
            tb = traceback.format_exc()
            message = f"{message}\n{tb}"
    
    # Add context if provided
    if context:
        message = f"{message} {format_context(context)}"
    
    logger.error(message)


def log_critical(message, exception=None, context=None, include_traceback=True):
    """Logs a critical error message with exception details and optional context information.
    
    Args:
        message: Message to log
        exception: Optional exception that caused the error
        context: Optional context information
        include_traceback: Whether to include traceback in the log
    """
    logger = get_logger()
    
    # Add exception details if provided
    if exception:
        exception_name = type(exception).__name__
        exception_message = str(exception)
        message = f"{message} - {exception_name}: {exception_message}"
        
        # Add traceback if requested
        if include_traceback:
            tb = traceback.format_exc()
            message = f"{message}\n{tb}"
    
    # Add context if provided
    if context:
        message = f"{message} {format_context(context)}"
    
    logger.critical(message)


def log_test_start(test_name, test_parameters=None):
    """Logs the start of a test case with test name and optional parameters.
    
    Args:
        test_name: Name of the test
        test_parameters: Optional test parameters
    """
    logger = get_logger()
    
    message = f"Starting test: {test_name}"
    
    if test_parameters:
        params_str = ", ".join(f"{k}={v}" for k, v in test_parameters.items())
        message = f"{message} with parameters: {params_str}"
    
    logger.info(message)


def log_test_end(test_name, status, duration):
    """Logs the end of a test case with result status and duration.
    
    Args:
        test_name: Name of the test
        status: Test result status (PASS, FAIL, ERROR, SKIP)
        duration: Test duration in seconds
    """
    logger = get_logger()
    
    message = f"Test {test_name} {status} (Duration: {duration:.2f}s)"
    
    # Log at different levels based on status
    if status == "PASS":
        logger.info(message)
    elif status in ["FAIL", "ERROR"]:
        logger.error(message)
    else:  # SKIP or other
        logger.warning(message)


def log_step(step_number, description, status="INFO"):
    """Logs a test step with step number, description, and status.
    
    Args:
        step_number: Step number
        description: Step description
        status: Step status (PASS, FAIL, ERROR, WARN)
    """
    logger = get_logger()
    
    message = f"Step {step_number}: {description} - {status}"
    
    # Log at different levels based on status
    if status in ["PASS", "INFO"]:
        logger.info(message)
    elif status in ["FAIL", "ERROR"]:
        logger.error(message)
    elif status == "WARN":
        logger.warning(message)
    else:
        logger.info(message)


def log_assertion(assertion_description, expected, actual, result):
    """Logs an assertion with expected vs. actual values and result.
    
    Args:
        assertion_description: Description of the assertion
        expected: Expected value
        actual: Actual value
        result: Assertion result (True if passed, False if failed)
    """
    logger = get_logger()
    
    message = f"Assertion: {assertion_description} - Expected: {expected}, Actual: {actual}"
    
    if result:
        message = f"{message} - PASS"
        logger.info(message)
    else:
        message = f"{message} - FAIL"
        logger.error(message)


def setup_file_logging(file_path, log_format=None):
    """Sets up file logging with the given file path and optional format.
    
    Args:
        file_path: Path to the log file
        log_format: Format string for log messages
        
    Returns:
        logging.FileHandler: The file handler that was added
    """
    logger = get_logger()
    
    # Create directory if it doesn't exist
    log_dir = os.path.dirname(file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(file_path)
    
    # Set formatter if provided
    if log_format:
        file_handler.setFormatter(logging.Formatter(log_format))
    else:
        file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return file_handler


def stop_file_logging(file_handler):
    """Stops file logging by removing the specified file handler.
    
    Args:
        file_handler: File handler to remove
        
    Returns:
        bool: True if handler was removed, False otherwise
    """
    logger = get_logger()
    
    if file_handler in logger.handlers:
        logger.removeHandler(file_handler)
        file_handler.close()
        return True
    return False


def get_caller_info():
    """Gets information about the caller function for detailed logging context.
    
    Returns:
        dict: Dictionary with caller information including filename, line number, function name
    """
    # Get the current frame
    current_frame = inspect.currentframe()
    
    # Get the caller's frame (2 frames up from this function)
    try:
        caller_frame = inspect.getouterframes(current_frame)[2]
        
        # Extract information from the frame
        filename = os.path.basename(caller_frame.filename)
        lineno = caller_frame.lineno
        function = caller_frame.function
        
        return {
            "file": filename,
            "line": lineno,
            "function": function
        }
    finally:
        # Cleanup to prevent reference cycles
        del current_frame


def format_context(context):
    """Formats context information for inclusion in log messages.
    
    Args:
        context: Context dictionary
        
    Returns:
        str: Formatted context string
    """
    if not context:
        return ""
    
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    return f"[Context: {context_str}]"