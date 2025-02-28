from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators

class NotificationLocators(BaseLocators):
    """
    Defines locators for notification elements in the Storydoc application.
    These locators are used to identify and interact with various types of notifications
    that appear during user workflows such as success messages, error alerts, and 
    informational notifications.
    """
    
    # General notification types
    SUCCESS_NOTIFICATION = (By.CSS_SELECTOR, ".notification.notification--success")
    ERROR_NOTIFICATION = (By.CSS_SELECTOR, ".notification.notification--error")
    INFO_NOTIFICATION = (By.CSS_SELECTOR, ".notification.notification--info")
    WARNING_NOTIFICATION = (By.CSS_SELECTOR, ".notification.notification--warning")
    
    # Notification components
    NOTIFICATION_TITLE = (By.CSS_SELECTOR, ".notification__title")
    NOTIFICATION_MESSAGE = (By.CSS_SELECTOR, ".notification__message")
    NOTIFICATION_CLOSE_BUTTON = (By.CSS_SELECTOR, ".notification__close")
    NOTIFICATION_CONTAINER = (By.CSS_SELECTOR, ".notification-container")
    
    # Specific notification messages for user workflows
    
    # User Registration (F-001-RQ-004)
    SIGNUP_SUCCESS_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='signup-success']")
    
    # User Authentication (F-002-RQ-003)
    SIGNIN_SUCCESS_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='signin-success']")
    
    # Story Creation (F-003-RQ-003)
    STORY_SAVED_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='story-saved']")
    
    # Story Sharing (F-004-RQ-001)
    STORY_SHARED_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='story-shared']")
    EMAIL_SENT_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='email-sent']")
    
    # Form validation error notifications
    FORM_ERROR_NOTIFICATION = (By.CSS_SELECTOR, ".notification[data-test='form-error']")