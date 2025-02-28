"""
Utility module providing retry mechanisms for handling flaky operations in the Storydoc test automation framework.
Implements decorators and functions for automatic retry of operations that may fail intermittently due to timing,
network, or other transient issues.
"""

import time
import functools
import traceback
import random
from typing import Callable, Any, Optional, Tuple, Dict, List, Type, TypeVar, Union

# Import logging functions
from .logger import log_info, log_warning, log_error

# Import timeout constants
from ..config.timeout_config import MAX_RETRY_COUNT, RETRY_TIMEOUT

# Import configuration manager
from .config_manager import get_config

# Module version
__version__ = "1.0.0"


class RetryExceededError(Exception):
    """Custom exception raised when maximum retry attempts have been exhausted."""
    
    def __init__(self, original_exception: Exception, attempts: int, function_name: str):
        """Initialize the RetryExceededError with details about the retry attempts.
        
        Args:
            original_exception: The last exception that caused the retry to fail
            attempts: Number of retry attempts made
            function_name: Name of the function that was being retried
        """
        self.original_exception = original_exception
        self.attempts = attempts
        self.function_name = function_name
        
        message = f"Function '{function_name}' failed after {attempts} attempts: {str(original_exception)}"
        super().__init__(message)


def calculate_wait_time(attempt: int, base_delay: float, backoff_factor: float, add_jitter: bool) -> float:
    """Calculates wait time using exponential backoff with optional jitter for retry mechanism.
    
    Args:
        attempt: Current attempt number (1-based)
        base_delay: Base delay in seconds
        backoff_factor: Factor to increase delay with each attempt
        add_jitter: Whether to add random jitter to the delay
        
    Returns:
        float: Calculated wait time in seconds
    """
    # Calculate exponential backoff: base_delay * (backoff_factor ^ (attempt-1))
    wait_time = base_delay * (backoff_factor ** (attempt - 1))
    
    # Add jitter if requested (±15%)
    if add_jitter:
        jitter_factor = random.uniform(0.85, 1.15)
        wait_time *= jitter_factor
    
    return wait_time


def format_exception(exception: Exception, include_traceback: bool = False) -> str:
    """Formats exception information for logging during retry attempts.
    
    Args:
        exception: The exception to format
        include_traceback: Whether to include full traceback information
        
    Returns:
        str: Formatted exception details
    """
    # Extract exception type and message
    exception_type = type(exception).__name__
    exception_message = str(exception)
    
    # Format basic exception information
    result = f"{exception_type}: {exception_message}"
    
    # If include_traceback is True, append formatted traceback
    if include_traceback:
        tb = traceback.format_exc()
        result = f"{result}\n{tb}"
    
    return result


