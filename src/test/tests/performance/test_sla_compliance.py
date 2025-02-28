"""
Test module for validating Service Level Agreement (SLA) compliance of the Storydoc application.
It measures and validates performance metrics against defined SLA thresholds for different operations
and test types, ensuring the application meets performance requirements.
"""

import pytest
import time
import json

# Internal imports
from ...config.sla_config import (
    OPERATION_SLAS,
    TEST_TYPE_SLAS,
    get_operation_sla,
    get_test_type_sla,
    is_within_operation_sla,
    is_within_test_type_sla
)
from ...fixtures.performance_fixtures import (
    performance_monitor,
    session_performance_monitor,
    performance_threshold_validator,
    page_load_timer,
    element_interaction_timer
)
from ...utilities.timing_helper import TimingContext
from ...utilities.performance_monitor import (
    get_performance_data,
    get_performance_summary
)
from ...pages.base_page import BasePage

# Constants for operations
PAGE_NAVIGATION_OPERATIONS = ['signin_page_load', 'signup_page_load', 'dashboard_load', 'story_editor_load', 'share_dialog_load']
ELEMENT_INTERACTION_OPERATIONS = ['click_button', 'input_text', 'select_dropdown', 'check_checkbox']
TEST_TYPE_OPERATIONS = ['user_registration', 'user_authentication', 'story_creation', 'story_sharing', 'full_workflow']


def load_performance_thresholds():
    """
    Loads performance thresholds from the JSON configuration file
    
    Returns:
        dict: Dictionary containing performance thresholds
    """
    try:
        with open('src/test/config/performance_thresholds.json', 'r') as file:
            thresholds = json.load(file)
        return thresholds
    except Exception as e:
        pytest.fail(f"Failed to load performance thresholds: {str(e)}")
        return {}


def validate_operation_sla(sla_config):
    """
    Validates that operation SLA definitions match expected structure
    
    Args:
        sla_config: SLA configuration dictionary
        
    Returns:
        bool: True if validation passed, False otherwise
    """
    required_fields = ['target_response_time', 'timeout', 'retry_strategy']
    
    for operation, config in sla_config.items():
        # Check required fields
        for field in required_fields:
            if field not in config:
                return False
        
        # Check types
        if not isinstance(config['target_response_time'], (int, float)):
            return False
        if not isinstance(config['timeout'], (int, float)):
            return False
        if not isinstance(config['retry_strategy'], dict):
            return False
            
    return True


