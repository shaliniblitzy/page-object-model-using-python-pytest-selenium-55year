# Performance Testing Documentation

## Introduction

This document provides an overview of the performance testing capabilities within the Storydoc test automation framework. The framework includes comprehensive tools and utilities for measuring, validating, and reporting on the performance aspects of the Storydoc application to ensure compliance with defined Service Level Agreements (SLAs).

Performance testing is a critical component of the overall quality assurance strategy, ensuring that the Storydoc application meets user expectations for responsiveness and reliability. The framework's performance testing capabilities focus on measuring key user interactions and validating them against defined SLA thresholds.

## Performance Requirements

The Storydoc application is subject to specific performance requirements across different user workflows. These requirements are defined as Service Level Agreements (SLAs) and serve as the foundation for performance testing efforts.

### Core Performance SLAs

| Operation | Target Response Time | Timeout | Description |
|-----------|----------------------|---------|-------------|
| Page Navigation | 5 seconds | 10 seconds | Maximum time for page loading |
| Element Interaction | 2 seconds | 5 seconds | Maximum time for element interaction |
| Form Submission | 3 seconds | 10 seconds | Maximum time for form submission |
| Email Delivery | 30 seconds | 60 seconds | Maximum time for email delivery |

### Workflow Performance SLAs

| Test Type | Maximum Duration | Success Rate | Description |
|-----------|------------------|--------------|-------------|
| User Registration | 30 seconds | 98% | End-to-end registration flow |
| User Authentication | 20 seconds | 99% | Sign-in process |
| Story Creation | 45 seconds | 95% | Creating a new story |
| Story Sharing | 60 seconds | 95% | Sharing a story with verification |
| Full Workflow | 180 seconds | 90% | Complete end-to-end workflow |

## Performance Metrics

The framework tracks the following key performance metrics:

### Page Load Time
Measures the time taken to load pages within the application, from initiation of navigation to full page readiness. 

```python
# Example of measuring page load time
def test_signup_page_load_time(self, signup_page):
    load_time = measure_page_load_time(signup_page, "signup_page")
    assert_page_load_time_within_sla("signup_page", load_time)
```

### Element Response Time
Measures the time taken for UI elements to respond to user interactions such as clicks, text input, and selection.

```python
# Example of measuring element response time
def test_button_click_response_time(self, signin_page, performance_timer):
    performance_timer.start()
    signin_page.click_signin_button()
    click_time = performance_timer.stop()
    assert_interaction_time_within_sla("Signin Button", "click", click_time)
```

### Test Execution Time
Measures the duration of test execution for specific user flows, ensuring they complete within the defined SLA thresholds.

```python
# Example of measuring test execution time
@pytest.fixture(scope='function', autouse=True)
def test_execution_timer(request, performance_monitor):
    start_time = time.time()
    yield
    end_time = time.time()
    execution_time = end_time - start_time
    performance_monitor.record_test_execution_time(
        test_name=request.node.name,
        test_type=determine_test_type(request.node),
        execution_time=execution_time
    )
```

## SLA Definitions

SLA definitions are stored in a machine-readable format in the `performance_thresholds.json` file. These definitions include:

1. **Operations SLAs** - Thresholds for individual operations like page navigation and element interaction
2. **Test Type SLAs** - Thresholds for complete test workflows like user registration and story creation
3. **Alert Thresholds** - Values that trigger warnings or critical alerts when exceeded

The SLA configuration is accessible through the `sla_config.py` module, which provides helper functions:

```python
# Example of SLA validation
def is_within_operation_sla(operation_type, duration):
    sla_config = get_operation_sla(operation_type)
    return duration <= sla_config["target_response_time"]

def is_within_test_type_sla(test_type, duration):
    sla_config = get_test_type_sla(test_type)
    return duration <= sla_config["maximum_duration"]
```

## Performance Test Types

The framework includes several types of performance tests:

### Page Load Time Tests
These tests measure how long it takes for different pages in the application to load completely. They validate that the load times meet the specified SLA requirements.

Location: `src/test/tests/performance/test_page_load_time.py`

### Response Time Tests
These tests measure the responsiveness of various UI interactions, such as button clicks, form submissions, and data input. They ensure that the application's UI is responsive and meets user expectations.

Location: `src/test/tests/performance/test_response_time.py`

### SLA Compliance Tests
These tests specifically validate that all performance aspects of the application comply with the defined SLAs. They serve as a comprehensive check on performance requirements.

Location: `src/test/tests/performance/test_sla_compliance.py`

## Running Performance Tests

The framework provides dedicated scripts for running performance tests on different platforms:

### On Linux/macOS

```bash
# Run all performance tests
./src/test/scripts/run_performance_tests.sh --all

# Run specific test types
./src/test/scripts/run_performance_tests.sh --page-load --response-time

# Additional options
./src/test/scripts/run_performance_tests.sh --headless --verbose
```

### On Windows

```batch
# Run all performance tests
src\test\scripts\run_performance_tests.bat --all

# Run specific test types
src\test\scripts\run_performance_tests.bat --page-load true --response-time true

# Additional options
src\test\scripts\run_performance_tests.bat --headless true --verbose
```

