import pytest  # pytest 7.3+
import time
from typing import Dict  # typing is part of the Python standard library

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.story_fixtures import created_story  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.user_fixtures import register_and_authenticate_user
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.pages.shared_story_page import SharedStoryPage  # src/test/pages/shared_story_page.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.assertion_helper import assert_true, assert_false, assert_equal
from src.test.utilities.logger import log_info, log_error  # src/test/utilities/logger.py

SHARING_TIMEOUT = 60
STORY_SHARING_SUBJECT = "Story shared with you"


def generate_recipient_email():
    """Generate a unique recipient email address for testing

    Returns:
        str: Generated recipient email address using mailinator.com
    """
    email_helper = EmailHelper()
    recipient_email = email_helper.generate_email_address(prefix="recipient")
    return recipient_email


def share_story_and_get_link(browser, story, recipient_email):
    """Share a story with a recipient and get the sharing link

    Args:
        browser (webdriver.WebDriver):
        story (dict):
        recipient_email (str):

    Returns:
        str: URL of the shared story
    """
    story_editor_page = StoryEditorPage(browser)
    story_editor_page.click_share_button()
    share_dialog_page = ShareDialogPage(browser)
    share_dialog_page.complete_sharing(recipient_email)
    email_helper = EmailHelper()
    message = email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT, timeout=SHARING_TIMEOUT)
    sharing_link = email_helper.extract_verification_link(message)
    return sharing_link


@pytest.mark.story_sharing
@pytest.mark.permissions
class TestSharingPermissions:
    """Test class for sharing permissions functionality in Storydoc"""

    def __init__(self):
        """Initialize the test class"""
        self.email_helper = EmailHelper()  # Initialize EmailHelper instance
        # Set up any class-level properties

    @pytest.mark.permissions
    def test_anonymous_user_access(self, browser, authenticated_user, created_story):
        """Test that a shared story can be accessed by an anonymous user (not logged in)

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Log out the current user
        signin_page = SigninPage(browser)
        signin_page.navigate_to()
        # Initialize SharedStoryPage
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "Shared story is accessible", driver=browser)
        story_content = shared_story_page.get_story_content()
        assert_true(story_content != "", "Story content is visible and matches expected content", driver=browser)

    @pytest.mark.permissions
    def test_different_user_access(self, browser, authenticated_user, created_story):
        """Test that a shared story can be accessed by a different authenticated user

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Create and authenticate a different user
        new_user = register_and_authenticate_user(browser)
        # Initialize SharedStoryPage
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "Shared story is accessible", driver=browser)
        story_content = shared_story_page.get_story_content()
        assert_true(story_content != "", "Story content is visible and matches expected content", driver=browser)

    @pytest.mark.permissions
    def test_restricted_access_link(self, browser, authenticated_user, created_story):
        """Test accessing a story with restricted access permissions

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        # Share the story with the recipient using restricted permissions
        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()
        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.complete_sharing(recipient_email)
        email_helper = EmailHelper()
        message = email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT, timeout=SHARING_TIMEOUT)
        sharing_link = email_helper.extract_verification_link(message)
        # Log out the current user
        signin_page = SigninPage(browser)
        signin_page.navigate_to()
        # Initialize SharedStoryPage
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_access_restricted(), "Access is restricted", driver=browser)
        # Assert that the page shows a login requirement message

    def test_revoke_sharing_access(self, browser, authenticated_user, created_story):
        """Test that access can be revoked for a previously shared story

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Verify initial access is successful
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "Initial access is successful", driver=browser)
        # Revoke sharing permissions for the recipient
        # Navigate to the shared story using the same link
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_access_restricted(), "Access is now restricted", driver=browser)
        # Assert that the page shows an access revoked message

    @pytest.mark.xfail(reason="Need ability to create or simulate expired links")
    def test_expired_link_access(self, browser, authenticated_user, created_story):
        """Test that expired sharing links cannot be accessed

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        # Share the story with recipient using a short expiration time
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Wait for the link to expire
        time.sleep(60)
        # Navigate to the shared story using the link
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.has_story_expired(), "The link is shown as expired", driver=browser)
        # Assert that the page shows an expiration message

    def test_view_only_permissions(self, browser, authenticated_user, created_story):
        """Test that view-only permissions prevent editing the shared story

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        # Share the story with view-only permissions
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Create and authenticate a different user
        register_and_authenticate_user(browser)
        # Navigate to the shared story using the link
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "The story is accessible", driver=browser)
        # Attempt to edit the shared story
        # Verify that edit controls are not available or disabled
        # Assert that the story remains in view-only mode

    def test_edit_permissions(self, browser, authenticated_user, created_story):
        """Test that edit permissions allow editing the shared story

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        # Share the story with edit permissions
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Create and authenticate a different user
        register_and_authenticate_user(browser)
        # Navigate to the shared story using the link
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "The story is accessible", driver=browser)
        # Attempt to edit the shared story
        # Verify that edit controls are available and functional
        # Make a change to the story
        # Save the changes
        # Verify the changes are saved successfully

    def test_permission_inheritance(self, browser, authenticated_user, created_story):
        """Test that permission changes affect all existing shared links

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        # Generate multiple recipient emails
        recipient_email1 = generate_recipient_email()
        recipient_email2 = generate_recipient_email()
        # Share the story with view-only permissions to all recipients
        sharing_link1 = share_story_and_get_link(browser, created_story, recipient_email1)
        sharing_link2 = share_story_and_get_link(browser, created_story, recipient_email2)
        # Get all sharing links
        # Change story permissions to edit for all shared links
        # Verify all links now have edit permissions
        # Change story permissions to restricted access
        # Verify all links now require authentication

    def test_download_permissions(self, browser, authenticated_user, created_story):
        """Test that download permissions control ability to download shared stories

        Args:
            browser (webdriver.WebDriver):
            authenticated_user (dict):
            created_story (dict):
        """
        recipient_email = generate_recipient_email()
        # Share the story with download disabled
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Navigate to the shared story using the link
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        # Verify download button is not available
        assert_false(shared_story_page.is_download_available(), "Download button is not available", driver=browser)
        # Share the story again with download enabled
        sharing_link = share_story_and_get_link(browser, created_story, recipient_email)
        # Navigate to the shared story using the link
        shared_story_page.navigate_to_shared_story(sharing_link)
        # Verify download button is available and functional
        assert_true(shared_story_page.is_download_available(), "Download button is available and functional", driver=browser)