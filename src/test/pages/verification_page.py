from selenium.webdriver.remote.webdriver import WebDriver  # version: 4.10+
import time

from .base_page import BasePage
from ..locators.verification_locators import VerificationLocators
from ..config.urls import get_verification_url, get_shared_story_url
from ..utilities.logger import log_info, log_error


class VerificationPage(BasePage):
    """
    Page object for the verification page in the Storydoc application.
    Handles email verification during registration and story sharing processes.
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize the verification page object
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.page_name = "Verification Page"
        # URL is set dynamically based on verification token
    
    def navigate_to_verification(self, token: str) -> bool:
        """
        Navigate to the verification page using a verification token
        
        Args:
            token: Verification token
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            # Construct the verification URL using the token
            verification_url = get_verification_url(token)
            self.url = verification_url
            
            # Navigate to the verification page
            log_info(f"Navigating to verification page with token: {token}")
            success = self.open()
            
            # Wait for the page to be ready
            if success:
                return self.is_verification_page_displayed()
            return False
        except Exception as e:
            log_error(f"Failed to navigate to verification page: {str(e)}")
            self.take_screenshot(f"verification_navigation_error_{token[:8]}")
            return False
    
    def navigate_to_shared_story(self, token: str) -> bool:
        """
        Navigate to a shared story using a sharing token
        
        Args:
            token: Sharing token
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            # Construct the shared story URL using the token
            shared_story_url = get_shared_story_url(token)
            self.url = shared_story_url
            
            # Navigate to the shared story page
            log_info(f"Navigating to shared story with token: {token}")
            success = self.open()
            
            # Wait for the page to be ready
            return success
        except Exception as e:
            log_error(f"Failed to navigate to shared story: {str(e)}")
            self.take_screenshot(f"shared_story_navigation_error_{token[:8]}")
            return False
    
    def is_verification_page_displayed(self) -> bool:
        """
        Check if the verification page is displayed
        
        Returns:
            True if verification page is displayed, False otherwise
        """
        return self.is_element_visible(VerificationLocators.EMAIL_VERIFICATION_HEADING)
    
    def is_account_verified(self) -> bool:
        """
        Check if the account has been successfully verified
        
        Returns:
            True if account is verified, False otherwise
        """
        return self.is_element_visible(VerificationLocators.ACCOUNT_VERIFIED_MESSAGE)
    
    def is_verification_link_expired(self) -> bool:
        """
        Check if the verification link has expired
        
        Returns:
            True if verification link is expired, False otherwise
        """
        return self.is_element_visible(VerificationLocators.VERIFICATION_LINK_EXPIRED)
    
    def continue_to_dashboard(self) -> bool:
        """
        Click the continue to dashboard button after successful verification
        
        Returns:
            True if button was clicked successfully, False otherwise
        """
        if self.is_account_verified():
            log_info("Account verification successful. Continuing to dashboard...")
            return self.click(VerificationLocators.CONTINUE_TO_DASHBOARD_BUTTON)
        else:
            log_error("Cannot continue to dashboard: Account verification not confirmed")
            self.take_screenshot("continue_to_dashboard_error")
            return False
    
    def resend_verification_email(self) -> bool:
        """
        Click the resend verification button if verification link expired
        
        Returns:
            True if resend button was clicked successfully, False otherwise
        """
        if self.is_verification_link_expired():
            log_info("Verification link expired. Resending verification email...")
            return self.click(VerificationLocators.RESEND_VERIFICATION_BUTTON)
        else:
            log_error("Cannot resend verification email: Link not expired")
            self.take_screenshot("resend_verification_error")
            return False
    
    def get_verification_status_message(self) -> str:
        """
        Get the current verification status message displayed on the page
        
        Returns:
            Status message text or empty string if not found
        """
        if self.is_account_verified():
            return self.get_text(VerificationLocators.ACCOUNT_VERIFIED_MESSAGE)
        elif self.is_verification_link_expired():
            return self.get_text(VerificationLocators.VERIFICATION_LINK_EXPIRED)
        elif self.is_element_visible(VerificationLocators.EMAIL_VERIFICATION_ERROR_MESSAGE):
            return self.get_text(VerificationLocators.EMAIL_VERIFICATION_ERROR_MESSAGE)
        return ""
    
    def is_shared_story_access_successful(self) -> bool:
        """
        Check if shared story access was successful
        
        Returns:
            True if shared story access is successful, False otherwise
        """
        return self.is_element_visible(VerificationLocators.SHARED_STORY_ACCESS_SUCCESS)
    
    def wait_for_verification_completion(self, timeout: float = 30.0) -> bool:
        """
        Wait for the verification process to complete
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if verification completed successfully, False otherwise
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            if self.is_account_verified():
                log_info("Account verification completed successfully")
                return True
            elif self.is_verification_link_expired():
                log_error("Verification link has expired")
                return False
            
            # Wait a short time before checking again
            time.sleep(1)
        
        log_error(f"Verification did not complete within timeout ({timeout}s)")
        self.take_screenshot("verification_timeout")
        return False
    
    def complete_verification(self, token: str) -> bool:
        """
        Complete the verification process from start to finish
        
        Args:
            token: Verification token
            
        Returns:
            True if verification was successfully completed, False otherwise
        """
        # Navigate to the verification page
        if not self.navigate_to_verification(token):
            log_error("Failed to navigate to verification page")
            return False
        
        # Wait for verification to complete
        if not self.wait_for_verification_completion():
            log_error("Verification process failed or timed out")
            return False
        
        # If verification was successful, continue to dashboard
        if self.is_account_verified():
            log_info("Verification completed successfully, continuing to dashboard")
            return self.continue_to_dashboard()
        
        log_error("Verification failed: account is not verified")
        self.take_screenshot("verification_failure")
        return False