### Running via pytest

You can also run performance tests directly using pytest:

```bash
# Run all performance tests
pytest src/test/tests/performance/

# Run specific test file
pytest src/test/tests/performance/test_page_load_time.py

# Run with HTML report
pytest src/test/tests/performance/ --html=reports/performance_report.html
```

## Monitoring and Alerting

The framework includes built-in monitoring and alerting capabilities to help identify performance issues:

### Performance Monitoring

The `PerformanceMonitor` class collects and analyzes performance metrics throughout test execution:

```python
# Example of using the performance monitor
performance_monitor = PerformanceMonitor()
performance_monitor.record_page_load_time("dashboard_page", 2.5)
performance_monitor.record_element_interaction_time("submit_button", "click", 0.75)
```

### Alert Thresholds

Alert thresholds are defined in the `performance_thresholds.json` file:

| Metric | Warning Threshold | Critical Threshold | Action |
|--------|-------------------|-------------------|--------|
| Test Pass Rate | < 90% | < 80% | Notify team, investigate failures |
| Test Duration | > 120% of baseline | > 150% of baseline | Investigate performance issues |
| Element Wait Time | > 5 seconds | > 10 seconds | Check application performance |
| Resource Usage | > 80% CPU/Memory | > 90% CPU/Memory | Optimize resource usage |

### Performance Reports

The framework generates comprehensive performance reports after test execution:

```python
# Generate a performance report
report_path = performance_monitor.generate_report(report_name="performance_summary")
```

These reports include:
- Summary statistics for each performance category
- Individual operation measurements
- SLA compliance analysis
- Slowest operations identification

## Performance Test Implementation

When implementing new performance tests, follow these guidelines:

### 1. Using Performance Fixtures

The framework provides several pytest fixtures for performance testing:

```python
# Example performance test using fixtures
def test_story_creation_performance(self, performance_monitor, performance_timer):
    # Measure individual operation
    performance_timer.start()
    story_editor_page.enter_story_title("Test Story")
    title_input_time = performance_timer.stop()
    
    # Record and validate
    assert_interaction_time_within_sla("Story Title", "input", title_input_time)
```

### 2. Using Timing Context

For more fine-grained control, use the `TimingContext` context manager:

```python
# Example using TimingContext
with TimingContext("create_story_workflow", "story_creation"):
    dashboard_page.click_create_story_button()
    story_editor_page.enter_story_title("Performance Test Story")
    story_editor_page.select_template("Basic")
    story_editor_page.save_story()
```

### 3. Selecting Appropriate SLAs

Always validate performance against the appropriate SLA:

```python
# Example of SLA validation
def test_signup_form_submission_time(self, signup_page, performance_timer):
    # Perform operation
    performance_timer.start()
    signup_page.click_signup_button()
    submission_time = performance_timer.stop()
    
    # Validate against form_submission SLA
    is_compliant = is_within_operation_sla("form_submission", submission_time)
    assert is_compliant, f"Signup form submission time exceeds SLA threshold"
```

## Result Interpretation

Performance test results should be interpreted in the context of the defined SLAs:

### HTML Reports

The framework generates HTML reports that include:
- Pass/fail summary for all tests
- Detailed timing information for each operation
- Highlighted SLA violations
- Performance trends over time

### Performance Summary

The `get_performance_summary()` function provides a detailed analysis of performance metrics:

```python
summary = performance_monitor.get_performance_summary()
# Summary includes:
# - Mean, median, min, max for each category
# - SLA compliance statistics
# - Slowest operations identification
```

### Identifying Performance Issues

When reviewing performance results, look for:
1. Operations consistently near or exceeding SLA thresholds
2. Unexpected performance degradation compared to previous runs
3. Patterns of performance issues at specific times or under specific conditions

## Troubleshooting

### Common Performance Issues

| Issue | Possible Causes | Resolution |
|-------|----------------|------------|
| Slow page loads | Network latency, large page size | Optimize page load, implement proper wait strategies |
| Slow element interactions | Complex DOM, JavaScript execution | Simplify DOM structure, optimize scripts |
| Timeout errors | Service unavailability, extreme latency | Implement retry mechanisms, check service status |
| Inconsistent performance | Environmental factors, resource contention | Run tests in controlled environment, ensure isolation |

### Debugging Techniques

1. **Enable verbose logging**:
   ```python
   # Set log level to DEBUG
   import logging
   logging.getLogger().setLevel(logging.DEBUG)
   ```

2. **Capture and analyze browser performance metrics**:
   ```python
   # Example of capturing browser metrics
   performance_metrics = driver.execute_script("return window.performance.timing")
   ```

3. **Isolate components**:
   Test individual operations separately to identify specific bottlenecks.

4. **Compare with baseline**:
   Use historical performance data to identify regressions.

---

## Additional Resources

- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/webdriver/)
- [pytest Documentation](https://docs.pytest.org/)
- [Web Performance Best Practices](https://web.dev/performance-measuring-tools/)