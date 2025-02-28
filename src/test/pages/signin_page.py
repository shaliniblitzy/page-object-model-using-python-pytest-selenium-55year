from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_page import BasePage
from .dashboard_page import DashboardPage
from ..locators.signin_locators import SigninLocators
from ..config.timeout_config import USER_AUTHENTICATION_TIMEOUT
from ..utilities.logger import log_info, log_debug, log_error
from ..utilities.wait_helper import WaitUtils
import time


class SigninPage(BasePage):
    """
    Page object representing the Storydoc signin page. Provides methods to interact
    with the signin form and validate authentication results.
    """
    
    def __init__(self, driver):
        """
        Initialize the signin page object with WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        # Initialize the base page with the driver
        super().__init__(driver)
        
        # Set the URL for the signin page
        self.url = "https://editor-staging.storydoc.com/sign-in"
        
        # Set a title for the page for logging purposes
        self.title = "Storydoc Signin"
        
        # Initialize dashboard page for verification of successful login
        self.dashboard_page = DashboardPage(driver)
        
        # Log initialization
        log_info("Initialized Signin page object")
    
    def navigate_to(self):
        """
        Navigate to the signin page
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            # Use the open method from BasePage to navigate to the signin URL
            self.open()
            
            # Wait for page to be ready
            WaitUtils.wait_for_page_ready(self.driver)
            
            # Verify that the signin form is displayed
            if self.is_element_visible(SigninLocators.EMAIL_FIELD) and \
               self.is_element_visible(SigninLocators.PASSWORD_FIELD) and \
               self.is_element_visible(SigninLocators.SIGNIN_BUTTON):
                log_info("Successfully navigated to Signin page")
                return True
            else:
                log_error("Signin page elements not visible after navigation")
                return False
        except Exception as e:
            log_error(f"Failed to navigate to Signin page: {str(e)}")
            return False
    
    def enter_email(self, email):
        """
        Enter the email address in the email field
        
        Args:
            email: Email address to enter
            
        Returns:
            bool: True if email was entered successfully, False otherwise
        """
        try:
            log_info(f"Entering email: {email}")
            return self.input_text(SigninLocators.EMAIL_FIELD, email)
        except Exception as e:
            log_error(f"Failed to enter email: {str(e)}")
            return False
    
    def enter_password(self, password):
        """
        Enter the password in the password field
        
        Args:
            password: Password to enter
            
        Returns:
            bool: True if password was entered successfully, False otherwise
        """
        try:
            log_info("Entering password")
            return self.input_text(SigninLocators.PASSWORD_FIELD, password)
        except Exception as e:
            log_error(f"Failed to enter password: {str(e)}")
            return False
    
    def check_remember_me(self):
        """
        Check the 'Remember Me' checkbox if it exists
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            log_info("Checking 'Remember Me' checkbox")
            
            # Check if the checkbox is visible first
            if self.is_element_visible(SigninLocators.REMEMBER_ME_CHECKBOX):
                return self.check_checkbox(SigninLocators.REMEMBER_ME_CHECKBOX)
            else:
                log_debug("Remember Me checkbox not found, skipping")
                return True  # Return True if not found, as it's optional
        except Exception as e:
            log_error(f"Failed to check Remember Me checkbox: {str(e)}")
            return False
    
    def click_signin_button(self):
        """
        Click the signin button to submit the form
        
        Returns:
            bool: True if button was clicked successfully, False otherwise
        """
        try:
            log_info("Clicking Signin button")
            result = self.click(SigninLocators.SIGNIN_BUTTON)
            
            # Wait a moment for page transition
            time.sleep(1)
            
            return result
        except Exception as e:
            log_error(f"Failed to click Signin button: {str(e)}")
            return False
    
    def get_error_message(self):
        """
        Get the error message displayed on failed signin
        
        Returns:
            str: Error message text or empty string if no error
        """
        try:
            log_info("Getting error message (if any)")
            
            # Check if the general error message is visible
            if self.is_element_visible(SigninLocators.SIGNIN_ERROR_MESSAGE):
                return self.get_text(SigninLocators.SIGNIN_ERROR_MESSAGE)
            
            # Check for field-specific error messages
            error_texts = []
            
            if self.is_element_visible(SigninLocators.EMAIL_ERROR_MESSAGE):
                email_error = self.get_text(SigninLocators.EMAIL_ERROR_MESSAGE)
                if email_error:
                    error_texts.append(f"Email: {email_error}")
            
            if self.is_element_visible(SigninLocators.PASSWORD_ERROR_MESSAGE):
                password_error = self.get_text(SigninLocators.PASSWORD_ERROR_MESSAGE)
                if password_error:
                    error_texts.append(f"Password: {password_error}")
            
            # Combine field-specific errors if any
            if error_texts:
                return " | ".join(error_texts)
            
            return ""
        except Exception as e:
            log_error(f"Error getting error message: {str(e)}")
            return ""
    
    def is_signin_successful(self, timeout=USER_AUTHENTICATION_TIMEOUT):
        """
        Verify if signin was successful by checking dashboard access
        
        Args:
            timeout: Maximum time to wait for dashboard to load
            
        Returns:
            bool: True if signin was successful, False otherwise
        """
        try:
            log_info("Verifying successful signin")
            
            # Use the dashboard page's is_loaded method to check if we've been redirected
            return self.dashboard_page.is_loaded()
        except Exception as e:
            log_error(f"Error verifying signin success: {str(e)}")
            return False
    
    def is_signin_error_displayed(self):
        """
        Check if any signin error message is displayed
        
        Returns:
            bool: True if error message is displayed, False otherwise
        """
        try:
            log_info("Checking for signin error messages")
            
            # Check for various error message elements
            general_error = self.is_element_visible(SigninLocators.SIGNIN_ERROR_MESSAGE)
            email_error = self.is_element_visible(SigninLocators.EMAIL_ERROR_MESSAGE)
            password_error = self.is_element_visible(SigninLocators.PASSWORD_ERROR_MESSAGE)
            
            # Return True if any error is visible
            is_error = general_error or email_error or password_error
            
            if is_error:
                log_info("Signin error message is displayed")
            else:
                log_info("No signin error message is displayed")
            
            return is_error
        except Exception as e:
            log_error(f"Error checking for signin errors: {str(e)}")
            return False
    
    def click_forgot_password(self):
        """
        Click the 'Forgot Password' link
        
        Returns:
            bool: True if link was clicked successfully, False otherwise
        """
        try:
            log_info("Clicking Forgot Password link")
            
            # Check if the link is visible
            if self.is_element_visible(SigninLocators.FORGOT_PASSWORD_LINK):
                result = self.click(SigninLocators.FORGOT_PASSWORD_LINK)
                
                # Wait a moment for page transition
                time.sleep(1)
                
                return result
            else:
                log_error("Forgot Password link not visible")
                return False
        except Exception as e:
            log_error(f"Failed to click Forgot Password link: {str(e)}")
            return False
    
    def click_signup_link(self):
        """
        Click the 'Sign up' link to navigate to registration page
        
        Returns:
            bool: True if link was clicked successfully, False otherwise
        """
        try:
            log_info("Clicking Sign up link")
            
            # Check if the link is visible
            if self.is_element_visible(SigninLocators.SIGNUP_LINK):
                result = self.click(SigninLocators.SIGNUP_LINK)
                
                # Wait a moment for page transition
                time.sleep(1)
                
                return result
            else:
                log_error("Sign up link not visible")
                return False
        except Exception as e:
            log_error(f"Failed to click Sign up link: {str(e)}")
            return False
    
    def complete_signin(self, email, password, remember_me=False, timeout=USER_AUTHENTICATION_TIMEOUT):
        """
        Complete the entire signin process with provided credentials
        
        Args:
            email: Email address to use
            password: Password to use
            remember_me: Whether to check the Remember Me checkbox
            timeout: Timeout for verifying successful signin
            
        Returns:
            bool: True if signin was successful, False otherwise
        """
        try:
            log_info(f"Attempting to sign in with email: {email}")
            
            # Navigate to signin page
            if not self.navigate_to():
                return False
            
            # Enter email and password
            self.enter_email(email)
            self.enter_password(password)
            
            # Check Remember Me if requested
            if remember_me:
                self.check_remember_me()
            
            # Click signin button
            self.click_signin_button()
            
            # Verify signin success
            success = self.is_signin_successful(timeout)
            
            if success:
                log_info("Signin successful")
            else:
                error_message = self.get_error_message()
                if error_message:
                    log_error(f"Signin failed with error: {error_message}")
                else:
                    log_error("Signin failed without specific error message")
            
            return success
        except Exception as e:
            log_error(f"Error in signin process: {str(e)}")
            return False