"""
Test module that measures and validates response times for various UI interactions and API operations in the Storydoc application.
Ensures that element interactions and server responses meet the defined Service Level Agreement (SLA) requirements.
"""

import pytest
import time
from typing import Dict, Any

# Internal imports
from ...utilities.performance_monitor import record_element_interaction_time, PerformanceMonitor
from ...utilities.timing_helper import Timer, get_formatted_time, is_within_sla
from ...config.sla_config import is_within_operation_sla, OPERATION_SLAS
from ...config.timeout_config import ELEMENT_TIMEOUT
from ...fixtures.performance_fixtures import (
    performance_monitor,
    performance_timer,
    element_interaction_timer
)
from ...utilities.logger import get_logger

# Setup logger
logger = get_logger(__name__)


def measure_element_interaction_time(page_object: object, locator: tuple, operation: str, element_identifier: str, **args: Dict) -> float:
    """
    Helper function to measure the response time for an element interaction
    
    Args:
        page_object: Page object instance
        locator: Element locator tuple
        operation: Operation to perform (click, input_text, etc.)
        element_identifier: Human-readable identifier for the element
        args: Additional arguments for the operation
        
    Returns:
        Interaction time in seconds
    """
    logger.info(f"Measuring {operation} response time for {element_identifier}")
    
    # Create timer for precise measurement
    timer = Timer(name=f"{element_identifier}_{operation}")
    
    # Start timing
    timer.start()
    
    # Perform the requested operation
    if operation == "click":
        page_object.click(locator)
    elif operation == "input_text":
        page_object.input_text(locator, args.get("text", ""))
    elif operation == "check":
        page_object.check(locator)
    elif operation == "uncheck":
        page_object.uncheck(locator)
    elif operation == "select":
        page_object.select(locator, args.get("option", ""))
    else:
        # Default to generic method call if operation not recognized
        method = getattr(page_object, operation)
        method(locator, **args)
    
    # Stop timing and get elapsed time
    interaction_time = timer.stop()
    
    # Log the measured time
    logger.info(f"{element_identifier} {operation} response time: {get_formatted_time(interaction_time)}")
    
    # Record the interaction time in the performance monitoring system
    record_element_interaction_time(element_identifier, operation, interaction_time)
    
    return interaction_time


def assert_interaction_time_within_sla(element_identifier: str, operation: str, interaction_time: float) -> None:
    """
    Helper function to assert that element interaction time is within SLA requirements
    
    Args:
        element_identifier: Human-readable identifier for the element
        operation: Operation performed (click, input_text, etc.)
        interaction_time: Measured interaction time in seconds
    """
    # Check if the interaction time is within SLA for element interactions
    is_compliant = is_within_operation_sla("element_interaction", interaction_time)
    
    # Log SLA compliance result
    sla_threshold = OPERATION_SLAS["element_interaction"]["target_response_time"]
    if is_compliant:
        logger.info(f"SLA PASS: {element_identifier} {operation} response time {get_formatted_time(interaction_time)} is within SLA ({get_formatted_time(sla_threshold)})")
    else:
        logger.warning(f"SLA FAIL: {element_identifier} {operation} response time {get_formatted_time(interaction_time)} exceeds SLA ({get_formatted_time(sla_threshold)})")
    
    # Assert that interaction time is within SLA
    assert is_compliant, f"{element_identifier} {operation} response time ({get_formatted_time(interaction_time)}) exceeds SLA threshold ({get_formatted_time(sla_threshold)})"


