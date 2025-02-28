# src/test/tests/story_sharing/test_sharing_confirmation.py
import pytest  # pytest 7.3+
import time  # standard library
import random  # standard library

from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.story_fixtures import created_story  # src/test/fixtures/story_fixtures.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.locators.share_dialog_locators import ShareDialogLocators  # src/test/locators/share_dialog_locators.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.config.timeout_config import STORY_SHARING_TIMEOUT  # src/test/config/timeout_config.py

SUBJECT_STORY_SHARED: str = 'Story shared with you'
EMAIL_VERIFICATION_TIMEOUT: int = 60


def generate_test_message() -> str:
    """Generate a random test message for story sharing

    Returns:
        str: A randomly generated message for sharing
    """
    message_templates = [
        "Check out this awesome story!",
        "I wanted to share this with you.",
        "Hope you find this interesting!",
        "Let me know what you think."
    ]
    selected_message = random.choice(message_templates)
    return selected_message


class TestSharingConfirmation:
    """Test class for verifying story sharing confirmation functionality"""

    def __init__(self):
        """Default constructor"""
        pass

    @pytest.mark.smoke
    def test_sharing_ui_confirmation(self, browser, created_story):
        """Test that the UI displays a confirmation message after successful sharing

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):

        Returns:
            None: No return value
        """
        log_info("Starting test_sharing_ui_confirmation")

        email_helper = EmailHelper()
        recipient_email = email_helper.generate_email_address()

        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()

        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.enter_recipient_email(recipient_email)

        test_message = generate_test_message()
        share_dialog_page.enter_personal_message(test_message)

        share_dialog_page.click_share_button()

        share_dialog_page.wait_for_sharing_complete()

        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
        assert share_dialog_page.is_element_visible(ShareDialogLocators.SHARE_SUCCESS_MESSAGE), \
            "Success message is not visible in the UI"

        log_info("test_sharing_ui_confirmation completed successfully")

    @pytest.mark.integration
    def test_sharing_email_delivery(self, browser, created_story):
        """Test that sharing emails are delivered and contain the correct links

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):

        Returns:
            None: No return value
        """
        log_info("Starting test_sharing_email_delivery")

        email_helper = EmailHelper()
        recipient_email = email_helper.generate_email_address()

        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()

        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.enter_recipient_email(recipient_email)

        test_message = generate_test_message()
        share_dialog_page.enter_personal_message(test_message)

        share_dialog_page.click_share_button()

        share_dialog_page.wait_for_sharing_complete()

        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"

        assert share_dialog_page.verify_sharing_email(recipient_email), \
            "Sharing email was not delivered to recipient address"

        sharing_link = share_dialog_page.get_sharing_link(recipient_email)
        assert sharing_link is not None, "A valid sharing link was not extracted"

        log_info("test_sharing_email_delivery completed successfully")

    @pytest.mark.extended
    def test_sharing_confirmation_with_multiple_recipients(self, browser, created_story):
        """Test sharing confirmation when sharing with multiple recipients

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):

        Returns:
            None: No return value
        """
        log_info("Starting test_sharing_confirmation_with_multiple_recipients")

        email_helper = EmailHelper()
        recipient_emails = [email_helper.generate_email_address() for _ in range(3)]

        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()

        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.enter_recipient_email(recipient_emails[0])

        for email in recipient_emails[1:]:
            share_dialog_page.add_additional_recipient()
            share_dialog_page.enter_recipient_email(email)

        test_message = generate_test_message()
        share_dialog_page.enter_personal_message(test_message)

        share_dialog_page.click_share_button()

        share_dialog_page.wait_for_sharing_complete()

        assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"

        all_emails_received = all(share_dialog_page.verify_sharing_email(email) for email in recipient_emails)
        assert all_emails_received, "Not all recipients received sharing emails"

        log_info("test_sharing_confirmation_with_multiple_recipients completed successfully")

    @pytest.mark.performance
    def test_sharing_confirmation_timing(self, browser, created_story):
        """Test that sharing confirmation appears within expected time thresholds

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):

        Returns:
            None: No return value
        """
        log_info("Starting test_sharing_confirmation_timing")

        email_helper = EmailHelper()
        recipient_email = email_helper.generate_email_address()

        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()

        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.enter_recipient_email(recipient_email)

        test_message = generate_test_message()
        share_dialog_page.enter_personal_message(test_message)

        start_time = time.time()
        share_dialog_page.click_share_button()

        share_dialog_page.wait_for_sharing_complete()
        end_time = time.time()

        confirmation_time = end_time - start_time
        assert confirmation_time < 3, "Confirmation appeared slower than expected (under 3 seconds)"

        log_info(f"Sharing confirmation appeared in {confirmation_time:.2f} seconds")
        log_info("test_sharing_confirmation_timing completed successfully")

    @pytest.mark.performance
    def test_sharing_email_delivery_timing(self, browser, created_story):
        """Test that sharing emails are delivered within expected time thresholds

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):

        Returns:
            None: No return value
        """
        log_info("Starting test_sharing_email_delivery_timing")

        email_helper = EmailHelper()
        recipient_email = email_helper.generate_email_address()

        story_editor_page = StoryEditorPage(browser)
        story_editor_page.click_share_button()

        share_dialog_page = ShareDialogPage(browser)
        share_dialog_page.enter_recipient_email(recipient_email)

        test_message = generate_test_message()
        share_dialog_page.enter_personal_message(test_message)

        start_time = time.time()
        share_dialog_page.click_share_button()

        email_received = share_dialog_page.verify_sharing_email(recipient_email)
        end_time = time.time()

        delivery_time = end_time - start_time
        assert email_received, "Sharing email was not delivered"
        assert delivery_time < 30, "Email was delivered slower than expected (under 30 seconds)"

        log_info(f"Sharing email delivered in {delivery_time:.2f} seconds")
        log_info("test_sharing_email_delivery_timing completed successfully")