def retry(
    max_attempts: Optional[int] = None,
    delay: Optional[float] = None,
    backoff_factor: Optional[float] = None,
    exceptions: Optional[tuple] = None,
    add_jitter: Optional[bool] = None,
    raise_original_exception: Optional[bool] = None
) -> Callable:
    """Decorator that retries a function if it raises specified exceptions.
    Implements exponential backoff between retry attempts.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: MAX_RETRY_COUNT from config)
        delay: Initial delay between retries in seconds (default: RETRY_TIMEOUT from config)
        backoff_factor: Factor by which the delay increases with each attempt (default: 2)
        exceptions: Tuple of exception types to catch and retry (default: (Exception,))
        add_jitter: Whether to add random jitter to the delay (default: True)
        raise_original_exception: Whether to raise the original exception or a RetryExceededError (default: False)
        
    Returns:
        Callable: Decorated function with retry logic
    """
    # Set default values if not provided
    if max_attempts is None:
        max_attempts = get_config("retry_attempts", MAX_RETRY_COUNT)
    
    if delay is None:
        delay = get_config("retry_delay", RETRY_TIMEOUT)
    
    if backoff_factor is None:
        backoff_factor = get_config("retry_backoff_factor", 2)
    
    if exceptions is None:
        exceptions = (Exception,)
    
    if add_jitter is None:
        add_jitter = True
    
    if raise_original_exception is None:
        raise_original_exception = False
    
    def decorator(func: Callable) -> Callable:
        """Decorator function that wraps the target function with retry logic."""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper function that implements retry logic."""
            
            # Initialize attempt counter, last_exception, and success flag
            attempt = 0
            last_exception = None
            success = False
            
            # Loop until max_attempts reached or success flag set
            while attempt < max_attempts and not success:
                attempt += 1
                
                try:
                    # Try to execute the wrapped function and set success flag if successful
                    result = func(*args, **kwargs)
                    success = True
                    
                except exceptions as e:
                    # Catch specified exceptions and store the last exception
                    last_exception = e
                    
                    # If this was the last attempt, don't wait
                    if attempt >= max_attempts:
                        break
                    
                    # Log retry attempt with attempt number, function name, and exception details
                    formatted_exception = format_exception(e, include_traceback=False)
                    log_warning(
                        f"Retry attempt {attempt}/{max_attempts} for '{func.__name__}' after error: {formatted_exception}"
                    )
                    
                    # Calculate delay using exponential backoff: delay * (backoff_factor ^ (attempt-1))
                    wait_time = calculate_wait_time(attempt, delay, backoff_factor, add_jitter)
                    
                    # Sleep for the calculated delay time before next attempt
                    time.sleep(wait_time)
            
            # If all attempts fail and raise_original_exception is True, raise the last exception
            if not success:
                if raise_original_exception:
                    log_error(
                        f"Function '{func.__name__}' failed after {attempt} attempts. Raising original exception."
                    )
                    raise last_exception
                else:
                    # Otherwise, raise RetryExceededError with details
                    log_error(
                        f"Function '{func.__name__}' failed after {attempt} attempts. Raising RetryExceededError."
                    )
                    raise RetryExceededError(last_exception, attempt, func.__name__)
            
            # Return the result of the wrapped function if successful
            return result
        
        return wrapper
    
    return decorator


def retry_on_exceptions(
    exception_types: tuple,
    max_attempts: Optional[int] = None,
    delay: Optional[float] = None,
    backoff_factor: Optional[float] = None,
    add_jitter: Optional[bool] = None,
    raise_original_exception: Optional[bool] = None
) -> Callable:
    """Decorator that retries a function only if it raises specific exception types.
    More targeted version of the retry decorator.
    
    Args:
        exception_types: Tuple of exception types to catch and retry
        max_attempts: Maximum number of retry attempts (default: MAX_RETRY_COUNT from config)
        delay: Initial delay between retries in seconds (default: RETRY_TIMEOUT from config)
        backoff_factor: Factor by which the delay increases with each attempt (default: 2)
        add_jitter: Whether to add random jitter to the delay (default: True)
        raise_original_exception: Whether to raise the original exception or a RetryExceededError (default: False)
        
    Returns:
        Callable: Decorated function with retry logic for specific exceptions
    """
    return retry(
        max_attempts=max_attempts,
        delay=delay,
        backoff_factor=backoff_factor,
        exceptions=exception_types,
        add_jitter=add_jitter,
        raise_original_exception=raise_original_exception
    )


def retry_on_predicate(
    predicate: Callable[[Any], bool],
    max_attempts: Optional[int] = None,
    delay: Optional[float] = None,
    backoff_factor: Optional[float] = None,
    add_jitter: Optional[bool] = None
) -> Callable:
    """Decorator that retries a function if the result doesn't meet a specified predicate function's criteria.
    
    Args:
        predicate: Function that takes the result and returns True if it meets the criteria or False to retry
        max_attempts: Maximum number of retry attempts (default: MAX_RETRY_COUNT from config)
        delay: Initial delay between retries in seconds (default: RETRY_TIMEOUT from config)
        backoff_factor: Factor by which the delay increases with each attempt (default: 2)
        add_jitter: Whether to add random jitter to the delay (default: True)
        
    Returns:
        Callable: Decorated function with retry logic based on predicate
    """
    # Set default values if not provided
    if max_attempts is None:
        max_attempts = get_config("retry_attempts", MAX_RETRY_COUNT)
    
    if delay is None:
        delay = get_config("retry_delay", RETRY_TIMEOUT)
    
    if backoff_factor is None:
        backoff_factor = get_config("retry_backoff_factor", 2)
    
    if add_jitter is None:
        add_jitter = True
    
    def decorator(func: Callable) -> Callable:
        """Decorator function that wraps the target function with retry logic based on predicate."""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper function that implements retry logic based on predicate."""
            
            # Initialize attempt counter
            attempt = 0
            
            # Loop until max_attempts reached or predicate returns True
            while attempt < max_attempts:
                attempt += 1
                
                # Execute the wrapped function and store the result
                result = func(*args, **kwargs)
                
                # If predicate(result) returns True, return the result
                if predicate(result):
                    return result
                
                # If this was the last attempt, return the last result
                if attempt >= max_attempts:
                    break
                
                # Log retry attempt with attempt number and function name
                log_warning(
                    f"Retry attempt {attempt}/{max_attempts} for '{func.__name__}': "
                    f"result did not satisfy predicate"
                )
                
                # Calculate delay using exponential backoff
                wait_time = calculate_wait_time(attempt, delay, backoff_factor, add_jitter)
                
                # Sleep for the calculated delay time before next attempt
                time.sleep(wait_time)
            
            # If all attempts fail, return the last result
            return result
        
        return wrapper
    
    return decorator


