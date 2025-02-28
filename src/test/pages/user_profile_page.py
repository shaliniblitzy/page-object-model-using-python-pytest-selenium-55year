from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage, ELEMENT_STATE_VISIBLE, ELEMENT_STATE_CLICKABLE
from ..locators.user_profile_locators import UserProfileLocators
from ..utilities.wait_helper import WaitUtils
from ..utilities.logger import log_info, log_error, log_debug


class UserProfilePage(BasePage):
    """Page object representing the user profile page in the Storydoc application"""
    
    url = "https://editor-staging.storydoc.com/settings/profile"

    def __init__(self, driver: WebDriver):
        """Initialize the UserProfilePage object
        
        Args:
            driver: WebDriver instance for browser interaction
        """
        super().__init__(driver)
        log_info("UserProfilePage initialized")
    
    def is_profile_page_loaded(self) -> bool:
        """Check if the profile page is loaded
        
        Returns:
            bool: True if profile page is loaded, False otherwise
        """
        try:
            # Wait for profile settings elements to be visible
            WaitUtils.wait_for_element_state(
                self.driver, 
                UserProfileLocators.DISPLAY_NAME_FIELD, 
                ELEMENT_STATE_VISIBLE
            )
            
            # Check if display name field is visible
            is_loaded = self.is_element_visible(UserProfileLocators.DISPLAY_NAME_FIELD)
            
            # Log result
            log_debug(f"Profile page loaded: {is_loaded}")
            
            return is_loaded
        except TimeoutException:
            log_error("Timeout waiting for profile page to load")
            return False
    
    def navigate_to(self) -> bool:
        """Navigate to the user profile page
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        # Call the open method from BasePage
        self.open()
        
        # Wait for page to be ready
        WaitUtils.wait_for_page_ready(self.driver)
        
        # Call is_profile_page_loaded to verify page loaded correctly
        is_loaded = self.is_profile_page_loaded()
        
        # Log result
        log_info(f"Navigation to profile page {'' if is_loaded else 'un'}successful")
        
        return is_loaded
    
    def navigate_from_menu(self) -> bool:
        """Navigate to profile page through the profile menu
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            # Click on profile menu button
            self.click(UserProfileLocators.PROFILE_MENU_BUTTON)
            
            # Click on profile settings link
            self.click(UserProfileLocators.PROFILE_SETTINGS_LINK)
            
            # Wait for profile page to load
            WaitUtils.wait_for_page_ready(self.driver)
            
            # Verify profile page loaded
            is_loaded = self.is_profile_page_loaded()
            
            # Log result
            log_info(f"Navigation from menu {'' if is_loaded else 'un'}successful")
            
            return is_loaded
        except Exception as e:
            log_error(f"Error navigating from menu: {str(e)}")
            return False
    
    def get_display_name(self) -> str:
        """Get the current display name from the profile
        
        Returns:
            str: Current display name or empty string if not found
        """
        display_name = self.get_text(UserProfileLocators.DISPLAY_NAME_FIELD)
        log_debug(f"Retrieved display name: {display_name}")
        return display_name
    
    def get_email(self) -> str:
        """Get the email address from the profile
        
        Returns:
            str: Email address or empty string if not found
        """
        email = self.get_text(UserProfileLocators.EMAIL_FIELD)
        log_debug(f"Retrieved email: {email}")
        return email
    
    def update_display_name(self, new_name: str) -> bool:
        """Update the display name in the profile
        
        Args:
            new_name: New display name to set
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Input new text into display name field
            self.input_text(UserProfileLocators.DISPLAY_NAME_FIELD, new_name)
            
            # Click save profile button
            self.click(UserProfileLocators.SAVE_PROFILE_BUTTON)
            
            # Check for profile updated message
            success = self.is_profile_update_successful()
            
            # Log result
            log_info(f"Display name update {'' if success else 'un'}successful: {new_name}")
            
            return success
        except Exception as e:
            log_error(f"Error updating display name: {str(e)}")
            return False
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change the user's password
        
        Args:
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password change was successful, False otherwise
        """
        try:
            # Input current password into current password field
            self.input_text(UserProfileLocators.CURRENT_PASSWORD_FIELD, current_password)
            
            # Input new password into new password field
            self.input_text(UserProfileLocators.NEW_PASSWORD_FIELD, new_password)
            
            # Input new password into confirm password field
            self.input_text(UserProfileLocators.CONFIRM_PASSWORD_FIELD, new_password)
            
            # Click change password button
            self.click(UserProfileLocators.CHANGE_PASSWORD_BUTTON)
            
            # Check for password updated message
            success = self.is_password_update_successful()
            
            # Log result
            log_info(f"Password change {'' if success else 'un'}successful")
            
            return success
        except Exception as e:
            log_error(f"Error changing password: {str(e)}")
            return False
    
    def toggle_email_notifications(self, enable: bool) -> bool:
        """Toggle email notifications setting
        
        Args:
            enable: True to enable notifications, False to disable
            
        Returns:
            bool: True if toggle was successful, False otherwise
        """
        try:
            # Get current state of notifications toggle
            current_state = self.is_email_notifications_enabled()
            
            # If current state doesn't match desired state, click toggle
            if current_state != enable:
                self.click(UserProfileLocators.EMAIL_NOTIFICATIONS_TOGGLE)
            
            # Click save profile button
            self.click(UserProfileLocators.SAVE_PROFILE_BUTTON)
            
            # Check for profile updated message
            success = self.is_profile_update_successful()
            
            # Log result
            log_info(f"Email notifications toggle to {enable} {'' if success else 'un'}successful")
            
            return success
        except Exception as e:
            log_error(f"Error toggling email notifications: {str(e)}")
            return False
    
    def is_email_notifications_enabled(self) -> bool:
        """Check if email notifications are enabled
        
        Returns:
            bool: True if notifications are enabled, False otherwise
        """
        try:
            # Get the notification toggle element
            toggle_element = self.find_element(UserProfileLocators.EMAIL_NOTIFICATIONS_TOGGLE)
            
            # Check if the toggle is in 'on' state
            # This implementation might vary depending on how the toggle is implemented in the UI
            # Here we're checking for an 'active' class, but it could be a different attribute
            is_enabled = "active" in toggle_element.get_attribute("class")
            
            # Log the notification status
            log_debug(f"Email notifications enabled: {is_enabled}")
            
            return is_enabled
        except Exception as e:
            log_error(f"Error checking email notifications status: {str(e)}")
            return False
    
    def delete_account(self, confirm: bool) -> bool:
        """Delete the user account
        
        Args:
            confirm: True to confirm deletion, False to cancel
            
        Returns:
            bool: True if account deletion was initiated, False otherwise
        """
        try:
            # Click delete account button
            self.click(UserProfileLocators.DELETE_ACCOUNT_BUTTON)
            
            # If confirm is True, click confirm delete button
            if confirm:
                self.click(UserProfileLocators.CONFIRM_DELETE_BUTTON)
                log_info("Account deletion confirmed")
                return True
            # If confirm is False, cancel the delete operation
            else:
                # Click cancel button if available
                if self.is_element_visible(UserProfileLocators.CANCEL_DELETE_BUTTON):
                    self.click(UserProfileLocators.CANCEL_DELETE_BUTTON)
                else:
                    # Use JavaScript to simulate ESC key press
                    self.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Escape'}));")
                
                log_info("Account deletion canceled")
                return True
        except Exception as e:
            log_error(f"Error during account deletion process: {str(e)}")
            return False
    
    def is_profile_update_successful(self) -> bool:
        """Check if the profile was updated successfully
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Check for profile updated message
        success = self.is_element_visible(UserProfileLocators.PROFILE_UPDATED_MESSAGE)
        
        # Log result
        log_debug(f"Profile update {'' if success else 'un'}successful")
        
        return success
    
    def is_password_update_successful(self) -> bool:
        """Check if the password was updated successfully
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Check for password updated message
        success = self.is_element_visible(UserProfileLocators.PASSWORD_UPDATED_MESSAGE)
        
        # Log result
        log_debug(f"Password update {'' if success else 'un'}successful")
        
        return success