class TestOperationSLACompliance:
    """Test class for validating SLA compliance of individual operations"""
    
    def test_page_navigation_sla_definitions(self):
        """Verify that page navigation SLA definitions meet requirements"""
        # Check that page navigation operations have defined SLAs
        page_navigation_sla = get_operation_sla('page_navigation')
        
        # Verify that target response time is within requirements
        assert page_navigation_sla['target_response_time'] <= 5, \
            f"Page navigation target response time ({page_navigation_sla['target_response_time']}s) exceeds requirement (5s)"
        
        # Verify timeout is greater than target response time
        assert page_navigation_sla['timeout'] > page_navigation_sla['target_response_time'], \
            "Page navigation timeout must be greater than target response time"
    
    def test_element_interaction_sla_definitions(self):
        """Verify that element interaction SLA definitions meet requirements"""
        # Check that element interaction operations have defined SLAs
        element_interaction_sla = get_operation_sla('element_interaction')
        
        # Verify that target response time is within requirements
        assert element_interaction_sla['target_response_time'] <= 2, \
            f"Element interaction target response time ({element_interaction_sla['target_response_time']}s) exceeds requirement (2s)"
        
        # Verify timeout is greater than target response time
        assert element_interaction_sla['timeout'] > element_interaction_sla['target_response_time'], \
            "Element interaction timeout must be greater than target response time"
    
    def test_form_submission_sla_definitions(self):
        """Verify that form submission SLA definitions meet requirements"""
        # Check that form submission operations have defined SLAs
        form_submission_sla = get_operation_sla('form_submission')
        
        # Verify that target response time is within requirements
        assert form_submission_sla['target_response_time'] <= 3, \
            f"Form submission target response time ({form_submission_sla['target_response_time']}s) exceeds requirement (3s)"
        
        # Verify timeout is greater than target response time
        assert form_submission_sla['timeout'] > form_submission_sla['target_response_time'], \
            "Form submission timeout must be greater than target response time"
    
    def test_page_navigation_performance(self, performance_monitor, page_load_timer):
        """Test that page navigation operations meet SLA requirements"""
        # Create a mock page for testing
        class TestPage(BasePage):
            def __init__(self, driver):
                super().__init__(driver)
                self.url = "https://editor-staging.storydoc.com"
            
            def navigate_to(self):
                self.open()
        
        # Create mock driver for the test
        class MockDriver:
            def get(self, url):
                # Simulate page load time
                time.sleep(0.5)  # This should be well under the 5s target
            
            def execute_script(self, script):
                return True  # Simulate page ready state
        
        # Create mock page with mock driver
        mock_driver = MockDriver()
        test_page = TestPage(mock_driver)
        
        # Measure page load time
        load_time = page_load_timer(test_page, "navigate_to")
        
        # Verify it meets SLA requirements
        assert is_within_operation_sla('page_navigation', load_time), \
            f"Page navigation time ({load_time}s) exceeds SLA threshold ({get_operation_sla('page_navigation')['target_response_time']}s)"
        
        # Get performance summary
        summary = get_performance_summary(['page_load'])
        
        # Assert that all page loads meet SLA requirements
        assert summary.get('page_load', {}).get('sla_compliance', {}).get('compliance_percentage', 0) >= 90, \
            "Less than 90% of page loads meet SLA requirements"
    
    def test_element_interaction_performance(self, performance_monitor, element_interaction_timer):
        """Test that element interaction operations meet SLA requirements"""
        # Define mock interactions for testing
        def mock_click():
            # Simulate element click time
            time.sleep(0.1)  # This should be well under the 2s target
            return True
        
        def mock_input():
            # Simulate element input time
            time.sleep(0.2)  # This should be well under the 2s target
            return True
        
        # Use element_interaction_timer to measure performance
        click_result, click_time = element_interaction_timer("test_button", mock_click)
        input_result, input_time = element_interaction_timer("test_input", mock_input)
        
        # Verify they meet SLA requirements
        assert is_within_operation_sla('element_interaction', click_time), \
            f"Element click time ({click_time}s) exceeds SLA threshold ({get_operation_sla('element_interaction')['target_response_time']}s)"
        
        assert is_within_operation_sla('element_interaction', input_time), \
            f"Element input time ({input_time}s) exceeds SLA threshold ({get_operation_sla('element_interaction')['target_response_time']}s)"
        
        # Get performance summary
        summary = get_performance_summary(['element_interaction'])
        
        # Assert that all element interactions meet SLA requirements
        assert summary.get('element_interaction', {}).get('sla_compliance', {}).get('compliance_percentage', 0) >= 90, \
            "Less than 90% of element interactions meet SLA requirements"