class TestElementResponseTime:
    """
    Test class for measuring and validating element interaction response times
    """
    
    def test_button_click_response_time(self, signin_page, performance_timer):
        """
        Test to measure and validate the response time of button click interactions
        
        Args:
            signin_page: Signin page object fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_button_click_response_time")
        
        # Navigate to the signin page
        signin_page.navigate_to()
        
        # Measure response time for clicking the signin button
        performance_timer.start()
        signin_page.click_signin_button()
        click_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements
        assert_interaction_time_within_sla("Signin Button", "click", click_time)
        
        logger.info("Completed test: test_button_click_response_time")
    
    def test_text_input_response_time(self, signup_page, performance_timer):
        """
        Test to measure and validate the response time of text input interactions
        
        Args:
            signup_page: Signup page object fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_text_input_response_time")
        
        # Navigate to the signup page
        signup_page.navigate_to()
        
        # Measure response time for entering text in the email field
        performance_timer.start()
        signup_page.enter_email("test@mailinator.com")
        email_input_time = performance_timer.stop()
        
        # Measure response time for entering text in the password field
        performance_timer.start()
        signup_page.enter_password("Test@123")
        password_input_time = performance_timer.stop()
        
        # Measure response time for entering text in the name field
        performance_timer.start()
        signup_page.enter_name("Test User")
        name_input_time = performance_timer.stop()
        
        # Validate that all measured response times are within SLA requirements
        assert_interaction_time_within_sla("Email Field", "input", email_input_time)
        assert_interaction_time_within_sla("Password Field", "input", password_input_time)
        assert_interaction_time_within_sla("Name Field", "input", name_input_time)
        
        logger.info("Completed test: test_text_input_response_time")
    
    def test_checkbox_interaction_response_time(self, signup_page, performance_timer):
        """
        Test to measure and validate the response time of checkbox interactions
        
        Args:
            signup_page: Signup page object fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_checkbox_interaction_response_time")
        
        # Navigate to the signup page
        signup_page.navigate_to()
        
        # Measure response time for checking the terms checkbox
        performance_timer.start()
        signup_page.accept_terms()
        check_time = performance_timer.stop()
        
        # Measure response time for unchecking the terms checkbox
        performance_timer.start()
        signup_page.accept_terms()  # Assuming this is a toggle action, otherwise use an uncheck method
        uncheck_time = performance_timer.stop()
        
        # Validate that both measured response times are within SLA requirements
        assert_interaction_time_within_sla("Terms Checkbox", "check", check_time)
        assert_interaction_time_within_sla("Terms Checkbox", "uncheck", uncheck_time)
        
        logger.info("Completed test: test_checkbox_interaction_response_time")
    
    def test_dropdown_selection_response_time(self, story_editor_page, authenticated_user, performance_timer):
        """
        Test to measure and validate the response time of dropdown selection interactions
        
        Args:
            story_editor_page: Story Editor page object fixture
            authenticated_user: Authenticated user fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_dropdown_selection_response_time")
        
        # Ensure user is authenticated and navigate to the story editor page
        story_editor_page.navigate_to()
        
        # Measure response time for selecting a template from dropdown
        performance_timer.start()
        story_editor_page.select_template("Basic")
        selection_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements
        assert_interaction_time_within_sla("Template Dropdown", "select", selection_time)
        
        logger.info("Completed test: test_dropdown_selection_response_time")


