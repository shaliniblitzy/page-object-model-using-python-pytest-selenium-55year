"""
Utility module that generates, manages, and customizes test reports for the Storydoc automation framework.
It provides functions to create HTML reports, add screenshots, logs, and performance data to test reports,
and customize report formatting.
"""

import os
import datetime
import pytest
import json
import shutil
from typing import List, Dict, Any, Optional, Union
from jinja2 import Environment, FileSystemLoader

# Internal imports
from ..utilities.config_manager import get_config
from ..utilities.screenshot_manager import ScreenshotManager
from ..utilities.logger import get_logger
from ..utilities.timing_helper import get_formatted_time, get_timestamp
from ..utilities.performance_monitor import get_performance_summary
from ..config.reporting_config import REPORT_DIR, SCREENSHOT_DIR, LOG_DIR, ReportingConfig

# Set up logger
logger = get_logger(__name__)

# Default report template
DEFAULT_REPORT_TEMPLATE = "report_template.html"

# Initialize configuration and screenshot manager
_reporting_config = ReportingConfig()
_screenshot_manager = ScreenshotManager()

# Store report metadata
_report_metadata = {}


def configure_html_reporter(config_options: Dict = None) -> Dict:
    """
    Configures the pytest-html reporter with custom settings
    
    Args:
        config_options: Custom configuration options
        
    Returns:
        Updated reporter configuration
    """
    # Ensure reporting directories exist
    _reporting_config.ensure_directories_exist()
    
    # Get default options
    html_options = dict(_reporting_config.html_report_options)
    
    # Update with custom options if provided
    if config_options:
        html_options.update(config_options)
    
    # Set HTML report path if not already specified
    if 'report_path' not in html_options:
        report_prefix = html_options.get('report_name', 'test_report')
        html_options['report_path'] = _reporting_config.get_html_report_path(report_prefix)
    
    logger.info(f"HTML reporter configured with options: {html_options}")
    
    return html_options