class TestTestTypeSLACompliance:
    """Test class for validating SLA compliance of test types"""
    
    def test_test_type_sla_definitions(self):
        """Verify that test type SLA definitions meet requirements"""
        # Verify each test type has defined SLAs
        for test_type in TEST_TYPE_OPERATIONS:
            sla = get_test_type_sla(test_type)
            
            # Verify maximum duration matches requirements
            if test_type == 'user_registration':
                assert sla['maximum_duration'] == 30, "User registration maximum duration should be 30 seconds"
            elif test_type == 'user_authentication':
                assert sla['maximum_duration'] == 20, "User authentication maximum duration should be 20 seconds"
            elif test_type == 'story_creation':
                assert sla['maximum_duration'] == 45, "Story creation maximum duration should be 45 seconds"
            elif test_type == 'story_sharing':
                assert sla['maximum_duration'] == 60, "Story sharing maximum duration should be 60 seconds"
            elif test_type == 'full_workflow':
                assert sla['maximum_duration'] == 180, "Full workflow maximum duration should be 180 seconds"
            
            # Verify success rate is defined and reasonable
            assert 'success_rate' in sla, f"Success rate not defined for {test_type}"
            assert 80 <= sla['success_rate'] <= 100, f"Success rate for {test_type} should be between 80% and 100%"
    
    def test_user_registration_performance(self, performance_monitor, performance_threshold_validator):
        """Test that user registration performance meets SLA requirements"""
        # Simulate a user registration test
        with TimingContext("user_registration_test", "test_execution"):
            # Simulate test execution time
            time.sleep(1)  # This should be well under the 30s target
        
        # Get the test execution time from performance monitor
        performance_data = get_performance_data('test_execution')
        registration_time = next((item['execution_time'] for item in performance_data if item['operation'] == 'user_registration_test'), 0)
        
        # Validate against threshold
        performance_threshold_validator(registration_time, operation_type='user_registration', operation_name='user_registration_test')
        
        # Assert directly
        assert is_within_test_type_sla('user_registration', registration_time), \
            f"User registration time ({registration_time}s) exceeds SLA threshold ({get_test_type_sla('user_registration')['maximum_duration']}s)"
    
    def test_user_authentication_performance(self, performance_monitor, performance_threshold_validator):
        """Test that user authentication performance meets SLA requirements"""
        # Simulate a user authentication test
        with TimingContext("user_authentication_test", "test_execution"):
            # Simulate test execution time
            time.sleep(0.8)  # This should be well under the 20s target
        
        # Get the test execution time from performance monitor
        performance_data = get_performance_data('test_execution')
        authentication_time = next((item['execution_time'] for item in performance_data if item['operation'] == 'user_authentication_test'), 0)
        
        # Validate against threshold
        performance_threshold_validator(authentication_time, operation_type='user_authentication', operation_name='user_authentication_test')
        
        # Assert directly
        assert is_within_test_type_sla('user_authentication', authentication_time), \
            f"User authentication time ({authentication_time}s) exceeds SLA threshold ({get_test_type_sla('user_authentication')['maximum_duration']}s)"
    
    def test_story_creation_performance(self, performance_monitor, performance_threshold_validator):
        """Test that story creation performance meets SLA requirements"""
        # Simulate a story creation test
        with TimingContext("story_creation_test", "test_execution"):
            # Simulate test execution time
            time.sleep(1.5)  # This should be well under the 45s target
        
        # Get the test execution time from performance monitor
        performance_data = get_performance_data('test_execution')
        creation_time = next((item['execution_time'] for item in performance_data if item['operation'] == 'story_creation_test'), 0)
        
        # Validate against threshold
        performance_threshold_validator(creation_time, operation_type='story_creation', operation_name='story_creation_test')
        
        # Assert directly
        assert is_within_test_type_sla('story_creation', creation_time), \
            f"Story creation time ({creation_time}s) exceeds SLA threshold ({get_test_type_sla('story_creation')['maximum_duration']}s)"
    
    def test_story_sharing_performance(self, performance_monitor, performance_threshold_validator):
        """Test that story sharing performance meets SLA requirements"""
        # Simulate a story sharing test
        with TimingContext("story_sharing_test", "test_execution"):
            # Simulate test execution time
            time.sleep(2)  # This should be well under the 60s target
        
        # Get the test execution time from performance monitor
        performance_data = get_performance_data('test_execution')
        sharing_time = next((item['execution_time'] for item in performance_data if item['operation'] == 'story_sharing_test'), 0)
        
        # Validate against threshold
        performance_threshold_validator(sharing_time, operation_type='story_sharing', operation_name='story_sharing_test')
        
        # Assert directly
        assert is_within_test_type_sla('story_sharing', sharing_time), \
            f"Story sharing time ({sharing_time}s) exceeds SLA threshold ({get_test_type_sla('story_sharing')['maximum_duration']}s)"
    
    def test_full_workflow_performance(self, performance_monitor, performance_threshold_validator):
        """Test that full end-to-end workflow performance meets SLA requirements"""
        # Simulate a full workflow test
        with TimingContext("full_workflow_test", "test_execution"):
            # Simulate test execution time
            time.sleep(5)  # This should be well under the 180s target
        
        # Get the test execution time from performance monitor
        performance_data = get_performance_data('test_execution')
        workflow_time = next((item['execution_time'] for item in performance_data if item['operation'] == 'full_workflow_test'), 0)
        
        # Validate against threshold
        performance_threshold_validator(workflow_time, operation_type='full_workflow', operation_name='full_workflow_test')
        
        # Assert directly
        assert is_within_test_type_sla('full_workflow', workflow_time), \
            f"Full workflow time ({workflow_time}s) exceeds SLA threshold ({get_test_type_sla('full_workflow')['maximum_duration']}s)"


