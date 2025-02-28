# src/test/tests/end_to_end/test_story_lifecycle.py
import pytest  # pytest 7.3+
import time
from typing import Dict  # built-in

# Internal imports
from ...fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from ...fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from ...fixtures.story_fixtures import story_title  # src/test/fixtures/story_fixtures.py
from ...fixtures.story_fixtures import story_content  # src/test/fixtures/story_fixtures.py
from ...fixtures.story_fixtures import create_story  # src/test/fixtures/story_fixtures.py
from ...fixtures.story_fixtures import delete_stories  # src/test/fixtures/story_fixtures.py
from ...fixtures.email_fixtures import sharing_email  # src/test/fixtures/email_fixtures.py
from ...fixtures.email_fixtures import email_helper  # src/test/fixtures/email_fixtures.py
from ...pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from ...pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from ...pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from ...pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from ...pages.shared_story_page import SharedStoryPage  # src/test/pages/shared_story_page.py
from ...utilities.logger import log_info, log_error  # src/test/utilities/logger.py

DEFAULT_TEMPLATE = "Basic"
SHARE_MESSAGE_TEMPLATE = "I'm sharing this Storydoc story with you for automated testing purposes."
TEST_TIMEOUT = 60


def setup_story_test_data(authenticated_user: Dict, story_title: str, story_content: str) -> Dict:
    """Setup test data for story lifecycle testing"""
    test_data = {}  # Initialize an empty dictionary for test data
    test_data['user'] = authenticated_user  # Add user data from authenticated_user to the test data
    test_data['title'] = story_title  # Add story title and content to the test data
    test_data['content'] = story_content
    test_data['template'] = DEFAULT_TEMPLATE  # Add default template to the test data
    test_data['timestamp'] = str(int(time.time()))  # Generate timestamp for unique identification
    log_info("Created test data for story lifecycle")  # Log the creation of test data
    return test_data  # Return the prepared test data dictionary


def verify_story_creation(browser, story_title: str) -> bool:
    """Verify that a story was created successfully and appears in the dashboard"""
    dashboard_page = DashboardPage(browser)  # Initialize DashboardPage with browser
    dashboard_page.navigate_to()  # Navigate to dashboard
    assert dashboard_page.is_loaded(), "Dashboard did not load successfully"  # Assert that dashboard loaded successfully
    story_present = dashboard_page.is_story_present(story_title)  # Check if story with specified title is present in the dashboard
    log_info(f"Story creation verification: Story present = {story_present}")  # Log the verification result
    return story_present  # Return True if story is found, False otherwise


def complete_story_sharing(browser, editor_page: StoryEditorPage, recipient_email: str, personal_message: str = SHARE_MESSAGE_TEMPLATE) -> Dict:
    """Complete the sharing process for a story"""
    result = {'success': False}  # Initialize result dictionary with success=False
    editor_page.click_share_button()  # Click share button on editor page to open sharing dialog
    share_dialog = ShareDialogPage(browser)  # Initialize ShareDialogPage with browser
    assert share_dialog.is_dialog_open(), "Share dialog did not open"  # Verify share dialog opened successfully
    share_dialog.enter_recipient_email(recipient_email)  # Enter recipient email in the share dialog
    share_dialog.enter_personal_message(personal_message)  # Enter personal message if provided
    share_dialog.click_share_button()  # Click share button to submit sharing request
    sharing_success = share_dialog.is_sharing_successful()  # Wait for and verify sharing was successful
    sharing_link = share_dialog.get_sharing_link(recipient_email)  # Get sharing link from email
    result['success'] = sharing_success  # Update result dictionary with success=True and sharing link
    result['sharing_link'] = sharing_link
    log_info(f"Story sharing completed: Success = {sharing_success}, Sharing Link = {sharing_link}")  # Log the sharing completion status
    return result  # Return the result dictionary