class TestFormSubmissionResponseTime:
    """
    Test class for measuring and validating form submission response times
    """
    
    def test_signup_form_submission_time(self, signup_page, performance_timer):
        """
        Test to measure and validate the response time of signup form submission
        
        Args:
            signup_page: Signup page object fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_signup_form_submission_time")
        
        # Navigate to the signup page
        signup_page.navigate_to()
        
        # Fill out the signup form with valid test data
        signup_page.enter_email("test.user@mailinator.com")
        signup_page.enter_password("Test@123")
        signup_page.enter_name("Test User")
        signup_page.accept_terms()
        
        # Measure response time for submitting the signup form
        performance_timer.start()
        signup_page.click_signup_button()
        submission_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements for form submissions
        is_compliant = is_within_operation_sla("form_submission", submission_time)
        
        sla_threshold = OPERATION_SLAS["form_submission"]["target_response_time"]
        assert is_compliant, f"Signup form submission time ({get_formatted_time(submission_time)}) exceeds SLA threshold ({get_formatted_time(sla_threshold)})"
        
        logger.info("Completed test: test_signup_form_submission_time")
    
    def test_signin_form_submission_time(self, signin_page, performance_timer):
        """
        Test to measure and validate the response time of signin form submission
        
        Args:
            signin_page: Signin page object fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_signin_form_submission_time")
        
        # Navigate to the signin page
        signin_page.navigate_to()
        
        # Fill out the signin form with valid credentials
        signin_page.enter_email("existing.user@mailinator.com")
        signin_page.enter_password("Test@123")
        
        # Measure response time for submitting the signin form
        performance_timer.start()
        signin_page.click_signin_button()
        submission_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements for form submissions
        is_compliant = is_within_operation_sla("form_submission", submission_time)
        
        sla_threshold = OPERATION_SLAS["form_submission"]["target_response_time"]
        assert is_compliant, f"Signin form submission time ({get_formatted_time(submission_time)}) exceeds SLA threshold ({get_formatted_time(sla_threshold)})"
        
        logger.info("Completed test: test_signin_form_submission_time")
    
    def test_story_save_response_time(self, story_editor_page, authenticated_user, performance_timer):
        """
        Test to measure and validate the response time of saving a story
        
        Args:
            story_editor_page: Story Editor page object fixture
            authenticated_user: Authenticated user fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_story_save_response_time")
        
        # Ensure user is authenticated and navigate to the story editor page
        story_editor_page.navigate_to()
        
        # Enter basic story details
        story_editor_page.enter_story_title("Test Story")
        story_editor_page.select_template("Basic")
        
        # Measure response time for saving the story
        performance_timer.start()
        story_editor_page.save_story()
        save_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements
        is_compliant = is_within_operation_sla("form_submission", save_time)
        
        sla_threshold = OPERATION_SLAS["form_submission"]["target_response_time"]
        assert is_compliant, f"Story save operation time ({get_formatted_time(save_time)}) exceeds SLA threshold ({get_formatted_time(sla_threshold)})"
        
        logger.info("Completed test: test_story_save_response_time")
    
    def test_story_share_response_time(self, share_dialog_page, story_editor_page, authenticated_user, performance_timer):
        """
        Test to measure and validate the response time of sharing a story
        
        Args:
            share_dialog_page: Share Dialog page object fixture
            story_editor_page: Story Editor page object fixture
            authenticated_user: Authenticated user fixture
            performance_timer: Timer fixture for measuring performance
        """
        logger.info("Starting test: test_story_share_response_time")
        
        # Ensure user is authenticated and navigate to the story editor page with an existing story
        story_editor_page.navigate_to()
        
        # Open the share dialog
        story_editor_page.click_share_button()
        
        # Enter recipient email address
        share_dialog_page.enter_recipient_email("recipient@mailinator.com")
        
        # Measure response time for submitting the share form
        performance_timer.start()
        share_dialog_page.click_share_button()
        share_time = performance_timer.stop()
        
        # Validate that the measured response time is within SLA requirements
        is_compliant = is_within_operation_sla("form_submission", share_time)
        
        sla_threshold = OPERATION_SLAS["form_submission"]["target_response_time"]
        assert is_compliant, f"Story share operation time ({get_formatted_time(share_time)}) exceeds SLA threshold ({get_formatted_time(sla_threshold)})"
        
        logger.info("Completed test: test_story_share_response_time")


class TestSequentialInteractionResponseTime:
    """
    Test class for measuring and validating response times of sequential interactions
    """
    
    def test_form_fill_response_time(self, signup_page, performance_timer, performance_monitor):
        """
        Test to measure the cumulative and individual response times of sequential form interactions
        
        Args:
            signup_page: Signup page object fixture
            performance_timer: Timer fixture for measuring performance
            performance_monitor: Performance monitor fixture
        """
        logger.info("Starting test: test_form_fill_response_time")
        
        # Navigate to the signup page
        signup_page.navigate_to()
        
        # Measure individual response times for each form field interaction
        performance_timer.start()
        signup_page.enter_email("test.sequential@mailinator.com")
        email_time = performance_timer.stop()
        
        performance_timer.start()
        signup_page.enter_password("Test@123")
        password_time = performance_timer.stop()
        
        performance_timer.start()
        signup_page.enter_name("Test User")
        name_time = performance_timer.stop()
        
        performance_timer.start()
        signup_page.accept_terms()
        terms_time = performance_timer.stop()
        
        # Measure cumulative time for the complete form fill process
        total_timer = Timer()
        total_timer.start()
        
        signup_page.enter_email("test.sequential@mailinator.com")
        signup_page.enter_password("Test@123")
        signup_page.enter_name("Test User")
        signup_page.accept_terms()
        
        total_time = total_timer.stop()
        
        # Validate that all individual response times are within SLA requirements
        assert_interaction_time_within_sla("Email Field", "input", email_time)
        assert_interaction_time_within_sla("Password Field", "input", password_time)
        assert_interaction_time_within_sla("Name Field", "input", name_time)
        assert_interaction_time_within_sla("Terms Checkbox", "check", terms_time)
        
        # Validate that the cumulative time is reasonable
        # (sum of individual times may be less than cumulative due to setup overhead)
        sum_of_individual = email_time + password_time + name_time + terms_time
        logger.info(f"Sum of individual interactions: {get_formatted_time(sum_of_individual)}")
        logger.info(f"Cumulative form fill time: {get_formatted_time(total_time)}")
        
        # Generate a report comparing individual vs. cumulative times
        performance_monitor.generate_report(report_name="form_fill_comparison")
        
        logger.info(f"Completed test: test_form_fill_response_time - Individual times: Email {get_formatted_time(email_time)}, Password {get_formatted_time(password_time)}, Name {get_formatted_time(name_time)}, Terms {get_formatted_time(terms_time)} - Total: {get_formatted_time(total_time)}")
    
    def test_story_creation_workflow_response_time(self, signin_page, dashboard_page, story_editor_page, authenticated_user, performance_timer, performance_monitor):
        """
        Test to measure response times across the entire story creation workflow
        
        Args:
            signin_page: Signin page object fixture
            dashboard_page: Dashboard page object fixture
            story_editor_page: Story Editor page object fixture
            authenticated_user: Authenticated user fixture
            performance_timer: Timer fixture for measuring performance
            performance_monitor: Performance monitor fixture
        """
        logger.info("Starting test: test_story_creation_workflow_response_time")
        
        # Ensure user is authenticated 
        # (using authenticated_user fixture)
        
        # Measure response time for navigating to dashboard
        performance_timer.start()
        dashboard_page.navigate_to()
        dashboard_time = performance_timer.stop()
        
        # Measure response time for clicking create story button
        performance_timer.start()
        dashboard_page.click_create_story_button()
        create_button_time = performance_timer.stop()
        
        # Measure response time for selecting a template
        performance_timer.start()
        story_editor_page.select_template("Basic")
        template_time = performance_timer.stop()
        
        # Measure response time for entering story title
        performance_timer.start()
        story_editor_page.enter_story_title("Performance Test Story")
        title_time = performance_timer.stop()
        
        # Measure response time for saving the story
        performance_timer.start()
        story_editor_page.save_story()
        save_time = performance_timer.stop()
        
        # Calculate total workflow response time
        total_workflow_time = dashboard_time + create_button_time + template_time + title_time + save_time
        
        # Validate that all individual response times are within SLA requirements
        assert_interaction_time_within_sla("Dashboard", "navigation", dashboard_time)
        assert_interaction_time_within_sla("Create Story Button", "click", create_button_time)
        assert_interaction_time_within_sla("Template Selection", "select", template_time)
        assert_interaction_time_within_sla("Story Title", "input", title_time)
        
        # Validate that save operation meets form submission SLA
        is_save_compliant = is_within_operation_sla("form_submission", save_time)
        save_threshold = OPERATION_SLAS["form_submission"]["target_response_time"]
        assert is_save_compliant, f"Story save time ({get_formatted_time(save_time)}) exceeds SLA threshold ({get_formatted_time(save_threshold)})"
        
        # Validate that the total workflow time meets SLA requirements
        is_workflow_compliant = is_within_operation_sla("test_execution", total_workflow_time)
        workflow_threshold = OPERATION_SLAS["test_execution"]["target_response_time"]
        assert is_workflow_compliant, f"Story creation workflow time ({get_formatted_time(total_workflow_time)}) exceeds SLA threshold ({get_formatted_time(workflow_threshold)})"
        
        # Generate a workflow performance report
        performance_monitor.generate_report(report_name="story_creation_workflow")
        
        logger.info(f"Completed test: test_story_creation_workflow_response_time - Dashboard: {get_formatted_time(dashboard_time)}, Create Button: {get_formatted_time(create_button_time)}, Template: {get_formatted_time(template_time)}, Title: {get_formatted_time(title_time)}, Save: {get_formatted_time(save_time)} - Total: {get_formatted_time(total_workflow_time)}")