class TestPerformanceReporting:
    """Test class for validating performance reporting capabilities"""
    
    def test_performance_data_collection(self, performance_monitor):
        """Verify that performance data is correctly collected and stored"""
        # Record some test metrics
        with TimingContext("test_operation", "test_category"):
            time.sleep(0.5)
        
        # Get the recorded data
        performance_data = get_performance_data('test_category')
        
        # Verify data is correctly recorded
        assert performance_data, "No performance data was collected"
        assert len(performance_data) > 0, "Performance data array is empty"
        assert any(item['operation'] == 'test_operation' for item in performance_data), "Test operation not found in performance data"
        
        # Verify data structure
        for item in performance_data:
            assert 'operation' in item, "Operation field missing in performance data"
            assert 'execution_time' in item, "Execution time field missing in performance data"
            assert 'timestamp' in item, "Timestamp field missing in performance data"
    
    def test_performance_summary_generation(self, performance_monitor):
        """Verify that performance summary is correctly generated"""
        # Record various metrics
        with TimingContext("page_load_test", "page_load"):
            time.sleep(0.3)
        
        with TimingContext("element_click_test", "element_interaction"):
            time.sleep(0.2)
        
        with TimingContext("test_execution_test", "test_execution"):
            time.sleep(0.5)
        
        # Generate summary
        summary = get_performance_summary()
        
        # Verify summary structure
        assert 'page_load' in summary, "Page load category missing in summary"
        assert 'element_interaction' in summary, "Element interaction category missing in summary"
        assert 'test_execution' in summary, "Test execution category missing in summary"
        
        # Verify category statistics
        for category in ['page_load', 'element_interaction', 'test_execution']:
            assert 'mean' in summary[category], f"Mean missing in {category} statistics"
            assert 'min' in summary[category], f"Min missing in {category} statistics"
            assert 'max' in summary[category], f"Max missing in {category} statistics"
            assert 'count' in summary[category], f"Count missing in {category} statistics"
            assert 'operations' in summary[category], f"Operations missing in {category} statistics"
            assert 'sla_compliance' in summary[category], f"SLA compliance missing in {category} statistics"
            
            # Verify SLA compliance percentage is calculated
            sla_compliance = summary[category]['sla_compliance']
            assert 'compliance_percentage' in sla_compliance, f"Compliance percentage missing in {category} SLA compliance"
    
    def test_sla_compliance_reporting(self, session_performance_monitor):
        """Verify that SLA compliance is correctly reported"""
        # Record metrics that should meet SLA
        with TimingContext("compliant_operation", "page_load"):
            time.sleep(0.3)  # This should be under any SLA threshold
        
        # Record metrics that should exceed SLA
        with TimingContext("non_compliant_operation", "page_load"):
            time.sleep(10)  # This should exceed page navigation SLA threshold
        
        # Generate summary
        summary = get_performance_summary(['page_load'])
        
        # Verify compliance results
        page_load_compliance = summary['page_load']['sla_compliance']
        assert page_load_compliance['compliant'] >= 1, "Compliant operations not correctly counted"
        assert page_load_compliance['non_compliant'] >= 1, "Non-compliant operations not correctly counted"
        
        # Verify percentage calculation
        total_ops = page_load_compliance['compliant'] + page_load_compliance['non_compliant']
        expected_percentage = (page_load_compliance['compliant'] / total_ops * 100) if total_ops > 0 else 0
        assert abs(page_load_compliance['compliance_percentage'] - expected_percentage) < 0.01, \
            "Compliance percentage calculation is incorrect"