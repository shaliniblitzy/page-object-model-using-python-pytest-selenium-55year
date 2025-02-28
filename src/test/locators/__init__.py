"""
Package initialization file for the locators module that imports and exposes all locator classes
used for Selenium element identification in the Storydoc test automation framework. This allows
importing locators directly from the locators package with clean imports.
"""

# Import all locator classes
from .base_locators import BaseLocators
from .signup_locators import SignupLocators
from .signin_locators import SigninLocators
from .dashboard_locators import DashboardLocators
from .story_editor_locators import StoryEditorLocators
from .share_dialog_locators import ShareDialogLocators
from .error_locators import ErrorLocators
from .mailinator_locators import MailinatorLocators
from .shared_story_locators import SharedStoryLocators
from .verification_locators import VerificationLocators
from .template_selection_locators import TemplateSelectionLocators
from .notification_locators import NotificationLocators
from .user_profile_locators import UserProfileLocators

# Define what gets imported with "from locators import *"
__all__ = [
    'BaseLocators',
    'SignupLocators',
    'SigninLocators',
    'DashboardLocators',
    'StoryEditorLocators',
    'ShareDialogLocators',
    'ErrorLocators',
    'MailinatorLocators',
    'SharedStoryLocators',
    'VerificationLocators',
    'TemplateSelectionLocators',
    'NotificationLocators',
    'UserProfileLocators',
]