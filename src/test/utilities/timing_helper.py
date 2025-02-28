"""
Utility module providing timing and performance measurement tools for the Storydoc test automation framework.
This module helps track execution times, enforce SLA compliance, and generate performance metrics.
"""

import time
import datetime
import functools
import copy
import statistics
import contextlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Internal imports
from ..utilities.logger import get_logger
from ..config.timeout_config import DEFAULT_TIMEOUT, ELEMENT_TIMEOUT, PAGE_LOAD_TIMEOUT
from ..config.sla_config import OPERATION_SLAS

# Set up logger
logger = get_logger(__name__)

# Global dictionaries to store timing data and active timers
_timing_data = {}  # Format: {category: [{operation, execution_time, timestamp, metadata}]}
_active_timers = {}  # Format: {timer_name: start_time}
_metric_callbacks = []  # List of callback functions to call when metrics are recorded


def register_metric_callback(callback_func: Callable) -> bool:
    """
    Register a callback function to be called when timing metrics are recorded
    
    Args:
        callback_func: Callback function that accepts (category, operation, execution_time, metadata)
        
    Returns:
        True if callback was registered successfully
    """
    if not callable(callback_func):
        logger.error(f"Cannot register non-callable as metric callback: {callback_func}")
        return False
    
    if callback_func not in _metric_callbacks:
        _metric_callbacks.append(callback_func)
        logger.debug(f"Registered metric callback: {callback_func.__name__}")
        return True
    
    return False


def unregister_metric_callback(callback_func: Callable) -> bool:
    """
    Unregister a previously registered callback function
    
    Args:
        callback_func: The callback function to unregister
        
    Returns:
        True if callback was unregistered successfully
    """
    if callback_func in _metric_callbacks:
        _metric_callbacks.remove(callback_func)
        logger.debug(f"Unregistered metric callback: {callback_func.__name__}")
        return True
    
    return False


def notify_metric_callbacks(category: str, operation: str, execution_time: float, metadata: Dict) -> None:
    """
    Notify all registered callbacks about a timing metric
    
    Args:
        category: Category of the operation (e.g., 'page_navigation', 'element_interaction')
        operation: Name of the specific operation
        execution_time: Execution time in seconds
        metadata: Additional metadata about the operation
    """
    for callback in _metric_callbacks:
        try:
            callback(category, operation, execution_time, metadata)
        except Exception as e:
            logger.error(f"Error in metric callback {callback.__name__}: {str(e)}")


def timeit(func: Callable) -> Callable:
    """
    Decorator that measures execution time of a function
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function that measures execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Starting execution of {func_name}")
        
        # Record start time
        start_time = time.perf_counter()
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # Calculate execution time
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Log the execution time
        logger.debug(f"Function {func_name} executed in {get_formatted_time(execution_time)}")
        
        # Notify callbacks
        if hasattr(func, '__module__') and func.__module__:
            category = func.__module__.split('.')[-1]
            notify_metric_callbacks(category, func_name, execution_time, {"module": func.__module__})
        
        return result
    
    return wrapper


def measure_time(func: Callable, operation_name: str = None, log_result: bool = True, 
                notify_callbacks: bool = True) -> Tuple[Any, float]:
    """
    Measures execution time of a code block or function call
    
    Args:
        func: Function to execute and measure
        operation_name: Name of the operation for logging and metrics
        log_result: Whether to log the execution time
        notify_callbacks: Whether to notify metric callbacks
        
    Returns:
        Tuple containing (result, execution_time_seconds)
    """
    # Use function name if operation_name not provided
    if operation_name is None and hasattr(func, '__name__'):
        operation_name = func.__name__
    elif operation_name is None:
        operation_name = "unnamed_operation"
    
    # Record start time
    start_time = time.perf_counter()
    
    # Execute the function
    result = func()
    
    # Calculate execution time
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    # Log the result if requested
    if log_result:
        logger.debug(f"Operation {operation_name} executed in {get_formatted_time(execution_time)}")
    
    # Notify callbacks if requested
    if notify_callbacks:
        # Try to determine category from function module if available
        category = "general"
        if hasattr(func, '__module__') and func.__module__:
            category = func.__module__.split('.')[-1]
        
        notify_metric_callbacks(category, operation_name, execution_time, {})
    
    return result, execution_time


def get_formatted_time(seconds: float) -> str:
    """
    Formats time in seconds to a human-readable format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"
    else:
        hours = int(seconds / 3600)
        remaining = seconds % 3600
        minutes = int(remaining / 60)
        remaining_seconds = remaining % 60
        return f"{hours}h {minutes}m {remaining_seconds:.2f}s"


