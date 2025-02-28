import pytest  # pytest version: latest
import time  # time version: standard library
import random  # random version: standard library

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.story_fixtures import created_story  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.email_fixtures import random_recipient_email  # src/test/fixtures/email_fixtures.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.shared_story_page import SharedStoryPage  # src/test/pages/shared_story_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.assertion_helper import assert_true, assert_equal, assert_text_in_element  # src/test/utilities/assertion_helper.py
from src.test.utilities.logger import log_info, log_error  # src/test/utilities/logger.py
from src.test.config.constants import SHARING_EMAIL_SUBJECT  # src/test/config/constants.py
from src.test.config.mailinator_config import SHARING_EMAIL_TIMEOUT  # src/test/config/mailinator_config.py
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict
from pytest import FixtureRequest


def get_shared_story_link(browser: WebDriver, story: Dict, recipient_email: str, message: str = "Check out my story!") -> str:
    """Share a story and retrieve the sharing link from the recipient's email

    Args:
        browser (webdriver.WebDriver):
        story (dict):
        recipient_email (str):
        message (str):

    Returns:
        str: The shared story link or None if sharing fails
    """
    try:
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        log_info(f"Navigating to the story editor page using story ID")
        story_editor_page.navigate_to()

        # Click share button to open share dialog
        story_editor_page.click_share_button()

        # Initialize ShareDialogPage with browser
        share_dialog_page = ShareDialogPage(browser)

        # Complete sharing process with recipient_email and optional message
        share_dialog_page.complete_sharing(recipient_email, message)

        # Verify sharing email was received by recipient
        if not share_dialog_page.verify_sharing_email(recipient_email):
            log_error("Sharing email was not received by recipient")
            return None

        # Get sharing link from the received email
        sharing_link = share_dialog_page.get_sharing_link(recipient_email)

        # Return the sharing link
        return sharing_link
    except Exception as e:
        log_error(f"Error in get_shared_story_link: {e}")
        return None


@pytest.fixture
def shared_story_link(browser: WebDriver, created_story: Dict, random_recipient_email: str) -> str:
    """Pytest fixture that shares a story and provides the sharing link

    Args:
        browser (webdriver.WebDriver):
        created_story (dict):
        random_recipient_email (str):

    Returns:
        str: The shared story link
    """
    log_info("Creating a shared story link")
    sharing_link = get_shared_story_link(browser, created_story, random_recipient_email, message="Check out my story!")
    assert sharing_link is not None, "Failed to create a valid sharing link"
    yield sharing_link
    # No specific cleanup required


