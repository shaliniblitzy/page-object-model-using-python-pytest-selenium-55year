"""
Page object for the Storydoc signup page that implements the Page Object Model pattern.
This class encapsulates all interactions with the signup page UI elements including
form filling, validation, and submission. It provides methods for completing the user
registration workflow with verification.
"""

# Standard library imports
import time  # standard library
from typing import Dict, Optional, Tuple, Union  # standard library

# External imports
from selenium.webdriver.remote.webdriver import WebDriver  # selenium.webdriver.remote.webdriver 4.10+
from selenium.webdriver.remote.webelement import WebElement  # selenium.webdriver.remote.webelement 4.10+

# Internal imports
from .base_page import BasePage
from ..locators.signup_locators import SignupLocators
from ..config.timeout_config import (
    USER_REGISTRATION_TIMEOUT,
    ELEMENT_TIMEOUT,
    EMAIL_DELIVERY_TIMEOUT
)
from ..utilities.email_helper import EmailHelper
from ..utilities.random_data_generator import (
    generate_random_email,
    generate_random_password,
    generate_random_name
)
from ..utilities.logger import log_info, log_error


class SignupPage(BasePage):
    """
    Page object for the Storydoc signup page that provides methods to interact with
    signup form elements and complete the user registration process.
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize the signup page object with WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver, page_name='Signup Page')
        self.url = "https://editor-staging.storydoc.com/sign-up"
        self.email_helper = EmailHelper()
    
    def navigate_to(self) -> bool:
        """
        Navigate to the signup page
        
        Returns:
            True if navigation was successful, False otherwise
        """
        log_info("Navigating to signup page")
        return self.open()
    
    def enter_name(self, name: str) -> bool:
        """
        Enter the full name in the name field
        
        Args:
            name: Full name to enter
            
        Returns:
            True if successful, False otherwise
        """
        log_info(f"Entering name: {name}")
        return self.input_text(SignupLocators.NAME_FIELD, name)
    
    def enter_email(self, email: str) -> bool:
        """
        Enter the email address in the email field
        
        Args:
            email: Email address to enter
            
        Returns:
            True if successful, False otherwise
        """
        log_info(f"Entering email: {email}")
        return self.input_text(SignupLocators.EMAIL_FIELD, email)
    
    def enter_password(self, password: str) -> bool:
        """
        Enter the password in the password field
        
        Args:
            password: Password to enter
            
        Returns:
            True if successful, False otherwise
        """
        log_info(f"Entering password: {'*' * len(password)}")
        return self.input_text(SignupLocators.PASSWORD_FIELD, password)
    
    def accept_terms(self) -> bool:
        """
        Check the terms and conditions checkbox
        
        Returns:
            True if successful, False otherwise
        """
        log_info("Accepting terms and conditions")
        return self.check_checkbox(SignupLocators.TERMS_CHECKBOX)
    
    def click_signup_button(self) -> bool:
        """
        Click the signup button to submit the form
        
        Returns:
            True if successful, False otherwise
        """
        log_info("Clicking signup button")
        return self.click(SignupLocators.SIGNUP_BUTTON)
    
    def is_signup_successful(self) -> bool:
        """
        Check if signup was successful by looking for success message
        
        Returns:
            True if signup was successful, False otherwise
        """
        log_info("Checking if signup was successful")
        return self.is_element_visible(SignupLocators.SIGNUP_SUCCESS_MESSAGE, timeout=ELEMENT_TIMEOUT)
    
    def is_verification_email_sent(self) -> bool:
        """
        Check if verification email sent message is displayed
        
        Returns:
            True if verification email sent message is visible, False otherwise
        """
        log_info("Checking for verification email sent message")
        return self.is_element_visible(SignupLocators.VERIFICATION_EMAIL_SENT, timeout=ELEMENT_TIMEOUT)
    
    def click_signin_link(self) -> bool:
        """
        Click the sign in link to navigate to the signin page
        
        Returns:
            True if successful, False otherwise
        """
        log_info("Clicking sign in link")
        return self.click(SignupLocators.SIGNIN_LINK)
    
    def get_error_message(self, field_type: str) -> str:
        """
        Get the error message text for a specific field
        
        Args:
            field_type: Type of field ('email', 'password', 'terms')
            
        Returns:
            Error message text or empty string if not found
        """
        locator = None
        if field_type == 'email':
            locator = SignupLocators.EMAIL_ERROR_MESSAGE
        elif field_type == 'password':
            locator = SignupLocators.PASSWORD_ERROR_MESSAGE
        elif field_type == 'terms':
            locator = SignupLocators.TERMS_ERROR_MESSAGE
        else:
            return ""
        
        return self.get_text(locator)
    
    def validate_email_field(self, email: str) -> bool:
        """
        Validate if the email field has the correct validation behavior
        
        Args:
            email: Email to test
            
        Returns:
            True if email validation works as expected, False otherwise
        """
        # Enter the email
        self.enter_email(email)
        
        # Click outside the field to trigger validation
        self.click(SignupLocators.NAME_FIELD)
        
        # Check if error message appears for invalid email
        if '@' not in email or '.' not in email:
            return self.is_element_visible(SignupLocators.EMAIL_ERROR_MESSAGE)
        
        return True
    
    def validate_password_field(self, password: str) -> bool:
        """
        Validate if the password field has the correct validation behavior
        
        Args:
            password: Password to test
            
        Returns:
            True if password validation works as expected, False otherwise
        """
        # Enter the password
        self.enter_password(password)
        
        # Click outside the field to trigger validation
        self.click(SignupLocators.NAME_FIELD)
        
        # Check if error message appears for weak password
        # (This would depend on the actual validation rules of the application)
        is_weak = len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password)
        
        if is_weak:
            return self.is_element_visible(SignupLocators.PASSWORD_ERROR_MESSAGE)
        
        return True
    
    def fill_signup_form(self, name: str, email: str, password: str, accept_terms_checkbox: bool = True) -> bool:
        """
        Fill out the signup form with the provided details
        
        Args:
            name: Full name to enter
            email: Email address to enter
            password: Password to enter
            accept_terms_checkbox: Whether to check the terms checkbox
            
        Returns:
            True if all fields were filled successfully, False otherwise
        """
        name_success = self.enter_name(name)
        email_success = self.enter_email(email)
        password_success = self.enter_password(password)
        
        terms_success = True
        if accept_terms_checkbox:
            terms_success = self.accept_terms()
        
        return name_success and email_success and password_success and terms_success
    
    def generate_test_data(self) -> Dict[str, str]:
        """
        Generate random test data for signup form
        
        Returns:
            Dictionary containing name, email, and password
        """
        return {
            'name': generate_random_name(),
            'email': generate_random_email(),
            'password': generate_random_password()
        }
    
    def complete_signup(self, name: str, email: str, password: str) -> bool:
        """
        Complete the entire signup process including form filling and submission
        
        Args:
            name: Full name to enter
            email: Email address to enter
            password: Password to enter
            
        Returns:
            True if signup was successful, False otherwise
        """
        log_info(f"Completing signup with email: {email}")
        
        # Navigate to signup page
        if not self.navigate_to():
            log_error("Failed to navigate to signup page")
            return False
        
        # Fill out the signup form
        if not self.fill_signup_form(name, email, password):
            log_error("Failed to fill signup form")
            return False
        
        # Click the signup button
        if not self.click_signup_button():
            log_error("Failed to click signup button")
            return False
        
        # Wait for success message or verification email message
        success = self.is_signup_successful() or self.is_verification_email_sent()
        
        # Wait for URL to change to confirm redirection after signup
        if success:
            success = self.wait_for_url_contains("/dashboard") or self.wait_for_url_contains("/verify")
        
        if success:
            log_info(f"Signup completed successfully for {email}")
        else:
            log_error(f"Signup failed for {email}")
            self.take_screenshot(f"signup_failure_{email}")
        
        return success
    
    def verify_registration_email(self, email: str, timeout: int = EMAIL_DELIVERY_TIMEOUT) -> bool:
        """
        Verify that the registration confirmation email was received
        
        Args:
            email: Email address to check
            timeout: Maximum time to wait for email in seconds
            
        Returns:
            True if email was received, False otherwise
        """
        log_info(f"Waiting for registration email to be delivered to {email}")
        return self.email_helper.verify_email_received(email, "Welcome to Storydoc", timeout)
    
    def get_verification_link(self, email: str, timeout: int = EMAIL_DELIVERY_TIMEOUT) -> Optional[str]:
        """
        Get the verification link from the registration email
        
        Args:
            email: Email address to check
            timeout: Maximum time to wait for email in seconds
            
        Returns:
            Verification link or None if not found
        """
        # Wait for the email
        message = self.email_helper.wait_for_email(email, "Welcome to Storydoc", timeout)
        
        # Return None if no email received
        if not message:
            log_error(f"No verification email received for {email}")
            return None
        
        # Extract and return the verification link
        verification_link = self.email_helper.extract_verification_link(message)
        
        if verification_link:
            log_info(f"Extracted verification link: {verification_link}")
        else:
            log_error("Failed to extract verification link from email")
        
        return verification_link
    
    def complete_email_verification(self, email: str) -> bool:
        """
        Complete the email verification process by accessing the verification link
        
        Args:
            email: Email address to verify
            
        Returns:
            True if verification was successful, False otherwise
        """
        # Get the verification link
        verification_link = self.get_verification_link(email)
        
        if not verification_link:
            return False
        
        try:
            # Navigate to the verification link
            log_info(f"Navigating to verification link: {verification_link}")
            self.driver.get(verification_link)
            
            # Wait for verification to complete
            # This might redirect to dashboard or show a verified message
            success = (
                self.wait_for_url_contains("/dashboard") or 
                self.is_element_visible(SignupLocators.SUCCESS_MESSAGE)
            )
            
            if success:
                log_info(f"Email verification completed successfully for {email}")
            else:
                log_error(f"Email verification failed for {email}")
                self.take_screenshot(f"verification_failure_{email}")
            
            return success
        except Exception as e:
            log_error(f"Error during email verification: {str(e)}")
            self.take_screenshot(f"verification_error_{email}")
            return False
    
    def complete_registration_with_verification(self, name: str = None, email: str = None, password: str = None) -> Dict:
        """
        Complete the entire user registration process including email verification
        
        Args:
            name: Full name (will generate if None)
            email: Email address (will generate if None)
            password: Password (will generate if None)
            
        Returns:
            Dictionary with registration status and user data
        """
        # Generate test data for any missing parameters
        user_data = self.generate_test_data()
        
        if name:
            user_data['name'] = name
        if email:
            user_data['email'] = email
        if password:
            user_data['password'] = password
        
        result = {
            'success': False,
            'user_data': user_data,
            'verification_success': False,
            'message': ''
        }
        
        # Step 1: Complete signup
        signup_success = self.complete_signup(
            user_data['name'], 
            user_data['email'], 
            user_data['password']
        )
        
        if not signup_success:
            result['message'] = 'Registration failed'
            return result
        
        # Step 2: Verify registration email was received
        email_received = self.verify_registration_email(user_data['email'])
        
        if not email_received:
            result['success'] = True  # Registration succeeded even if email verification fails
            result['message'] = 'Registration successful, but verification email not received'
            return result
        
        # Step 3: Complete email verification
        verification_success = self.complete_email_verification(user_data['email'])
        
        result['success'] = True
        result['verification_success'] = verification_success
        
        if verification_success:
            result['message'] = 'Registration and verification completed successfully'
        else:
            result['message'] = 'Registration successful, but verification failed'
        
        return result