def is_within_sla(measured_time: float, operation_type: str, operation_name: str = "") -> bool:
    """
    Checks if a measured time is within SLA requirements
    
    Args:
        measured_time: Measured execution time in seconds
        operation_type: Type of operation (e.g., 'page_navigation', 'element_interaction')
        operation_name: Name of the specific operation for context in logs
        
    Returns:
        True if within SLA, False otherwise
    """
    # Get the SLA threshold from OPERATION_SLAS
    threshold = None
    
    if operation_type in OPERATION_SLAS:
        threshold = OPERATION_SLAS[operation_type].get("target_response_time")
    
    # If no specific SLA found, use defaults based on operation type
    if threshold is None:
        if operation_type == "page_navigation":
            threshold = PAGE_LOAD_TIMEOUT
        elif operation_type == "element_interaction":
            threshold = ELEMENT_TIMEOUT
        else:
            threshold = DEFAULT_TIMEOUT
    
    # Check if measured time is within SLA
    is_compliant = measured_time <= threshold
    
    # Log warning if SLA is not met
    if not is_compliant:
        operation_info = f"Operation '{operation_name}' of type '{operation_type}'" if operation_name else f"Operation type '{operation_type}'"
        logger.warning(f"SLA not met: {operation_info} took {get_formatted_time(measured_time)}, exceeds threshold of {get_formatted_time(threshold)}")
    
    return is_compliant