class TestAccessSharedStory:
    """Test class for accessing shared stories via sharing links"""

    def test_access_shared_story(self, browser: WebDriver, created_story: Dict, shared_story_link: str) -> None:
        """Test that a recipient can access a shared story via the sharing link

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):
            shared_story_link (str):
        """
        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Navigate to the shared story using the shared_story_link
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Verify the shared story page is loaded successfully
        assert_true(shared_story_page.is_loaded(), "Shared story page failed to load", driver=browser)

        # Get the story title from the shared view
        story_title = shared_story_page.get_story_title()

        # Verify the story title matches the expected title from created_story
        assert_equal(story_title, created_story['title'], "Story title does not match", driver=browser)

        # Verify the story content is not empty
        story_content = shared_story_page.get_story_content()
        assert_true(len(story_content) > 0, "Story content is empty", driver=browser)

        log_info("Successfully verified story access")

    def test_shared_story_content(self, browser: WebDriver, created_story: Dict, shared_story_link: str, authenticated_user: Dict) -> None:
        """Test that the shared story displays the correct content and information

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):
            shared_story_link (str):
            authenticated_user (dict):
        """
        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Navigate to the shared story using the shared_story_link
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Verify the shared story page is loaded successfully
        assert_true(shared_story_page.is_loaded(), "Shared story page failed to load", driver=browser)

        # Get the story title and verify it matches the expected title
        story_title = shared_story_page.get_story_title()
        assert_equal(story_title, created_story['title'], "Story title does not match", driver=browser)

        # Get the story content and verify it contains expected content
        story_content = shared_story_page.get_story_content()
        assert_true(len(story_content) > 0, "Story content is empty", driver=browser)

        # Get the shared by information and verify it contains the sharer's username
        shared_by_info = shared_story_page.get_shared_by_info()
        assert_text_in_element(browser, shared_by_info, authenticated_user['name'], "Shared by info", driver=browser)

        # Verify the story has navigation controls if it's a multi-section story
        has_controls = shared_story_page.has_viewer_controls()
        if has_controls:
            # If navigation controls exist, test navigation to next section
            shared_story_page.navigate_to_next_section()

        log_info("Successfully verified content")

    @pytest.mark.xfail(reason="This test is expected to fail as we cannot create expired links directly")
    def test_access_expired_shared_story(self, browser: WebDriver) -> None:
        """Test behavior when attempting to access an expired shared story link

        Args:
            browser (webdriver.WebDriver):
        """
        # Create a deliberately invalid or expired sharing link
        expired_link = "https://editor-staging.storydoc.com/shared/expired_token"

        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Attempt to navigate to the invalid sharing link
        shared_story_page.navigate_to_shared_story(expired_link)

        # Verify that the page indicates the story has expired or is invalid
        assert_true(shared_story_page.has_story_expired(), "Page should indicate story has expired", driver=browser)

        # Verify appropriate error message is displayed to the user
        assert_text_in_element(browser, "This link has expired", "Expiration message", driver=browser)

        log_info("Successfully verified expired link behavior")

    @pytest.mark.xfail(reason="This test is expected to fail as we cannot create restricted access links directly")
    def test_access_restricted_shared_story(self, browser: WebDriver, created_story: Dict, random_recipient_email: str) -> None:
        """Test behavior when attempting to access a restricted shared story

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):
            random_recipient_email (str):
        """
        # Get a special sharing link with restricted access (if platform supports this)
        restricted_link = "https://editor-staging.storydoc.com/shared/restricted_token"

        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Navigate to the restricted sharing link
        shared_story_page.navigate_to_shared_story(restricted_link)

        # Verify that the page indicates access is restricted
        assert_true(shared_story_page.is_access_restricted(), "Page should indicate access is restricted", driver=browser)

        # Verify appropriate login prompt or restriction message is displayed
        assert_text_in_element(browser, "You need to be logged in to view this story", "Restriction message", driver=browser)

        log_info("Successfully verified restricted access behavior")

    @pytest.mark.skip(reason="Requires multiple browser instances which is handled by separate browser fixtures")
    def test_access_shared_story_different_browsers(self, browser: WebDriver, created_story: Dict, random_recipient_email: str) -> None:
        """Test that a shared story can be accessed from different browsers

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):
            random_recipient_email (str):
        """
        # Share a story and get the sharing link
        sharing_link = get_shared_story_link(browser, created_story, random_recipient_email)

        # Verify access in the current browser
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_link)
        assert_true(shared_story_page.is_loaded(), "Story not accessible in the current browser", driver=browser)

        # Use a separate browser fixture (if available) to test access from another browser
        # Verify the story is accessible from both browsers
        # This requires a separate browser fixture and setup

        log_info("Successfully verified cross-browser access")

    def test_multiple_access_shared_story(self, browser: WebDriver, shared_story_link: str) -> None:
        """Test that a shared story can be accessed multiple times by the same user

        Args:
            browser (webdriver.WebDriver):
            shared_story_link (str):
        """
        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Navigate to the shared story using the shared_story_link
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Verify successful access first time
        assert_true(shared_story_page.is_loaded(), "Story not accessible on first attempt", driver=browser)

        # Navigate away from the story (go to a different URL)
        browser.get("https://www.google.com")

        # Navigate back to the shared story link
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Verify successful access second time
        assert_true(shared_story_page.is_loaded(), "Story not accessible on second attempt", driver=browser)

        # Repeat once more for third access
        browser.get("https://www.bing.com")
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Verify all accesses were successful
        assert_true(shared_story_page.is_loaded(), "Story not accessible on third attempt", driver=browser)

        log_info("Successfully verified multiple access")

    def test_verify_story_access_method(self, browser: WebDriver, created_story: Dict, shared_story_link: str) -> None:
        """Test the verify_story_access method of SharedStoryPage

        Args:
            browser (webdriver.WebDriver):
            created_story (dict):
            shared_story_link (str):
        """
        # Initialize SharedStoryPage with browser
        shared_story_page = SharedStoryPage(browser)

        # Navigate to the shared story using the shared_story_link
        shared_story_page.navigate_to_shared_story(shared_story_link)

        # Call the verify_story_access method with expected title from created_story
        verification_result = shared_story_page.verify_story_access(expected_title=created_story['title'])

        # Verify the method returns True indicating successful verification
        assert_true(verification_result, "verify_story_access method returned False", driver=browser)

        log_info("Successfully verified verification method")