def add_screenshot_to_report(screenshot_path: str, description: str = "Screenshot") -> Dict:
    """
    Adds a screenshot to the HTML report as extra content
    
    Args:
        screenshot_path: Path to the screenshot file
        description: Description of the screenshot
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Validate that screenshot_path exists
    if not os.path.exists(screenshot_path):
        logger.error(f"Screenshot not found: {screenshot_path}")
        return {}
    
    # Create a relative path for the HTML report
    rel_path = os.path.relpath(screenshot_path, REPORT_DIR)
    
    # Create extra content dictionary
    extra = {
        "name": description,
        "content": f'<div class="image"><img src="{rel_path}"></div>',
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added screenshot to report: {description}")
    
    return extra


def add_html_to_report(html_content: str, title: str = "HTML Content") -> Dict:
    """
    Adds custom HTML content to the test report
    
    Args:
        html_content: HTML content to add
        title: Title for the content
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Validate that html_content is not empty
    if not html_content:
        logger.error("Cannot add empty HTML content to report")
        return {}
    
    # Create extra content dictionary
    extra = {
        "name": title,
        "content": html_content,
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added HTML content to report: {title}")
    
    return extra


def add_table_to_report(headers: List[str], rows: List[List[Any]], title: str = "Data Table") -> Dict:
    """
    Adds a data table to the test report
    
    Args:
        headers: List of column headers
        rows: List of row data (each row is a list of values)
        title: Title for the table
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Validate headers and rows are not empty
    if not headers or not rows:
        logger.error("Cannot add empty table to report")
        return {}
    
    # Generate HTML table
    table_html = format_html_table(headers, rows, "data-table")
    
    # Create extra content dictionary
    extra = {
        "name": title,
        "content": table_html,
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added table to report: {title}")
    
    return extra


def add_json_to_report(json_data: Dict, title: str = "JSON Data") -> Dict:
    """
    Adds JSON data to the test report in a formatted way
    
    Args:
        json_data: JSON data to add
        title: Title for the data
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Validate that json_data is not empty
    if not json_data:
        logger.error("Cannot add empty JSON data to report")
        return {}
    
    # Format JSON data for readability
    formatted_json = json.dumps(json_data, indent=2)
    
    # Wrap in pre tag with styling
    html_content = f'<pre style="white-space: pre-wrap; word-wrap: break-word;">{formatted_json}</pre>'
    
    # Create extra content dictionary
    extra = {
        "name": title,
        "content": html_content,
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added JSON data to report: {title}")
    
    return extra


def add_log_to_report(log_file_path: str, title: str = "Log Content", include_full_log: bool = False) -> Dict:
    """
    Adds log content to the test report
    
    Args:
        log_file_path: Path to the log file
        title: Title for the log content
        include_full_log: Whether to include the full log or just extract relevant portions
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Validate that log_file_path exists
    if not os.path.exists(log_file_path):
        logger.error(f"Log file not found: {log_file_path}")
        return {}
    
    # Read log file content
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    
    # Extract relevant portions if not include_full_log
    if not include_full_log:
        # This could be implemented to filter for specific log patterns
        # For now, we'll just include everything
        pass
    
    # Format log content in a pre tag with styling
    html_content = f'<pre style="white-space: pre-wrap; word-wrap: break-word; max-height: 500px; overflow-y: auto;">{log_content}</pre>'
    
    # Create extra content dictionary
    extra = {
        "name": title,
        "content": html_content,
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added log content to report: {title}")
    
    return extra


def add_performance_data_to_report(categories: List[str] = None, title: str = "Performance Data") -> Dict:
    """
    Adds performance data to the test report
    
    Args:
        categories: List of performance categories to include
        title: Title for the performance data
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Get performance summary
    perf_summary = get_performance_summary(categories)
    
    # Format as HTML
    html_content = '<div class="performance-data">'
    
    for category, stats in perf_summary.items():
        html_content += f'<h3>{category.title()}</h3>'
        
        # Overall statistics
        stats_html = f"""
        <div class="performance-stats">
            <p>Count: {stats.get('count', 0)}</p>
            <p>Average: {get_formatted_time(stats.get('mean', 0))}</p>
            <p>Min: {get_formatted_time(stats.get('min', 0))}</p>
            <p>Max: {get_formatted_time(stats.get('max', 0))}</p>
        </div>
        """
        html_content += stats_html
        
        # Operations table if available
        if 'operations' in stats:
            headers = ['Operation', 'Count', 'Average', 'Min', 'Max', 'SLA Compliant']
            rows = []
            
            for op_name, op_stats in stats['operations'].items():
                sla_status = '✅' if op_stats.get('sla_compliant', True) else '❌'
                rows.append([
                    op_name,
                    op_stats.get('count', 0),
                    get_formatted_time(op_stats.get('avg_time', 0)),
                    get_formatted_time(op_stats.get('min_time', 0)),
                    get_formatted_time(op_stats.get('max_time', 0)),
                    sla_status
                ])
            
            html_content += format_html_table(headers, rows, "performance-table")
    
    html_content += '</div>'
    
    # Create extra content dictionary
    extra = {
        "name": title,
        "content": html_content,
        "mime_type": "text/html",
        "extension": "html"
    }
    
    logger.info(f"Added performance data to report: {title}")
    
    return extra


def set_report_metadata(key: str, value: str) -> None:
    """
    Sets metadata for the test report such as environment info, browser version, etc.
    
    Args:
        key: Metadata key
        value: Metadata value
    """
    global _report_metadata
    _report_metadata[key] = value
    logger.debug(f"Set report metadata: {key}={value}")


def get_report_metadata(key: str = None) -> Union[Dict, str, None]:
    """
    Gets all metadata or a specific metadata value for the test report
    
    Args:
        key: Metadata key to retrieve, or None for all metadata
        
    Returns:
        Metadata dictionary or specific value
    """
    global _report_metadata
    
    if key is not None:
        return _report_metadata.get(key)
    
    return _report_metadata


def generate_summary_report(report_name: str = None, report_path: str = None, test_results: Dict = None) -> str:
    """
    Generates a summary report with test results, performance data, and metadata
    
    Args:
        report_name: Name for the report file
        report_path: Path to save the report
        test_results: Test execution results
        
    Returns:
        Path to the generated report file
    """
    # Ensure reporting directories exist
    _reporting_config.ensure_directories_exist()
    
    # Use default path if not provided
    if report_path is None:
        report_path = REPORT_DIR
    
    # Generate report name with timestamp if not provided
    if report_name is None:
        timestamp = get_timestamp("%Y%m%d_%H%M%S")
        report_name = f"test_summary_{timestamp}.html"
    elif not report_name.endswith('.html'):
        report_name += '.html'
    
    # Full report path
    report_file = os.path.join(report_path, report_name)
    
    # Test results, using empty dict if not provided
    results = test_results or {}
    
    # Get performance data
    performance_data = get_performance_summary()
    
    # Prepare report context
    context = {
        'title': _reporting_config.html_report_options.get('title', 'Test Report'),
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'results': results,
        'performance': performance_data,
        'metadata': _report_metadata,
        'summary': generate_test_report_summary(results)
    }
    
    # Load template
    template_path = os.path.dirname(os.path.abspath(__file__))
    template_file = DEFAULT_REPORT_TEMPLATE
    
    try:
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(template_file)
    except Exception as e:
        # Fallback to a simple template if the file can't be loaded
        logger.error(f"Failed to load template {template_file}: {e}")
        html_content = f"""
        <html>
        <head><title>{context['title']}</title></head>
        <body>
            <h1>{context['title']}</h1>
            <p>Generated: {context['timestamp']}</p>
            <h2>Test Summary</h2>
            <pre>{context['summary']}</pre>
            <h2>Metadata</h2>
            <pre>{json.dumps(context['metadata'], indent=2)}</pre>
        </body>
        </html>
        """
    else:
        # Render template with context
        html_content = template.render(**context)
    
    # Write report to file
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Generated summary report: {report_file}")
    
    return report_file


def capture_and_add_screenshot(driver, name: str = None, description: str = "Screenshot") -> Dict:
    """
    Captures a screenshot and adds it to the test report
    
    Args:
        driver: WebDriver instance
        name: Name for the screenshot file
        description: Description for the screenshot
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Capture screenshot
    screenshot_path = _screenshot_manager.capture_screenshot(driver, name)
    
    # Add to report
    if screenshot_path:
        return add_screenshot_to_report(screenshot_path, description)
    
    return {}


def capture_and_add_failure_screenshot(driver, test_name: str, error_message: str = None) -> Dict:
    """
    Captures a screenshot for a test failure and adds it to the report
    
    Args:
        driver: WebDriver instance
        test_name: Name of the test that failed
        error_message: Error message for context
        
    Returns:
        Extra content dictionary for pytest-html
    """
    # Capture failure screenshot
    screenshot_path = _screenshot_manager.capture_failure_screenshot(driver, test_name, error_message)
    
    # Add to report
    if screenshot_path:
        description = f"Failure in {test_name}"
        if error_message:
            description += f": {error_message}"
        
        return add_screenshot_to_report(screenshot_path, description)
    
    return {}


def generate_test_report_summary(test_results: Dict) -> str:
    """
    Generates a text summary of test execution results
    
    Args:
        test_results: Test execution results
        
    Returns:
        Formatted test summary text
    """
    # Extract test counts
    total = test_results.get('total', 0)
    passed = test_results.get('passed', 0)
    failed = test_results.get('failed', 0)
    skipped = test_results.get('skipped', 0)
    errors = test_results.get('errors', 0)
    
    # Calculate pass rate
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Format duration
    duration = test_results.get('duration', 0)
    formatted_duration = get_formatted_time(duration)
    
    # Build summary string
    summary = f"""
    Test Execution Summary
    ---------------------
    Total Tests: {total}
    Passed: {passed}
    Failed: {failed}
    Skipped: {skipped}
    Errors: {errors}
    Pass Rate: {pass_rate:.2f}%
    Duration: {formatted_duration}
    """
    
    return summary


def format_html_table(headers: List[str], rows: List[List[Any]], table_class: str = "") -> str:
    """
    Formats data as an HTML table
    
    Args:
        headers: List of column headers
        rows: List of row data (each row is a list of values)
        table_class: CSS class for the table
        
    Returns:
        HTML table string
    """
    # Table header
    html = f'<table class="{table_class}">\n<thead>\n<tr>'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr>\n</thead>\n<tbody>'
    
    # Table rows
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    
    html += '</tbody>\n</table>'
    
    return html


def customize_report_style(css_content: str) -> bool:
    """
    Customizes the style of HTML reports with CSS
    
    Args:
        css_content: CSS content to apply
        
    Returns:
        True if successful, False otherwise
    """
    # Validate that css_content is not empty
    if not css_content:
        logger.error("Cannot apply empty CSS content")
        return False
    
    try:
        # Create style file
        style_file = os.path.join(REPORT_DIR, "custom_style.css")
        
        # Write CSS content to file
        with open(style_file, 'w') as f:
            f.write(css_content)
        
        # Set custom style in configuration
        set_config_value = getattr(get_config, 'set', None)
        if callable(set_config_value):
            set_config_value('pytest_html_css', style_file)
        
        logger.info(f"Customized report style with CSS file: {style_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to customize report style: {str(e)}")
        return False


class ReportingHelper:
    """Helper class that provides methods for test report generation and customization"""
    
    def __init__(self, report_path: str = None):
        """
        Initializes the ReportingHelper with configuration
        
        Args:
            report_path: Path for storing reports
        """
        self.config = _reporting_config
        self.screenshot_manager = _screenshot_manager
        self.metadata = {}
        self.report_path = report_path or REPORT_DIR
        
        # Ensure reporting directories exist
        self.config.ensure_directories_exist()
        
        logger.info(f"Initialized ReportingHelper with report path: {self.report_path}")
    
    def configure_html_reporter(self, config_options: Dict = None) -> Dict:
        """
        Configures the pytest-html reporter with custom settings
        
        Args:
            config_options: Custom configuration options
            
        Returns:
            Updated reporter configuration
        """
        # Get default options
        html_options = dict(self.config.html_report_options)
        
        # Update with custom options if provided
        if config_options:
            html_options.update(config_options)
        
        # Set HTML report path based on report_path property
        report_prefix = html_options.get('report_name', 'test_report')
        html_options['report_path'] = os.path.join(self.report_path, f"{report_prefix}.html")
        
        logger.info(f"HTML reporter configured with options: {html_options}")
        
        return html_options
    
    def add_screenshot(self, screenshot_path: str, description: str = "Screenshot") -> Dict:
        """
        Adds a screenshot to the HTML report as extra content
        
        Args:
            screenshot_path: Path to the screenshot file
            description: Description of the screenshot
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_screenshot_to_report(screenshot_path, description)
    
    def capture_screenshot(self, driver, name: str = None, description: str = "Screenshot") -> Dict:
        """
        Captures a screenshot and adds it to the test report
        
        Args:
            driver: WebDriver instance
            name: Name for the screenshot file
            description: Description for the screenshot
            
        Returns:
            Extra content dictionary for pytest-html
        """
        screenshot_path = self.screenshot_manager.capture_screenshot(driver, name)
        return self.add_screenshot(screenshot_path, description)
    
    def capture_failure_screenshot(self, driver, test_name: str, error_message: str = None) -> Dict:
        """
        Captures a screenshot for a test failure and adds it to the report
        
        Args:
            driver: WebDriver instance
            test_name: Name of the test that failed
            error_message: Error message for context
            
        Returns:
            Extra content dictionary for pytest-html
        """
        screenshot_path = self.screenshot_manager.capture_failure_screenshot(driver, test_name, error_message)
        description = f"Failure in {test_name}"
        if error_message:
            description += f": {error_message}"
        return self.add_screenshot(screenshot_path, description)
    
    def add_html_content(self, html_content: str, title: str = "HTML Content") -> Dict:
        """
        Adds custom HTML content to the test report
        
        Args:
            html_content: HTML content to add
            title: Title for the content
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_html_to_report(html_content, title)
    
    def add_table(self, headers: List[str], rows: List[List[Any]], title: str = "Data Table") -> Dict:
        """
        Adds a data table to the test report
        
        Args:
            headers: List of column headers
            rows: List of row data (each row is a list of values)
            title: Title for the table
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_table_to_report(headers, rows, title)
    
    def add_json_data(self, json_data: Dict, title: str = "JSON Data") -> Dict:
        """
        Adds JSON data to the test report in a formatted way
        
        Args:
            json_data: JSON data to add
            title: Title for the data
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_json_to_report(json_data, title)
    
    def add_log_content(self, log_file_path: str, title: str = "Log Content", include_full_log: bool = False) -> Dict:
        """
        Adds log content to the test report
        
        Args:
            log_file_path: Path to the log file
            title: Title for the log content
            include_full_log: Whether to include the full log or just extract relevant portions
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_log_to_report(log_file_path, title, include_full_log)
    
    def add_performance_data(self, categories: List[str] = None, title: str = "Performance Data") -> Dict:
        """
        Adds performance data to the test report
        
        Args:
            categories: List of performance categories to include
            title: Title for the performance data
            
        Returns:
            Extra content dictionary for pytest-html
        """
        return add_performance_data_to_report(categories, title)
    
    def set_metadata(self, key: str, value: str) -> None:
        """
        Sets metadata for the test report
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        logger.debug(f"Set report metadata: {key}={value}")
    
    def get_metadata(self, key: str = None) -> Union[Dict, str, None]:
        """
        Gets metadata for the test report
        
        Args:
            key: Metadata key to retrieve, or None for all metadata
            
        Returns:
            Metadata dictionary or specific value
        """
        if key is not None:
            return self.metadata.get(key)
        
        return self.metadata.copy()
    
    def generate_summary_report(self, report_name: str = None, test_results: Dict = None) -> str:
        """
        Generates a summary report with test results and metadata
        
        Args:
            report_name: Name for the report file
            test_results: Test execution results
            
        Returns:
            Path to the generated report file
        """
        return generate_summary_report(report_name, self.report_path, test_results)
    
    def customize_style(self, css_content: str) -> bool:
        """
        Customizes the style of HTML reports with CSS
        
        Args:
            css_content: CSS content to apply
            
        Returns:
            True if successful, False otherwise
        """
        return customize_report_style(css_content)
    
    def generate_test_summary(self, test_results: Dict) -> str:
        """
        Generates a text summary of test execution results
        
        Args:
            test_results: Test execution results
            
        Returns:
            Formatted test summary text
        """
        return generate_test_report_summary(test_results)


class HTMLReportExtension:
    """Class that provides pytest hooks for extending HTML reports"""
    
    def __init__(self):
        """Initializes the HTMLReportExtension"""
        self.reporting_helper = ReportingHelper()
        logger.info("Initialized HTMLReportExtension")
    
    def pytest_configure(self, config):
        """
        Hook that runs when pytest is being configured
        
        Args:
            config: pytest configuration object
        """
        html_options = self.reporting_helper.configure_html_reporter()
        
        # Configure HTML plugin if installed
        if hasattr(config, 'option') and hasattr(config.option, 'htmlpath'):
            config.option.htmlpath = html_options.get('report_path')
        
        # Add pytest-html metadata
        for key, value in self.reporting_helper.metadata.items():
            config._metadata[key] = value
        
        logger.info("Configured pytest-html plugin")
    
    def pytest_html_report_title(self, report_title):
        """
        Hook that sets the HTML report title
        
        Args:
            report_title: Default report title
            
        Returns:
            Custom report title
        """
        custom_title = self.reporting_helper.config.html_report_options.get('title', 'Storydoc Test Report')
        return custom_title
    
    def pytest_html_results_table_header(self, cells):
        """
        Hook that customizes the HTML results table header
        
        Args:
            cells: Header cells to modify
        """
        # Add custom header cells
        cells.insert(2, '<th>Time</th>')
        cells.insert(3, '<th>Performance</th>')
        
        logger.debug("Customized HTML results table header")
    
    def pytest_html_results_table_row(self, report, cells):
        """
        Hook that customizes the HTML results table rows
        
        Args:
            report: Test report object
            cells: Row cells to modify
        """
        # Add custom cells to match custom headers
        cells.insert(2, f'<td>{getattr(report, "duration", 0):.2f}s</td>')
        
        # Add performance data if available
        performance_data = getattr(report, "performance", "")
        cells.insert(3, f'<td>{performance_data}</td>')
        
        # Add styling based on outcome
        if report.outcome == 'passed':
            cells[1] = cells[1].replace('passed', 'passed" style="background-color: #dfd')
        elif report.outcome == 'failed':
            cells[1] = cells[1].replace('failed', 'failed" style="background-color: #fdd')
        elif report.outcome == 'skipped':
            cells[1] = cells[1].replace('skipped', 'skipped" style="background-color: #eee')
    
    def pytest_html_results_summary(self, prefix, summary, postfix):
        """
        Hook that adds extra summary information to the HTML report
        
        Args:
            prefix: HTML to insert before the summary table
            summary: The summary data
            postfix: HTML to insert after the summary table
        """
        # Add performance summary
        perf_summary = get_performance_summary()
        if perf_summary:
            perf_html = '<h2>Performance Summary</h2>'
            
            for category, stats in perf_summary.items():
                perf_html += f'<h3>{category.title()}</h3>'
                perf_html += '<p>'
                perf_html += f'Average: {get_formatted_time(stats.get("mean", 0))}, '
                perf_html += f'Min: {get_formatted_time(stats.get("min", 0))}, '
                perf_html += f'Max: {get_formatted_time(stats.get("max", 0))}'
                perf_html += '</p>'
            
            prefix.append(perf_html)
        
        # Add environment information
        env_html = '<h2>Environment</h2>'
        env_html += '<table>'
        
        for key, value in self.reporting_helper.metadata.items():
            env_html += f'<tr><td>{key}</td><td>{value}</td></tr>'
        
        env_html += '</table>'
        prefix.append(env_html)
        
        logger.info("Added custom summary information to HTML report")