def store_timing(category: str, operation: str, execution_time: float, metadata: Dict = None) -> bool:
    """
    Stores timing data for later analysis and reporting
    
    Args:
        category: Category of the operation (e.g., 'page_navigation', 'element_interaction')
        operation: Name of the specific operation
        execution_time: Execution time in seconds
        metadata: Additional metadata about the operation
        
    Returns:
        True if successfully stored, False otherwise
    """
    global _timing_data
    
    # Initialize category if it doesn't exist
    if category not in _timing_data:
        _timing_data[category] = []
    
    # Create the timing entry
    timing_entry = {
        "operation": operation,
        "execution_time": execution_time,
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Add the entry to the appropriate category
    _timing_data[category].append(timing_entry)
    
    # Notify callbacks
    notify_metric_callbacks(category, operation, execution_time, metadata or {})
    
    logger.debug(f"Stored timing data for {category}.{operation}: {get_formatted_time(execution_time)}")
    
    return True


def get_timing_data(category: str = None) -> Dict:
    """
    Retrieves stored timing data for a specific category or all categories
    
    Args:
        category: Category to retrieve data for, or None for all categories
        
    Returns:
        Timing data dictionary
    """
    global _timing_data
    
    # Return data for specific category if requested
    if category and category in _timing_data:
        return copy.deepcopy(_timing_data[category])
    
    # Return all data
    return copy.deepcopy(_timing_data)


def clear_timing_data(category: str = None) -> bool:
    """
    Clears all stored timing data or for a specific category
    
    Args:
        category: Category to clear data for, or None for all categories
        
    Returns:
        True if successfully cleared, False otherwise
    """
    global _timing_data
    
    # Clear specific category if requested
    if category:
        if category in _timing_data:
            _timing_data[category] = []
            logger.debug(f"Cleared timing data for category: {category}")
            return True
        return False
    
    # Clear all timing data
    _timing_data = {}
    logger.debug("Cleared all timing data")
    
    return True


def get_performance_report(categories: List[str] = None) -> Dict:
    """
    Generates a performance report based on collected timing data
    
    Args:
        categories: List of categories to include in the report, or None for all categories
        
    Returns:
        Performance report with statistics
    """
    global _timing_data
    
    # Initialize the report
    report = {
        "categories": {},
        "summary": {
            "total_operations": 0,
            "total_time": 0,
            "average_time": 0,
            "sla_compliance": {
                "compliant": 0,
                "non_compliant": 0,
                "compliance_rate": 0
            }
        }
    }
    
    # Use all categories if none specified
    if not categories:
        categories = list(_timing_data.keys())
    
    # Counters for summary statistics
    total_operations = 0
    total_time = 0
    sla_compliant = 0
    sla_non_compliant = 0
    
    # Process each category
    for category in categories:
        if category not in _timing_data:
            continue
        
        category_data = _timing_data[category]
        if not category_data:
            continue
        
        # Initialize category statistics
        category_stats = {
            "operations": {},
            "total_operations": len(category_data),
            "total_time": sum(entry["execution_time"] for entry in category_data),
            "average_time": 0,
            "min_time": float('inf'),
            "max_time": 0
        }
        
        # Group by operation
        operations = {}
        for entry in category_data:
            operation = entry["operation"]
            execution_time = entry["execution_time"]
            
            if operation not in operations:
                operations[operation] = []
            
            operations[operation].append(execution_time)
            
            # Update category min/max
            category_stats["min_time"] = min(category_stats["min_time"], execution_time)
            category_stats["max_time"] = max(category_stats["max_time"], execution_time)
        
        # Calculate average time for the category
        if category_stats["total_operations"] > 0:
            category_stats["average_time"] = category_stats["total_time"] / category_stats["total_operations"]
        
        # Analyze each operation
        for operation, times in operations.items():
            # Calculate statistics
            count = len(times)
            min_time = min(times)
            max_time = max(times)
            avg_time = sum(times) / count
            median_time = statistics.median(times) if count > 0 else 0
            
            # Check SLA compliance
            is_compliant = is_within_sla(avg_time, category, operation)
            
            # Update compliance counters
            if is_compliant:
                sla_compliant += 1
            else:
                sla_non_compliant += 1
            
            # Store operation statistics
            category_stats["operations"][operation] = {
                "count": count,
                "min_time": min_time,
                "max_time": max_time,
                "avg_time": avg_time,
                "median_time": median_time,
                "sla_compliant": is_compliant
            }
        
        # Update report with category statistics
        report["categories"][category] = category_stats
        
        # Update summary counters
        total_operations += category_stats["total_operations"]
        total_time += category_stats["total_time"]
    
    # Calculate summary statistics
    report["summary"]["total_operations"] = total_operations
    report["summary"]["total_time"] = total_time
    if total_operations > 0:
        report["summary"]["average_time"] = total_time / total_operations
    
    # Calculate compliance rate
    total_compliance_checks = sla_compliant + sla_non_compliant
    if total_compliance_checks > 0:
        compliance_rate = (sla_compliant / total_compliance_checks) * 100
    else:
        compliance_rate = 0
    
    report["summary"]["sla_compliance"]["compliant"] = sla_compliant
    report["summary"]["sla_compliance"]["non_compliant"] = sla_non_compliant
    report["summary"]["sla_compliance"]["compliance_rate"] = compliance_rate
    
    return report


def wait_until(condition_func: Callable, timeout: float = DEFAULT_TIMEOUT, 
               poll_interval: float = 0.5, condition_description: str = None) -> bool:
    """
    Waits until a condition is met or timeout occurs
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        poll_interval: Time between checks in seconds
        condition_description: Description of the condition for logging
        
    Returns:
        True if condition met, False if timeout occurred
    """
    if condition_description is None:
        if hasattr(condition_func, '__name__'):
            condition_description = condition_func.__name__
        else:
            condition_description = "condition"
    
    logger.debug(f"Waiting for {condition_description} (timeout: {timeout}s, interval: {poll_interval}s)")
    
    start_time = time.perf_counter()
    
    while True:
        try:
            if condition_func():
                elapsed = time.perf_counter() - start_time
                logger.debug(f"Condition '{condition_description}' met after {get_formatted_time(elapsed)}")
                return True
        except Exception as e:
            logger.debug(f"Error checking condition: {str(e)}")
        
        # Check for timeout
        elapsed = time.perf_counter() - start_time
        if elapsed >= timeout:
            logger.warning(f"Timeout waiting for condition '{condition_description}' after {get_formatted_time(elapsed)}")
            return False
        
        # Wait before next check
        time.sleep(poll_interval)


def start_timer(timer_name: str = None) -> str:
    """
    Starts a named timer for measuring execution time
    
    Args:
        timer_name: Name of the timer, or None to generate a unique name
        
    Returns:
        Name of the started timer
    """
    global _active_timers
    
    # Generate a unique name if not provided
    if timer_name is None:
        timer_name = f"timer_{len(_active_timers) + 1}_{time.time()}"
    
    # Store the start time
    _active_timers[timer_name] = time.perf_counter()
    
    logger.debug(f"Started timer: {timer_name}")
    
    return timer_name


def stop_timer(timer_name: str, log_result: bool = True, 
               category: str = None, metadata: Dict = None) -> float:
    """
    Stops a named timer and returns the elapsed time
    
    Args:
        timer_name: Name of the timer to stop
        log_result: Whether to log the elapsed time
        category: Category to store the timing data under, if storing
        metadata: Additional metadata to store with the timing data
        
    Returns:
        Elapsed time in seconds, or -1 if timer not found
    """
    global _active_timers
    
    # Check if timer exists
    if timer_name not in _active_timers:
        logger.warning(f"Timer not found: {timer_name}")
        return -1
    
    # Get the start time and calculate elapsed time
    start_time = _active_timers[timer_name]
    elapsed_time = time.perf_counter() - start_time
    
    # Remove the timer
    del _active_timers[timer_name]
    
    # Log the result if requested
    if log_result:
        logger.debug(f"Timer {timer_name} stopped after {get_formatted_time(elapsed_time)}")
    
    # Store timing data if category provided
    if category:
        store_timing(category, timer_name, elapsed_time, metadata or {})
    
    return elapsed_time


def get_timestamp(format_string: str = None) -> str:
    """
    Returns a formatted timestamp for the current time
    
    Args:
        format_string: Format string for the timestamp, or None for ISO format
        
    Returns:
        Formatted timestamp string
    """
    now = datetime.datetime.now()
    
    if format_string:
        return now.strftime(format_string)
    
    return now.isoformat()


class Timer:
    """
    Class for precise timing measurements with context manager support
    """
    
    def __init__(self, name: str = None, category: str = None, auto_start: bool = False):
        """
        Initialize a new Timer instance
        
        Args:
            name: Name of the timer (default: auto-generated)
            category: Category for storing timing data
            auto_start: Whether to automatically start the timer upon initialization
        """
        self.name = name or f"timer_{id(self)}_{time.time()}"
        self.category = category
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.running = False
        self.metadata = {}
        
        if auto_start:
            self.start()
    
    def start(self):
        """
        Starts the timer
        
        Returns:
            Self reference for method chaining
        """
        if self.running:
            logger.warning(f"Timer {self.name} is already running")
            return self
        
        self.start_time = time.perf_counter()
        self.running = True
        logger.debug(f"Timer {self.name} started")
        
        return self
    
    def stop(self, store_result: bool = True):
        """
        Stops the timer and calculates elapsed time
        
        Args:
            store_result: Whether to store the timing result (if category is set)
            
        Returns:
            Elapsed time in seconds
        """
        if not self.running:
            logger.warning(f"Timer {self.name} is not running")
            return self.elapsed_time
        
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time
        self.running = False
        
        logger.debug(f"Timer {self.name} stopped after {get_formatted_time(self.elapsed_time)}")
        
        if store_result and self.category:
            store_timing(self.category, self.name, self.elapsed_time, self.metadata)
        
        return self.elapsed_time
    
    def reset(self):
        """
        Resets the timer to initial state
        
        Returns:
            Self reference for method chaining
        """
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.running = False
        
        logger.debug(f"Timer {self.name} reset")
        
        return self
    
    def add_metadata(self, additional_metadata: Dict):
        """
        Adds metadata to be stored with timing information
        
        Args:
            additional_metadata: Dictionary of metadata to add
            
        Returns:
            Self reference for method chaining
        """
        self.metadata.update(additional_metadata)
        return self
    
    def get_elapsed(self):
        """
        Gets the elapsed time, even for running timers
        
        Returns:
            Elapsed time in seconds
        """
        if not self.running:
            return self.elapsed_time
        
        # For running timers, calculate current elapsed time
        return time.perf_counter() - self.start_time
    
    def __enter__(self):
        """
        Context manager entry, starts the timer
        
        Returns:
            Self reference
        """
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit, stops the timer
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        # Add exception info to metadata if an exception occurred
        if exc_type is not None:
            self.add_metadata({
                "exception_type": exc_type.__name__,
                "exception_message": str(exc_val)
            })
        
        self.stop(store_result=True)


class TimingContext:
    """
    Context manager for timing blocks of code
    """
    
    def __init__(self, operation_name: str, category: str = None, 
                 log_result: bool = True, notify_callbacks: bool = True):
        """
        Initialize a new TimingContext
        
        Args:
            operation_name: Name of the operation being timed
            category: Category for the operation
            log_result: Whether to log the timing result
            notify_callbacks: Whether to notify timing callbacks
        """
        self.operation_name = operation_name
        self.category = category or "general"
        self.log_result = log_result
        self.notify_callbacks = notify_callbacks
        self.timer = Timer(name=operation_name, category=category)
    
    def __enter__(self):
        """
        Context manager entry, starts the timer
        
        Returns:
            Self reference
        """
        self.timer.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit, stops the timer and logs/records results
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        # Add exception info to metadata if an exception occurred
        if exc_type is not None:
            self.timer.add_metadata({
                "exception_type": exc_type.__name__,
                "exception_message": str(exc_val)
            })
        
        # Stop the timer and get the elapsed time
        elapsed_time = self.timer.stop(store_result=False)
        
        # Log the result if requested
        if self.log_result:
            logger.debug(f"Operation {self.operation_name} completed in {get_formatted_time(elapsed_time)}")
        
        # Check if within SLA
        is_within_sla(elapsed_time, self.category, self.operation_name)
        
        # Notify callbacks if requested
        if self.notify_callbacks:
            notify_metric_callbacks(self.category, self.operation_name, elapsed_time, self.timer.metadata)
    
    def get_elapsed_time(self):
        """
        Gets the elapsed time so far
        
        Returns:
            Elapsed time in seconds
        """
        return self.timer.get_elapsed()


class TimingStats:
    """
    Class for calculating statistics on timing measurements
    """
    
    def __init__(self, initial_measurements: List[float] = None):
        """
        Initialize a new TimingStats instance
        
        Args:
            initial_measurements: Initial list of timing measurements
        """
        self.measurements = initial_measurements.copy() if initial_measurements else []
    
    def add_measurement(self, time_value: float):
        """
        Adds a new timing measurement
        
        Args:
            time_value: Time value in seconds
        """
        self.measurements.append(time_value)
    
    def add_measurements(self, time_values: List[float]):
        """
        Adds multiple timing measurements
        
        Args:
            time_values: List of time values in seconds
        """
        self.measurements.extend(time_values)
    
    def get_mean(self) -> float:
        """
        Calculates mean of timing measurements
        
        Returns:
            Mean value or 0 if no measurements
        """
        if not self.measurements:
            return 0
        
        return statistics.mean(self.measurements)
    
    def get_median(self) -> float:
        """
        Calculates median of timing measurements
        
        Returns:
            Median value or 0 if no measurements
        """
        if not self.measurements:
            return 0
        
        return statistics.median(self.measurements)
    
    def get_min(self) -> float:
        """
        Gets minimum timing measurement
        
        Returns:
            Minimum value or 0 if no measurements
        """
        if not self.measurements:
            return 0
        
        return min(self.measurements)
    
    def get_max(self) -> float:
        """
        Gets maximum timing measurement
        
        Returns:
            Maximum value or 0 if no measurements
        """
        if not self.measurements:
            return 0
        
        return max(self.measurements)
    
    def get_count(self) -> int:
        """
        Gets number of measurements
        
        Returns:
            Number of measurements
        """
        return len(self.measurements)
    
    def get_statistics(self) -> Dict:
        """
        Gets all statistics as a dictionary
        
        Returns:
            Dictionary with all statistics
        """
        return {
            "mean": self.get_mean(),
            "median": self.get_median(),
            "min": self.get_min(),
            "max": self.get_max(),
            "count": self.get_count()
        }
    
    def clear(self):
        """
        Clears all measurements
        """
        self.measurements = []