"""
Utility module that monitors, records, and analyzes performance metrics during test execution of the Storydoc application.
It tracks page load times, element interaction times, test execution durations, and validates compliance with defined 
Service Level Agreements (SLAs).
"""

import time
import datetime
import typing
import statistics
import copy
import threading
import json
import os
from typing import Dict, List, Optional, Any, Callable, Union

# Internal imports
from .logger import get_logger
from .timing_helper import Timer, get_formatted_time, is_within_sla, TimingStats
from .config_manager import get_config
from ..config.sla_config import OPERATION_SLAS, TEST_TYPE_SLAS, is_within_operation_sla

# Set up logger
logger = get_logger(__name__)

# Global variables for storing performance data
_performance_data = {}  # Format: {category: [{operation, execution_time, timestamp, metadata}]}
_active_timers = {}  # Format: {timer_id: Timer}
_metrics_callbacks = []  # Callbacks to be notified of new metrics

# Default report path
DEFAULT_REPORT_PATH = "src/test/reports/performance/"

# Lock for thread safety
_lock = threading.RLock()


def record_page_load_time(page_name: str, load_time: float, metadata: Dict = None) -> bool:
    """
    Records page load time for a specific page
    
    Args:
        page_name: Name of the page being loaded
        load_time: Page load time in seconds
        metadata: Additional metadata about the page load
        
    Returns:
        True if successfully recorded, False otherwise
    """
    with _lock:
        # Initialize category if it doesn't exist
        if "page_load" not in _performance_data:
            _performance_data["page_load"] = []
        
        # Create measurement entry
        entry = {
            "page_name": page_name,
            "load_time": load_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to performance data
        _performance_data["page_load"].append(entry)
        
        logger.debug(f"Recorded page load time for {page_name}: {get_formatted_time(load_time)}")
        
        # Notify callbacks
        notify_metric_callbacks("page_load", page_name, load_time, metadata or {})
        
        # Check SLA compliance
        check_sla_compliance("page_load", "page_navigation", load_time)
        
        return True


def record_element_interaction_time(element_identifier: str, operation: str, 
                                   interaction_time: float, metadata: Dict = None) -> bool:
    """
    Records element interaction time for a specific element operation
    
    Args:
        element_identifier: Identifier for the element (e.g., locator, name)
        operation: Type of operation (e.g., click, input, wait)
        interaction_time: Time taken for the operation in seconds
        metadata: Additional metadata about the interaction
        
    Returns:
        True if successfully recorded, False otherwise
    """
    with _lock:
        # Initialize category if it doesn't exist
        if "element_interaction" not in _performance_data:
            _performance_data["element_interaction"] = []
        
        # Create measurement entry
        entry = {
            "element_identifier": element_identifier,
            "operation": operation,
            "interaction_time": interaction_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to performance data
        _performance_data["element_interaction"].append(entry)
        
        logger.debug(f"Recorded element interaction time for {element_identifier}.{operation}: {get_formatted_time(interaction_time)}")
        
        # Notify callbacks
        notify_metric_callbacks("element_interaction", f"{element_identifier}.{operation}", 
                               interaction_time, metadata or {})
        
        # Check SLA compliance
        check_sla_compliance("element_interaction", "element_interaction", interaction_time)
        
        return True


def record_test_execution_time(test_name: str, test_type: str, 
                              execution_time: float, metadata: Dict = None) -> bool:
    """
    Records execution time for a specific test
    
    Args:
        test_name: Name of the test
        test_type: Type of test (e.g., user_registration, story_creation)
        execution_time: Execution time in seconds
        metadata: Additional metadata about the test execution
        
    Returns:
        True if successfully recorded, False otherwise
    """
    with _lock:
        # Initialize category if it doesn't exist
        if "test_execution" not in _performance_data:
            _performance_data["test_execution"] = []
        
        # Create measurement entry
        entry = {
            "test_name": test_name,
            "test_type": test_type,
            "execution_time": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to performance data
        _performance_data["test_execution"].append(entry)
        
        logger.debug(f"Recorded test execution time for {test_name} ({test_type}): {get_formatted_time(execution_time)}")
        
        # Notify callbacks
        notify_metric_callbacks("test_execution", test_name, execution_time, metadata or {})
        
        # Check SLA compliance
        check_sla_compliance("test_execution", test_type, execution_time)
        
        return True


def check_sla_compliance(category: str, operation_type: str, measured_time: float) -> bool:
    """
    Checks if a measured time complies with the relevant SLA
    
    Args:
        category: Category of the operation (page_load, element_interaction, test_execution)
        operation_type: Type of operation or test
        measured_time: Measured time in seconds
        
    Returns:
        True if within SLA, False otherwise
    """
    is_compliant = False
    
    # Determine which SLA checker to use based on category
    if category in ["page_load", "element_interaction"]:
        is_compliant = is_within_operation_sla(operation_type, measured_time)
    elif category == "test_execution":
        # Use the appropriate SLA checker from sla_config
        if operation_type in TEST_TYPE_SLAS:
            max_duration = TEST_TYPE_SLAS[operation_type].get("maximum_duration")
            is_compliant = measured_time <= max_duration
        else:
            # Default to within_sla if test_type not found
            is_compliant = is_within_sla(measured_time, "test_execution", operation_type)
    
    # Log the result
    if is_compliant:
        logger.debug(f"SLA compliance: {category}.{operation_type} - {get_formatted_time(measured_time)} - PASS")
    else:
        logger.warning(f"SLA compliance: {category}.{operation_type} - {get_formatted_time(measured_time)} - FAIL")
    
    return is_compliant


def start_performance_timer(name: str, category: str) -> str:
    """
    Starts a timer for measuring a specific performance category
    
    Args:
        name: Name of the operation being timed
        category: Category of the operation (page_load, element_interaction, test_execution)
        
    Returns:
        Timer ID that can be used to stop the timer
    """
    with _lock:
        # Create a timer
        timer = Timer(name=name, category=category)
        timer.start()
        
        # Generate a unique timer ID
        timer_id = f"{category}_{name}_{time.time()}"
        
        # Store the timer
        _active_timers[timer_id] = timer
        
        logger.debug(f"Started performance timer: {timer_id}")
        
        return timer_id


def stop_performance_timer(timer_id: str, metadata: Dict = None) -> float:
    """
    Stops a timer and records its measurement in the appropriate category
    
    Args:
        timer_id: Timer ID returned from start_performance_timer
        metadata: Additional metadata to include with the measurement
        
    Returns:
        Elapsed time in seconds
    """
    with _lock:
        if timer_id not in _active_timers:
            logger.warning(f"Timer not found: {timer_id}")
            return -1
        
        # Get the timer
        timer = _active_timers[timer_id]
        
        # Update metadata if provided
        if metadata:
            timer.add_metadata(metadata)
        
        # Stop the timer and get elapsed time
        elapsed_time = timer.stop(store_result=False)
        
        # Record the measurement based on category
        if timer.category == "page_load":
            record_page_load_time(timer.name, elapsed_time, timer.metadata)
        elif timer.category == "element_interaction":
            record_element_interaction_time(timer.name, "interaction", elapsed_time, timer.metadata)
        elif timer.category == "test_execution":
            record_test_execution_time(timer.name, "general", elapsed_time, timer.metadata)
        else:
            # Generic category
            if timer.category not in _performance_data:
                _performance_data[timer.category] = []
            
            entry = {
                "operation": timer.name,
                "execution_time": elapsed_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": timer.metadata
            }
            
            _performance_data[timer.category].append(entry)
            
            # Notify callbacks
            notify_metric_callbacks(timer.category, timer.name, elapsed_time, timer.metadata)
        
        # Remove the timer
        del _active_timers[timer_id]
        
        logger.debug(f"Stopped performance timer {timer_id}: {get_formatted_time(elapsed_time)}")
        
        return elapsed_time


def get_performance_data(category: str = None) -> Dict:
    """
    Retrieves performance data for a specific category or all categories
    
    Args:
        category: Category to retrieve data for, or None for all categories
        
    Returns:
        Performance data dictionary
    """
    with _lock:
        if category:
            return copy.deepcopy(_performance_data.get(category, {}))
        else:
            return copy.deepcopy(_performance_data)


def clear_performance_data(category: str = None) -> bool:
    """
    Clears performance data for a specific category or all categories
    
    Args:
        category: Category to clear data for, or None for all categories
        
    Returns:
        True if successfully cleared, False otherwise
    """
    with _lock:
        if category:
            if category in _performance_data:
                _performance_data[category] = []
                logger.info(f"Cleared performance data for category: {category}")
            else:
                logger.warning(f"Category not found: {category}")
                return False
        else:
            _performance_data.clear()
            logger.info("Cleared all performance data")
        
        return True


def register_metric_callback(callback_function: Callable) -> bool:
    """
    Registers a callback function to be called when new performance metrics are recorded
    
    Args:
        callback_function: Function that takes (category, operation, measured_time, metadata)
        
    Returns:
        True if successfully registered, False otherwise
    """
    with _lock:
        if not callable(callback_function):
            logger.error(f"Cannot register non-callable as metric callback: {callback_function}")
            return False
        
        if callback_function not in _metrics_callbacks:
            _metrics_callbacks.append(callback_function)
            logger.info(f"Registered metric callback: {callback_function.__name__}")
            return True
        
        return False


def unregister_metric_callback(callback_function: Callable) -> bool:
    """
    Unregisters a previously registered callback function
    
    Args:
        callback_function: Callback function to unregister
        
    Returns:
        True if successfully unregistered, False otherwise
    """
    with _lock:
        if callback_function in _metrics_callbacks:
            _metrics_callbacks.remove(callback_function)
            logger.info(f"Unregistered metric callback: {callback_function.__name__}")
            return True
        
        return False


def notify_metric_callbacks(category: str, operation: str, measured_time: float, metadata: Dict) -> None:
    """
    Notifies all registered callbacks about a new performance metric
    
    Args:
        category: Category of the operation
        operation: Name of the operation
        measured_time: Measured time in seconds
        metadata: Additional metadata about the operation
    """
    with _lock:
        for callback in _metrics_callbacks:
            try:
                callback(category, operation, measured_time, metadata)
            except Exception as e:
                logger.error(f"Error in metric callback {callback.__name__}: {str(e)}")


def get_performance_summary(categories: List[str] = None) -> Dict:
    """
    Generates a summary of performance data with statistics
    
    Args:
        categories: List of categories to include in the summary, or None for all
        
    Returns:
        Performance summary dictionary with statistics
    """
    with _lock:
        summary = {}
        
        # Use all categories if none specified
        if categories is None:
            categories = list(_performance_data.keys())
        
        # Process each category
        for category in categories:
            if category not in _performance_data or not _performance_data[category]:
                continue
            
            # Create TimingStats for this category
            stats = TimingStats()
            
            # Group by operation
            operations = {}
            
            # Add all measurements and group by operation
            for entry in _performance_data[category]:
                # Get the operation name
                operation = entry.get("operation") or entry.get("page_name") or \
                           entry.get("test_name") or entry.get("element_identifier")
                
                # Get the time value
                time_value = entry.get("execution_time") or entry.get("load_time") or \
                            entry.get("interaction_time")
                
                if operation not in operations:
                    operations[operation] = []
                
                # Add to grouped operations
                operations[operation].append(time_value)
                
                # Add to overall stats
                stats.add_measurement(time_value)
            
            # Calculate category statistics
            category_stats = stats.get_statistics()
            
            # Calculate SLA compliance
            sla_compliant = 0
            sla_non_compliant = 0
            
            # Check SLA compliance for each operation
            operation_stats = {}
            for operation, times in operations.items():
                # Calculate operation statistics
                op_stats = TimingStats(times).get_statistics()
                
                # Check SLA compliance
                is_compliant = check_sla_compliance(category, operation, op_stats["mean"])
                
                if is_compliant:
                    sla_compliant += 1
                else:
                    sla_non_compliant += 1
                
                # Add compliance to operation stats
                op_stats["sla_compliant"] = is_compliant
                
                # Store operation stats
                operation_stats[operation] = op_stats
            
            # Calculate compliance percentage
            total_ops = sla_compliant + sla_non_compliant
            compliance_percentage = (sla_compliant / total_ops * 100) if total_ops > 0 else 0
            
            # Add operations and compliance to category stats
            category_stats["operations"] = operation_stats
            category_stats["sla_compliance"] = {
                "compliant": sla_compliant,
                "non_compliant": sla_non_compliant,
                "compliance_percentage": compliance_percentage
            }
            
            # Get top slowest operations
            top_slowest = sorted(operation_stats.items(), 
                               key=lambda x: x[1]["mean"], 
                               reverse=True)[:3]
            
            category_stats["slowest_operations"] = {
                op: stats for op, stats in top_slowest
            }
            
            # Store category stats in summary
            summary[category] = category_stats
        
        return summary


def generate_performance_report(report_name: str = None, report_path: str = None) -> str:
    """
    Generates a detailed performance report and saves it to a file
    
    Args:
        report_name: Name for the report file (default: timestamp-based)
        report_path: Path where the report should be saved (default: DEFAULT_REPORT_PATH)
        
    Returns:
        Path to the generated report file
    """
    with _lock:
        # Generate report summary
        summary = get_performance_summary()
        
        # Create full report with raw data
        report = {
            "summary": summary,
            "raw_data": get_performance_data(),
            "timestamp": datetime.datetime.now().isoformat(),
            "report_name": report_name or f"performance_report_{int(time.time())}",
            "sla_compliance": {}
        }
        
        # Calculate overall SLA compliance
        sla_compliant = 0
        sla_non_compliant = 0
        
        for category, stats in summary.items():
            if "sla_compliance" in stats:
                sla_compliant += stats["sla_compliance"]["compliant"]
                sla_non_compliant += stats["sla_compliance"]["non_compliant"]
        
        total = sla_compliant + sla_non_compliant
        compliance_percentage = (sla_compliant / total * 100) if total > 0 else 0
        
        report["sla_compliance"] = {
            "compliant": sla_compliant,
            "non_compliant": sla_non_compliant,
            "compliance_percentage": compliance_percentage,
            "total_operations": total
        }
        
        # Ensure report directory exists
        report_path = report_path or DEFAULT_REPORT_PATH
        os.makedirs(report_path, exist_ok=True)
        
        # Generate report file name
        if report_name is None:
            report_name = f"performance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif not report_name.endswith('.json'):
            report_name += '.json'
        
        # Full report path
        full_path = os.path.join(report_path, report_name)
        
        # Write report to file
        with open(full_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated performance report: {full_path}")
        
        return full_path


def monitor_performance(category: str, operation_type: str):
    """
    Decorator to monitor the performance of a function
    
    Args:
        category: Category for the performance measurement
        operation_type: Type of operation for SLA compliance checking
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Start timer
            timer_id = start_performance_timer(func.__name__, category)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                return result
            finally:
                # Stop timer and record measurement
                metadata = {
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "operation_type": operation_type
                }
                stop_performance_timer(timer_id, metadata)
        
        return wrapper
    
    return decorator


class PerformanceMonitor:
    """
    Class that provides performance monitoring functionality for the test framework
    """
    
    def __init__(self):
        """
        Initializes a new PerformanceMonitor instance
        """
        self._performance_data = {}
        self._active_timers = {}
        self._metrics_callbacks = []
        self._lock = threading.RLock()
        
        logger.info("Created PerformanceMonitor instance")
    
    def record_page_load_time(self, page_name: str, load_time: float, metadata: Dict = None) -> bool:
        """
        Records page load time for a specific page
        
        Args:
            page_name: Name of the page being loaded
            load_time: Page load time in seconds
            metadata: Additional metadata about the page load
            
        Returns:
            True if successfully recorded, False otherwise
        """
        with self._lock:
            # Initialize category if it doesn't exist
            if "page_load" not in self._performance_data:
                self._performance_data["page_load"] = []
            
            # Create measurement entry
            entry = {
                "page_name": page_name,
                "load_time": load_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to performance data
            self._performance_data["page_load"].append(entry)
            
            logger.debug(f"Recorded page load time for {page_name}: {get_formatted_time(load_time)}")
            
            # Notify callbacks
            self.notify_callbacks("page_load", page_name, load_time, metadata or {})
            
            # Check SLA compliance
            self.check_sla_compliance("page_load", "page_navigation", load_time)
            
            return True
    
    def record_element_interaction_time(self, element_identifier: str, operation: str, 
                                      interaction_time: float, metadata: Dict = None) -> bool:
        """
        Records element interaction time for a specific element operation
        
        Args:
            element_identifier: Identifier for the element (e.g., locator, name)
            operation: Type of operation (e.g., click, input, wait)
            interaction_time: Time taken for the operation in seconds
            metadata: Additional metadata about the interaction
            
        Returns:
            True if successfully recorded, False otherwise
        """
        with self._lock:
            # Initialize category if it doesn't exist
            if "element_interaction" not in self._performance_data:
                self._performance_data["element_interaction"] = []
            
            # Create measurement entry
            entry = {
                "element_identifier": element_identifier,
                "operation": operation,
                "interaction_time": interaction_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to performance data
            self._performance_data["element_interaction"].append(entry)
            
            logger.debug(f"Recorded element interaction time for {element_identifier}.{operation}: {get_formatted_time(interaction_time)}")
            
            # Notify callbacks
            self.notify_callbacks("element_interaction", f"{element_identifier}.{operation}", 
                                interaction_time, metadata or {})
            
            # Check SLA compliance
            self.check_sla_compliance("element_interaction", "element_interaction", interaction_time)
            
            return True
    
    def record_test_execution_time(self, test_name: str, test_type: str, 
                                 execution_time: float, metadata: Dict = None) -> bool:
        """
        Records execution time for a specific test
        
        Args:
            test_name: Name of the test
            test_type: Type of test (e.g., user_registration, story_creation)
            execution_time: Execution time in seconds
            metadata: Additional metadata about the test execution
            
        Returns:
            True if successfully recorded, False otherwise
        """
        with self._lock:
            # Initialize category if it doesn't exist
            if "test_execution" not in self._performance_data:
                self._performance_data["test_execution"] = []
            
            # Create measurement entry
            entry = {
                "test_name": test_name,
                "test_type": test_type,
                "execution_time": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to performance data
            self._performance_data["test_execution"].append(entry)
            
            logger.debug(f"Recorded test execution time for {test_name} ({test_type}): {get_formatted_time(execution_time)}")
            
            # Notify callbacks
            self.notify_callbacks("test_execution", test_name, execution_time, metadata or {})
            
            # Check SLA compliance
            self.check_sla_compliance("test_execution", test_type, execution_time)
            
            return True
    
    def start_timer(self, name: str, category: str) -> str:
        """
        Starts a timer for measuring a specific performance category
        
        Args:
            name: Name of the operation being timed
            category: Category of the operation (page_load, element_interaction, test_execution)
            
        Returns:
            Timer ID that can be used to stop the timer
        """
        with self._lock:
            # Create a timer
            timer = Timer(name=name, category=category)
            timer.start()
            
            # Generate a unique timer ID
            timer_id = f"{category}_{name}_{time.time()}"
            
            # Store the timer
            self._active_timers[timer_id] = timer
            
            logger.debug(f"Started performance timer: {timer_id}")
            
            return timer_id
    
    def stop_timer(self, timer_id: str, metadata: Dict = None) -> float:
        """
        Stops a timer and records its measurement in the appropriate category
        
        Args:
            timer_id: Timer ID returned from start_timer
            metadata: Additional metadata to include with the measurement
            
        Returns:
            Elapsed time in seconds
        """
        with self._lock:
            if timer_id not in self._active_timers:
                logger.warning(f"Timer not found: {timer_id}")
                return -1
            
            # Get the timer
            timer = self._active_timers[timer_id]
            
            # Update metadata if provided
            if metadata:
                timer.add_metadata(metadata)
            
            # Stop the timer and get elapsed time
            elapsed_time = timer.stop(store_result=False)
            
            # Record the measurement based on category
            if timer.category == "page_load":
                self.record_page_load_time(timer.name, elapsed_time, timer.metadata)
            elif timer.category == "element_interaction":
                self.record_element_interaction_time(timer.name, "interaction", elapsed_time, timer.metadata)
            elif timer.category == "test_execution":
                self.record_test_execution_time(timer.name, "general", elapsed_time, timer.metadata)
            else:
                # Generic category
                if timer.category not in self._performance_data:
                    self._performance_data[timer.category] = []
                
                entry = {
                    "operation": timer.name,
                    "execution_time": elapsed_time,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "metadata": timer.metadata
                }
                
                self._performance_data[timer.category].append(entry)
                
                # Notify callbacks
                self.notify_callbacks(timer.category, timer.name, elapsed_time, timer.metadata)
            
            # Remove the timer
            del self._active_timers[timer_id]
            
            logger.debug(f"Stopped performance timer {timer_id}: {get_formatted_time(elapsed_time)}")
            
            return elapsed_time
    
    def get_performance_data(self, category: str = None) -> Dict:
        """
        Retrieves performance data for a specific category or all categories
        
        Args:
            category: Category to retrieve data for, or None for all categories
            
        Returns:
            Performance data dictionary
        """
        with self._lock:
            if category:
                return copy.deepcopy(self._performance_data.get(category, {}))
            else:
                return copy.deepcopy(self._performance_data)
    
    def clear_performance_data(self, category: str = None) -> bool:
        """
        Clears performance data for a specific category or all categories
        
        Args:
            category: Category to clear data for, or None for all categories
            
        Returns:
            True if successfully cleared, False otherwise
        """
        with self._lock:
            if category:
                if category in self._performance_data:
                    self._performance_data[category] = []
                    logger.info(f"Cleared performance data for category: {category}")
                else:
                    logger.warning(f"Category not found: {category}")
                    return False
            else:
                self._performance_data.clear()
                logger.info("Cleared all performance data")
            
            return True
    
    def register_callback(self, callback_function: Callable) -> bool:
        """
        Registers a callback function to be called when new performance metrics are recorded
        
        Args:
            callback_function: Function that takes (category, operation, measured_time, metadata)
            
        Returns:
            True if successfully registered, False otherwise
        """
        with self._lock:
            if not callable(callback_function):
                logger.error(f"Cannot register non-callable as metric callback: {callback_function}")
                return False
            
            if callback_function not in self._metrics_callbacks:
                self._metrics_callbacks.append(callback_function)
                logger.info(f"Registered metric callback: {callback_function.__name__}")
                return True
            
            return False
    
    def unregister_callback(self, callback_function: Callable) -> bool:
        """
        Unregisters a previously registered callback function
        
        Args:
            callback_function: Callback function to unregister
            
        Returns:
            True if successfully unregistered, False otherwise
        """
        with self._lock:
            if callback_function in self._metrics_callbacks:
                self._metrics_callbacks.remove(callback_function)
                logger.info(f"Unregistered metric callback: {callback_function.__name__}")
                return True
            
            return False
    
    def notify_callbacks(self, category: str, operation: str, measured_time: float, metadata: Dict) -> None:
        """
        Notifies all registered callbacks about a new performance metric
        
        Args:
            category: Category of the operation
            operation: Name of the operation
            measured_time: Measured time in seconds
            metadata: Additional metadata about the operation
        """
        with self._lock:
            for callback in self._metrics_callbacks:
                try:
                    callback(category, operation, measured_time, metadata)
                except Exception as e:
                    logger.error(f"Error in metric callback {callback.__name__}: {str(e)}")
    
    def get_performance_summary(self, categories: List[str] = None) -> Dict:
        """
        Generates a summary of performance data with statistics
        
        Args:
            categories: List of categories to include in the summary, or None for all
            
        Returns:
            Performance summary dictionary with statistics
        """
        with self._lock:
            summary = {}
            
            # Use all categories if none specified
            if categories is None:
                categories = list(self._performance_data.keys())
            
            # Process each category
            for category in categories:
                if category not in self._performance_data or not self._performance_data[category]:
                    continue
                
                # Create TimingStats for this category
                stats = TimingStats()
                
                # Group by operation
                operations = {}
                
                # Add all measurements and group by operation
                for entry in self._performance_data[category]:
                    # Get the operation name
                    operation = entry.get("operation") or entry.get("page_name") or \
                               entry.get("test_name") or entry.get("element_identifier")
                    
                    # Get the time value
                    time_value = entry.get("execution_time") or entry.get("load_time") or \
                                entry.get("interaction_time")
                    
                    if operation not in operations:
                        operations[operation] = []
                    
                    # Add to grouped operations
                    operations[operation].append(time_value)
                    
                    # Add to overall stats
                    stats.add_measurement(time_value)
                
                # Calculate category statistics
                category_stats = stats.get_statistics()
                
                # Calculate SLA compliance
                sla_compliant = 0
                sla_non_compliant = 0
                
                # Check SLA compliance for each operation
                operation_stats = {}
                for operation, times in operations.items():
                    # Calculate operation statistics
                    op_stats = TimingStats(times).get_statistics()
                    
                    # Check SLA compliance
                    is_compliant = self.check_sla_compliance(category, operation, op_stats["mean"])
                    
                    if is_compliant:
                        sla_compliant += 1
                    else:
                        sla_non_compliant += 1
                    
                    # Add compliance to operation stats
                    op_stats["sla_compliant"] = is_compliant
                    
                    # Store operation stats
                    operation_stats[operation] = op_stats
                
                # Calculate compliance percentage
                total_ops = sla_compliant + sla_non_compliant
                compliance_percentage = (sla_compliant / total_ops * 100) if total_ops > 0 else 0
                
                # Add operations and compliance to category stats
                category_stats["operations"] = operation_stats
                category_stats["sla_compliance"] = {
                    "compliant": sla_compliant,
                    "non_compliant": sla_non_compliant,
                    "compliance_percentage": compliance_percentage
                }
                
                # Get top slowest operations
                top_slowest = sorted(operation_stats.items(), 
                                   key=lambda x: x[1]["mean"], 
                                   reverse=True)[:3]
                
                category_stats["slowest_operations"] = {
                    op: stats for op, stats in top_slowest
                }
                
                # Store category stats in summary
                summary[category] = category_stats
            
            return summary
    
    def generate_report(self, report_name: str = None, report_path: str = None) -> str:
        """
        Generates a detailed performance report and saves it to a file
        
        Args:
            report_name: Name for the report file (default: timestamp-based)
            report_path: Path where the report should be saved (default: DEFAULT_REPORT_PATH)
            
        Returns:
            Path to the generated report file
        """
        with self._lock:
            # Generate report summary
            summary = self.get_performance_summary()
            
            # Create full report with raw data
            report = {
                "summary": summary,
                "raw_data": self.get_performance_data(),
                "timestamp": datetime.datetime.now().isoformat(),
                "report_name": report_name or f"performance_report_{int(time.time())}",
                "sla_compliance": {}
            }
            
            # Calculate overall SLA compliance
            sla_compliant = 0
            sla_non_compliant = 0
            
            for category, stats in summary.items():
                if "sla_compliance" in stats:
                    sla_compliant += stats["sla_compliance"]["compliant"]
                    sla_non_compliant += stats["sla_compliance"]["non_compliant"]
            
            total = sla_compliant + sla_non_compliant
            compliance_percentage = (sla_compliant / total * 100) if total > 0 else 0
            
            report["sla_compliance"] = {
                "compliant": sla_compliant,
                "non_compliant": sla_non_compliant,
                "compliance_percentage": compliance_percentage,
                "total_operations": total
            }
            
            # Ensure report directory exists
            report_path = report_path or DEFAULT_REPORT_PATH
            os.makedirs(report_path, exist_ok=True)
            
            # Generate report file name
            if report_name is None:
                report_name = f"performance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif not report_name.endswith('.json'):
                report_name += '.json'
            
            # Full report path
            full_path = os.path.join(report_path, report_name)
            
            # Write report to file
            with open(full_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Generated performance report: {full_path}")
            
            return full_path
    
    def check_sla_compliance(self, category: str, operation_type: str, measured_time: float) -> bool:
        """
        Checks if a measured time complies with the relevant SLA
        
        Args:
            category: Category of the operation (page_load, element_interaction, test_execution)
            operation_type: Type of operation or test
            measured_time: Measured time in seconds
            
        Returns:
            True if within SLA, False otherwise
        """
        is_compliant = False
        
        # Determine which SLA checker to use based on category
        if category in ["page_load", "element_interaction"]:
            is_compliant = is_within_operation_sla(operation_type, measured_time)
        elif category == "test_execution":
            if operation_type in TEST_TYPE_SLAS:
                max_duration = TEST_TYPE_SLAS[operation_type].get("maximum_duration")
                is_compliant = measured_time <= max_duration
            else:
                # Default to within_sla if test_type not found
                is_compliant = is_within_sla(measured_time, "test_execution", operation_type)
        
        # Log the result
        if is_compliant:
            logger.debug(f"SLA compliance: {category}.{operation_type} - {get_formatted_time(measured_time)} - PASS")
        else:
            logger.warning(f"SLA compliance: {category}.{operation_type} - {get_formatted_time(measured_time)} - FAIL")
        
        return is_compliant


class PerformanceContext:
    """
    Context manager for monitoring performance of a code block
    """
    
    def __init__(self, name: str, category: str, operation_type: str = None, metadata: Dict = None):
        """
        Initializes a new PerformanceContext instance
        
        Args:
            name: Name of the operation being monitored
            category: Category of the operation (page_load, element_interaction, test_execution)
            operation_type: Type of operation for SLA compliance checking
            metadata: Additional metadata about the operation
        """
        self.name = name
        self.category = category
        self.operation_type = operation_type or category
        self.metadata = metadata or {}
        self.timer_id = None
    
    def __enter__(self):
        """
        Starts performance monitoring when entering the context
        
        Returns:
            Self reference for use in the with statement
        """
        self.timer_id = start_performance_timer(self.name, self.category)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stops performance monitoring when exiting the context
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        # Add exception info to metadata if an exception occurred
        if exc_type is not None:
            self.metadata["exception_type"] = exc_type.__name__
            self.metadata["exception_message"] = str(exc_val)
        
        # Stop the timer and record the measurement
        stop_performance_timer(self.timer_id, self.metadata)