def verify_shared_story_access(browser, sharing_link: str, expected_title: str) -> bool:
    """Verify that a shared story can be accessed by recipients"""
    shared_story_page = SharedStoryPage(browser)  # Initialize SharedStoryPage with browser
    shared_story_page.navigate_to_shared_story(sharing_link)  # Navigate to the shared story using the sharing link
    assert shared_story_page.is_loaded(), "Shared story page did not load successfully"  # Assert that shared story page loaded successfully
    actual_title = shared_story_page.get_story_title()
    assert actual_title == expected_title, f"Story title does not match. Expected: {expected_title}, Actual: {actual_title}"  # Verify the story title matches expected title
    assert shared_story_page.verify_story_access(), "Story access verification failed"  # Verify story access (content is visible, not restricted)
    log_info("Shared story access verification successful")  # Log the verification result
    return True  # Return True if all verifications pass, False otherwise


class TestStoryLifecycle:
    """Test class containing end-to-end tests for the story lifecycle in Storydoc"""

    def test_create_story(self, browser, authenticated_user: Dict, story_title: str, story_content: str):
        """Test story creation functionality"""
        log_info("Starting test_create_story")  # Log test start
        dashboard_page = DashboardPage(browser)  # Initialize DashboardPage with browser
        dashboard_page.navigate_to()  # Navigate to dashboard and verify loaded
        assert dashboard_page.is_loaded(), "Dashboard did not load successfully"
        dashboard_page.click_create_story_button()  # Click create story button
        editor_page = StoryEditorPage(browser)  # Initialize StoryEditorPage with browser
        assert editor_page.is_loaded(), "Story editor did not load successfully"  # Verify story editor loaded successfully
        editor_page.enter_story_title(story_title)  # Enter story title in editor
        editor_page.select_template(DEFAULT_TEMPLATE)  # Select default template
        editor_page.input_content(story_content)  # Enter story content in editor
        editor_page.save_story()  # Save the story
        assert editor_page.is_story_saved(), "Story was not saved successfully"  # Assert that story was saved successfully
        assert verify_story_creation(browser, story_title), "Story does not appear in dashboard"  # Verify story appears in dashboard
        delete_stories(browser, [story_title])  # Cleanup created story
        log_info("Completed test_create_story")  # Log test completion

    @pytest.mark.story_editing
    def test_edit_story(self, browser, authenticated_user: Dict, story_title: str, story_content: str):
        """Test story editing functionality"""
        log_info("Starting test_edit_story")  # Log test start
        test_data = setup_story_test_data(authenticated_user, story_title, story_content)
        create_story(browser, test_data['title'], test_data['template'], test_data['content'])  # Create a story for editing
        dashboard_page = DashboardPage(browser)
        dashboard_page.navigate_to()  # Navigate to dashboard
        editor_page = dashboard_page.open_story(test_data['title'])  # Open the created story for editing
        updated_title = "Updated: " + test_data['title']
        editor_page.enter_story_title(updated_title)  # Update story title with 'Updated: ' prefix
        editor_page.input_content(test_data['content'] + " [Updated Content]")  # Update story content
        editor_page.save_story()  # Save the story
        assert editor_page.is_story_saved(), "Story was not saved successfully"  # Assert that story was saved successfully
        dashboard_page.navigate_to()
        assert dashboard_page.is_story_present(updated_title), "Story with updated title does not appear in dashboard"  # Verify story with updated title appears in dashboard
        delete_stories(browser, [updated_title])  # Cleanup created story
        log_info("Completed test_edit_story")  # Log test completion

    @pytest.mark.story_sharing
    def test_share_story(self, browser, authenticated_user: Dict, story_title: str, story_content: str, sharing_email: str):
        """Test story sharing functionality"""
        log_info("Starting test_share_story")  # Log test start
        test_data = setup_story_test_data(authenticated_user, story_title, story_content)
        create_story(browser, test_data['title'], test_data['template'], test_data['content'])  # Create a story for sharing
        dashboard_page = DashboardPage(browser)
        dashboard_page.navigate_to()
        editor_page = dashboard_page.open_story(test_data['title'])  # Open created story in editor
        sharing_result = complete_story_sharing(browser, editor_page, sharing_email)  # Share the story with recipient email
        assert sharing_result['success'], "Story sharing was not successful"  # Verify sharing was successful
        assert email_helper.verify_email_received(sharing_email, "Story shared with you"), "Sharing email was not delivered"  # Wait for and verify sharing email delivery
        assert sharing_result['sharing_link'] is not None, "Sharing link was not extracted from email"
        delete_stories(browser, [story_title])  # Cleanup created story
        log_info("Completed test_share_story")  # Log test completion

    @pytest.mark.story_sharing
    def test_access_shared_story(self, browser, authenticated_user: Dict, story_title: str, story_content: str, sharing_email: str):
        """Test accessing a shared story as recipient"""
        log_info("Starting test_access_shared_story")  # Log test start
        test_data = setup_story_test_data(authenticated_user, story_title, story_content)
        create_story(browser, test_data['title'], test_data['template'], test_data['content'])  # Create a story for sharing
        dashboard_page = DashboardPage(browser)
        dashboard_page.navigate_to()
        editor_page = dashboard_page.open_story(test_data['title'])
        sharing_result = complete_story_sharing(browser, editor_page, sharing_email)  # Share the story with recipient email
        sharing_link = sharing_result['sharing_link']
        shared_story_page = SharedStoryPage(browser)  # Initialize SharedStoryPage with browser
        shared_story_page.navigate_to_shared_story(sharing_link)  # Navigate to shared story using sharing link
        assert shared_story_page.is_loaded(), "Shared story page did not load successfully"  # Verify shared story page loaded successfully
        assert shared_story_page.get_story_title() == story_title, "Story title does not match original title"  # Verify story title matches original title
        assert shared_story_page.verify_story_access(), "Story content is not accessible"  # Verify story content is accessible
        assert shared_story_page.get_shared_by_info() != "", "Sharing attribution is not displayed"  # Verify sharing attribution is displayed
        delete_stories(browser, [story_title])  # Cleanup created story
        log_info("Completed test_access_shared_story")  # Log test completion

    @pytest.mark.e2e
    @pytest.mark.story_lifecycle
    def test_story_lifecycle_end_to_end(self, browser, authenticated_user: Dict, story_title: str, story_content: str, sharing_email: str):
        """Test complete story lifecycle from creation to sharing and access"""
        log_info("Starting test_story_lifecycle_end_to_end")  # Log test start
        test_data = setup_story_test_data(authenticated_user, story_title, story_content)  # Setup test data for story lifecycle
        create_story(browser, test_data['title'], test_data['template'], test_data['content'])  # Create a new story with title and content
        assert verify_story_creation(browser, test_data['title']), "Story creation was not successful"  # Verify story creation was successful
        dashboard_page = DashboardPage(browser)
        dashboard_page.navigate_to()
        editor_page = dashboard_page.open_story(test_data['title'])
        editor_page.enter_story_title(test_data['title'] + " [Updated]")  # Edit the story with updated content
        editor_page.input_content(test_data['content'] + " [Updated Content]")
        editor_page.save_story()
        assert editor_page.is_story_saved(), "Story updates were not saved"  # Verify story updates were saved
        sharing_result = complete_story_sharing(browser, editor_page, sharing_email)  # Share the story with recipient email
        assert sharing_result['success'], "Story sharing was not successful"  # Verify sharing was successful
        shared_story_page = SharedStoryPage(browser)
        shared_story_page.navigate_to_shared_story(sharing_result['sharing_link'])  # Access shared story using sharing link
        assert shared_story_page.verify_story_access(), "Shared story is not accessible with correct content"  # Verify shared story is accessible with correct content
        delete_stories(browser, [test_data['title'] + " [Updated]"])  # Cleanup created story
        log_info("Completed test_story_lifecycle_end_to_end")  # Log test completion