class Retry:
    """Class-based implementation of retry logic that can be used as a decorator or context manager."""
    
    def __init__(
        self,
        max_attempts: int = MAX_RETRY_COUNT,
        delay: float = RETRY_TIMEOUT,
        backoff_factor: float = 2,
        exceptions: tuple = (Exception,),
        add_jitter: bool = True,
        raise_original_exception: bool = False
    ):
        """Initialize the Retry instance with retry parameters.
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff_factor: Factor by which the delay increases with each attempt
            exceptions: Tuple of exception types to catch and retry
            add_jitter: Whether to add random jitter to the delay
            raise_original_exception: Whether to raise the original exception or a RetryExceededError
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions
        self.add_jitter = add_jitter
        self.raise_original_exception = raise_original_exception
        
        # Initialize attempts counter to 0
        self.attempts = 0
        # Initialize last_exception to None
        self.last_exception = None
    
    def __call__(self, func: Callable) -> Callable:
        """Makes the class callable as a decorator.
        
        Args:
            func: Function to decorate
            
        Returns:
            Callable: Decorated function with retry logic
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Reset state for each call
            self.reset()
            
            # Implement retry logic (similar to retry function)
            while self.attempts < self.max_attempts:
                self.attempts += 1
                
                try:
                    # Attempt to execute the function
                    result = func(*args, **kwargs)
                    return result
                
                except self.exceptions as e:
                    # Store the exception
                    self.last_exception = e
                    
                    # If this was the last attempt, don't wait
                    if self.attempts >= self.max_attempts:
                        break
                    
                    # Log the retry attempt
                    formatted_exception = format_exception(e, include_traceback=False)
                    log_warning(
                        f"Retry attempt {self.attempts}/{self.max_attempts} for '{func.__name__}' "
                        f"after error: {formatted_exception}"
                    )
                    
                    # Calculate wait time for next attempt
                    wait_time = calculate_wait_time(
                        self.attempts, self.delay, self.backoff_factor, self.add_jitter
                    )
                    
                    # Wait before next attempt
                    time.sleep(wait_time)
            
            # If all attempts fail, handle based on raise_original_exception setting
            if self.raise_original_exception:
                # Raise the original exception
                log_error(
                    f"Function '{func.__name__}' failed after {self.attempts} attempts. "
                    f"Raising original exception."
                )
                raise self.last_exception
            else:
                # Raise RetryExceededError
                log_error(
                    f"Function '{func.__name__}' failed after {self.attempts} attempts. "
                    f"Raising RetryExceededError."
                )
                raise RetryExceededError(self.last_exception, self.attempts, func.__name__)
        
        return wrapper
    
    def __enter__(self) -> 'Retry':
        """Context manager entry point for use in with statements.
        
        Returns:
            Retry: Self reference
        """
        # Reset attempts counter to 0
        # Reset last_exception to None
        self.reset()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit point that handles retries on exceptions.
        
        Args:
            exc_type: Exception type or None if no exception
            exc_val: Exception value or None if no exception
            exc_tb: Exception traceback or None if no exception
            
        Returns:
            bool: True to suppress exception, False to propagate
        """
        # If no exception occurred (exc_type is None), return False to proceed normally
        if exc_type is None:
            return False
        
        # Increment attempts counter
        self.attempts += 1
        
        # If exception type matches self.exceptions
        if issubclass(exc_type, self.exceptions):
            # Store the exception as last_exception
            self.last_exception = exc_val
            
            # If attempts < max_attempts, calculate wait time and sleep
            if self.attempts < self.max_attempts:
                # Log the retry attempt
                formatted_exception = format_exception(exc_val, include_traceback=False)
                log_warning(
                    f"Retry attempt {self.attempts}/{self.max_attempts} "
                    f"after error: {formatted_exception}"
                )
                
                # Calculate wait time for next attempt
                wait_time = calculate_wait_time(
                    self.attempts, self.delay, self.backoff_factor, self.add_jitter
                )
                
                # Wait before next attempt
                time.sleep(wait_time)
                
                # Return True to suppress exception and retry the block
                return True
        
        # If attempts >= max_attempts, return False to propagate exception
        # If exception type doesn't match self.exceptions, return False to propagate exception
        return False
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executes a function with retry logic.
        
        Args:
            func: Function to execute with retry
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Any: Result of the function execution
        """
        # Reset attempts counter to 0
        # Reset last_exception to None
        self.reset()
        
        # Loop until success or max_attempts reached
        while self.attempts < self.max_attempts:
            self.attempts += 1
            
            try:
                # Try to execute the function with provided args and kwargs
                result = func(*args, **kwargs)
                # If successful, return the result
                return result
            
            except self.exceptions as e:
                # Store the exception
                self.last_exception = e
                
                # If this was the last attempt, don't wait
                if self.attempts >= self.max_attempts:
                    break
                
                # Log the retry attempt
                formatted_exception = format_exception(e, include_traceback=False)
                log_warning(
                    f"Retry attempt {self.attempts}/{self.max_attempts} for function execution "
                    f"after error: {formatted_exception}"
                )
                
                # Calculate wait time for next attempt
                wait_time = calculate_wait_time(
                    self.attempts, self.delay, self.backoff_factor, self.add_jitter
                )
                
                # Wait before next attempt
                time.sleep(wait_time)
        
        # If max attempts reached, handle based on raise_original_exception setting
        if self.raise_original_exception:
            # Raise the original exception
            log_error(
                f"Function execution failed after {self.attempts} attempts. "
                f"Raising original exception."
            )
            raise self.last_exception
        else:
            # Raise RetryExceededError
            log_error(
                f"Function execution failed after {self.attempts} attempts. "
                f"Raising RetryExceededError."
            )
            raise RetryExceededError(self.last_exception, self.attempts, "execute")
    
    def reset(self) -> None:
        """Resets the retry state.
        
        Returns:
            None
        """
        # Reset attempts counter to 0
        self.attempts = 0
        # Reset last_exception to None
        self.last_exception = None