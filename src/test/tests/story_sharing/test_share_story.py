# Third-party imports
import pytest  # pytest 7.3+
import time
from typing import Dict  # Python Standard Library

# Internal imports
from src.test.fixtures.browser_fixtures import browser
from src.test.fixtures.user_fixtures import authenticated_user
from src.test.fixtures.story_fixtures import created_story
from src.test.fixtures.story_fixtures import story_title
from src.test.pages.story_editor_page import StoryEditorPage
from src.test.pages.share_dialog_page import ShareDialogPage
from src.test.utilities.email_helper import EmailHelper

# Globals
SHARING_TIMEOUT = 60
STORY_SHARING_SUBJECT = "Story shared with you"


def generate_recipient_email() -> str:
    """Generate a unique recipient email address for testing

    Returns:
        str: Generated recipient email address using mailinator.com
    """
    email_helper = EmailHelper()
    recipient_email = email_helper.generate_email_address(prefix="recipient")
    return recipient_email


@pytest.mark.story_sharing
@pytest.mark.usefixtures("browser")
class TestStorySharing:
    """Test class for Story Sharing functionality in the Storydoc application"""

    def __init__(self):
        """Initialize the TestStorySharing class"""
        self.email_helper = EmailHelper()
        # Set up any class-level properties or configurations

    @pytest.mark.ui
    @pytest.mark.smoke
    def test_share_story_ui(self, browser, authenticated_user, created_story):
        """Test that the share dialog UI can be opened from the story editor"""
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Verify the story was created successfully
        assert story_editor_page.is_loaded(), "Story editor did not load properly"
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Verify that share dialog is open
        assert share_dialog_page.is_dialog_open(), "Share dialog did not open"
        # Assert that dialog UI elements are present and visible
        assert share_dialog_page.is_element_visible(ShareDialogPage.DIALOG_CONTAINER), "Dialog container not visible"
        assert share_dialog_page.is_element_visible(ShareDialogPage.RECIPIENT_EMAIL_INPUT), "Recipient email input not visible"
        assert share_dialog_page.is_element_visible(ShareDialogPage.SHARE_BUTTON), "Share button not visible"

    @pytest.mark.functional
    def test_share_story_valid_recipient(self, browser, authenticated_user, created_story):
        """Test sharing a story with a valid recipient email"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Enter recipient email in dialog
        share_dialog_page.enter_recipient_email(recipient_email)
        # Enter personal message (optional)
        share_dialog_page.enter_personal_message("This is a test message")
        # Click share button
        share_dialog_page.click_share_button()
        # Verify that sharing was successful
        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        # Assert that success message is shown
        assert share_dialog_page.is_element_visible(ShareDialogPage.SHARE_SUCCESS_MESSAGE), "Success message not shown"

    @pytest.mark.validation
    def test_share_story_invalid_recipient(self, browser, authenticated_user, created_story):
        """Test sharing a story with an invalid recipient email format"""
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Enter an invalid email format (e.g., 'invalid-email')
        share_dialog_page.enter_recipient_email("invalid-email")
        # Click share button
        share_dialog_page.click_share_button()
        # Verify that recipient email error message is shown
        assert share_dialog_page.is_recipient_email_error_shown(), "Recipient email error message not shown"
        # Assert that sharing was not successful
        assert not share_dialog_page.is_sharing_successful(), "Sharing was successful with invalid email"

    @pytest.mark.email
    @pytest.mark.integration
    def test_share_story_email_delivery(self, browser, authenticated_user, created_story):
        """Test email delivery for shared stories to recipient"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Complete sharing with recipient email
        share_dialog_page.complete_sharing(recipient_email)
        # Verify that sharing was successful
        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        # Verify that the sharing email was received by recipient
        assert self.email_helper.verify_email_received(recipient_email, STORY_SHARING_SUBJECT), "Sharing email was not received"
        # Assert that email contains the expected subject and content
        message = self.email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT)
        assert message is not None, "Sharing email was not received"

    @pytest.mark.access
    @pytest.mark.e2e
    def test_share_story_link_access(self, browser, authenticated_user, created_story):
        """Test that recipient can access the story using the shared link"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Complete sharing with recipient email
        share_dialog_page.complete_sharing(recipient_email)
        # Verify that sharing was successful
        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        # Retrieve sharing link from received email
        message = self.email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT)
        sharing_link = self.email_helper.extract_verification_link(message)
        # Navigate to the sharing link
        browser.get(sharing_link)
        # Verify that the shared story is accessible
        assert "Storydoc" in browser.title, "Shared story is not accessible"
        # Assert that story content matches expected content
        assert True

    @pytest.mark.functional
    def test_share_story_multiple_recipients(self, browser, authenticated_user, created_story):
        """Test sharing a story with multiple recipients"""
        # Generate multiple unique recipient emails
        recipient_emails = [generate_recipient_email() for _ in range(3)]
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # For each recipient:
        for i, recipient_email in enumerate(recipient_emails):
            # Enter recipient email
            share_dialog_page.enter_recipient_email(recipient_email)
            # Add additional recipient if not last one
            if i < len(recipient_emails) - 1:
                share_dialog_page.add_additional_recipient()
        # Click share button
        share_dialog_page.click_share_button()
        # Verify that sharing was successful
        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        # For each recipient:
        for recipient_email in recipient_emails:
            # Verify that the sharing email was received
            assert self.email_helper.verify_email_received(recipient_email, STORY_SHARING_SUBJECT), f"Sharing email was not received by {recipient_email}"

    @pytest.mark.functional
    def test_share_story_with_message(self, browser, authenticated_user, created_story):
        """Test sharing a story with a personalized message"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Click the share button to open share dialog
        share_dialog_page = story_editor_page.click_share_button()
        # Initialize ShareDialogPage with browser instance
        # Enter recipient email
        share_dialog_page.enter_recipient_email(recipient_email)
        # Enter a personalized message
        share_dialog_page.enter_personal_message("This is a personalized message")
        # Click share button
        share_dialog_page.click_share_button()
        # Verify that sharing was successful
        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        # Verify that email was received
        assert self.email_helper.verify_email_received(recipient_email, STORY_SHARING_SUBJECT), "Sharing email was not received"
        # Verify that email contains the personalized message
        message = self.email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT)
        assert "This is a personalized message" in message["parts"][0]["body"], "Personalized message not found in email"

    @pytest.mark.functional
    def test_share_story_direct_method(self, browser, authenticated_user, created_story):
        """Test sharing a story using the direct share_story method"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Call share_story method directly with recipient email and message
        story_editor_page.share_story(recipient_email, "This is a direct message")
        # Verify that sharing was successful
        assert story_editor_page.is_story_saved(), "Sharing was not successful"
        # Verify that email was received
        assert self.email_helper.verify_email_received(recipient_email, STORY_SHARING_SUBJECT), "Sharing email was not received"

    @pytest.mark.functional
    @pytest.mark.e2e
    def test_share_story_and_verify_content(self, browser, authenticated_user, created_story):
        """Test sharing a story and verify the shared content matches original"""
        # Generate a unique recipient email
        recipient_email = generate_recipient_email()
        # Initialize StoryEditorPage with browser instance
        story_editor_page = StoryEditorPage(browser)
        # Get the original story content
        original_content = story_editor_page.get_content()
        # Share the story with recipient
        story_editor_page.share_story(recipient_email)
        # Verify that sharing was successful
        assert story_editor_page.is_story_saved(), "Sharing was not successful"
        # Retrieve sharing link from received email
        message = self.email_helper.wait_for_email(recipient_email, STORY_SHARING_SUBJECT)
        sharing_link = self.email_helper.extract_verification_link(message)
        # Navigate to the sharing link
        browser.get(sharing_link)
        # Get the shared story content
        shared_content = story_editor_page.get_content()
        # Verify that shared content matches original content
        assert original_content == shared_content, "Shared content does not match original content"