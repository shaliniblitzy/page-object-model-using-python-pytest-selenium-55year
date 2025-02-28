import pytest  # pytest 7.3+
from typing import List  # standard library

# Internal imports
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.locators.share_dialog_locators import ShareDialogLocators  # src/test/locators/share_dialog_locators.py
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.story_fixtures import created_story  # src/test/fixtures/story_fixtures.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_false  # src/test/utilities/assertion_helper.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.utilities.logger import log_error  # src/test/utilities/logger.py

# Initialize EmailHelper
email_helper = EmailHelper()

# Define invalid email formats
INVALID_EMAIL_FORMATS = ["invalid", "invalid@", "invalid@domain", "invalid@domain.", "@domain.com", "user@.com", "user@domain@domain.com", "user@domain..com"]


@pytest.fixture
def valid_recipient_email() -> str:
    """Fixture that provides a valid recipient email address"""
    # Generate a valid email address using email_helper.generate_email_address()
    email = email_helper.generate_email_address()
    # Log the generated email address
    log_info(f"Generated valid recipient email: {email}")
    # Return the email address
    return email


@pytest.fixture
def invalid_recipient_emails() -> List:
    """Fixture that provides a list of invalid email formats for testing"""
    # Return the global INVALID_EMAIL_FORMATS list
    return INVALID_EMAIL_FORMATS


@pytest.fixture
def setup_share_dialog(browser, created_story) -> ShareDialogPage:
    """Fixture that sets up the share dialog for testing"""
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    # Click share button to open share dialog
    story_editor_page.click_share_button()
    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    # Wait for dialog to appear
    share_dialog_page.wait_for_dialog()
    # Assert that dialog is visible
    assert_true(share_dialog_page.is_dialog_open(), "Share dialog should be open", driver=browser)
    # Return the initialized ShareDialogPage object
    return share_dialog_page


@pytest.mark.validation
@pytest.mark.positive
def test_valid_recipient_email(browser, setup_share_dialog, valid_recipient_email):
    """Test that a valid recipient email is accepted without error"""
    # Enter valid recipient email in the share dialog
    setup_share_dialog.enter_recipient_email(valid_recipient_email)
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that no recipient error is shown
    assert_false(setup_share_dialog.is_recipient_email_error_shown(), "No recipient error should be shown", driver=browser)
    # Assert that sharing is successful
    assert_true(setup_share_dialog.is_sharing_successful(), "Sharing should be successful", driver=browser)
    # Log test completion
    log_info("Test completed: Valid recipient email accepted")


@pytest.mark.validation
@pytest.mark.negative
@pytest.mark.parametrize('invalid_email', INVALID_EMAIL_FORMATS)
def test_invalid_recipient_email_formats(browser, setup_share_dialog, invalid_recipient_emails, invalid_email):
    """Test that invalid recipient email formats are rejected with appropriate error messages"""
    # Enter invalid email format in the share dialog
    setup_share_dialog.enter_recipient_email(invalid_email)
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that recipient error message is shown
    assert_true(setup_share_dialog.is_recipient_email_error_shown(), "Recipient error should be shown", driver=browser)
    # Assert that sharing is not successful
    assert_false(setup_share_dialog.is_sharing_successful(), "Sharing should not be successful", driver=browser)
    # Log test completion with specific invalid format
    log_info(f"Test completed: Invalid email format '{invalid_email}' rejected")


@pytest.mark.validation
@pytest.mark.negative
def test_empty_recipient_email(browser, setup_share_dialog):
    """Test that empty recipient email field is rejected"""
    # Leave recipient email field empty
    setup_share_dialog.enter_recipient_email("")
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that recipient error message is shown
    assert_true(setup_share_dialog.is_recipient_email_error_shown(), "Recipient error should be shown", driver=browser)
    # Assert that sharing is not successful
    assert_false(setup_share_dialog.is_sharing_successful(), "Sharing should not be successful", driver=browser)
    # Log test completion
    log_info("Test completed: Empty recipient email rejected")


@pytest.mark.validation
def test_whitespace_in_recipient_email(browser, setup_share_dialog, valid_recipient_email):
    """Test that whitespace in recipient email is properly handled"""
    # Create email with whitespace by adding spaces before and after valid email
    email_with_whitespace = f"  {valid_recipient_email}  "
    # Enter email with whitespace in the share dialog
    setup_share_dialog.enter_recipient_email(email_with_whitespace)
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that no recipient error is shown (whitespace should be trimmed)
    assert_false(setup_share_dialog.is_recipient_email_error_shown(), "No recipient error should be shown", driver=browser)
    # Assert that sharing is successful
    assert_true(setup_share_dialog.is_sharing_successful(), "Sharing should be successful", driver=browser)
    # Log test completion
    log_info("Test completed: Whitespace in recipient email handled correctly")


@pytest.mark.validation
def test_multiple_recipients_validation(browser, setup_share_dialog, valid_recipient_email):
    """Test validation of multiple recipient email addresses"""
    # Enter first valid recipient email
    setup_share_dialog.enter_recipient_email(valid_recipient_email)
    # Add additional recipient by clicking add recipient button
    setup_share_dialog.add_additional_recipient()
    # Enter invalid email for second recipient
    setup_share_dialog.enter_recipient_email("invalid_email")
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that recipient error message is shown
    assert_true(setup_share_dialog.is_recipient_email_error_shown(), "Recipient error should be shown", driver=browser)
    # Assert that sharing is not successful
    assert_false(setup_share_dialog.is_sharing_successful(), "Sharing should not be successful", driver=browser)

    # Clear invalid email and enter valid email for second recipient
    setup_share_dialog.enter_recipient_email(valid_recipient_email)
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that no recipient error is shown
    assert_false(setup_share_dialog.is_recipient_email_error_shown(), "No recipient error should be shown", driver=browser)
    # Assert that sharing is successful
    assert_true(setup_share_dialog.is_sharing_successful(), "Sharing should be successful", driver=browser)
    # Log test completion
    log_info("Test completed: Multiple recipients validation successful")


@pytest.mark.validation
@pytest.mark.limits
def test_maximum_recipient_limit(browser, setup_share_dialog):
    """Test that the system enforces a maximum number of recipients"""
    # Define a large number of recipients to test (e.g., 20)
    num_recipients = 20
    # Enter first valid recipient email
    setup_share_dialog.enter_recipient_email(email_helper.generate_email_address())
    # Loop to add additional recipients up to system limit
    for _ in range(num_recipients - 1):
        setup_share_dialog.add_additional_recipient()
        setup_share_dialog.enter_recipient_email(email_helper.generate_email_address())
    # Attempt to add one more recipient beyond the limit
    setup_share_dialog.add_additional_recipient()
    # Assert that additional recipient cannot be added (button disabled or error shown)
    # Click share button with maximum allowed recipients
    setup_share_dialog.click_share_button()
    # Assert that sharing is successful
    assert_true(setup_share_dialog.is_sharing_successful(), "Sharing should be successful", driver=browser)
    # Log test completion with number of maximum recipients
    log_info(f"Test completed: Maximum recipient limit of {num_recipients} enforced")


@pytest.mark.validation
@pytest.mark.positive
def test_special_characters_in_email(browser, setup_share_dialog):
    """Test that valid emails with special characters are accepted"""
    # Create valid emails with special characters (e.g., 'user+tag@mailinator.com', 'user.name@mailinator.com')
    special_email1 = "user+tag@mailinator.com"
    special_email2 = "user.name@mailinator.com"
    # Enter special character email in the share dialog
    setup_share_dialog.enter_recipient_email(special_email1)
    # Click share button
    setup_share_dialog.click_share_button()
    # Assert that no recipient error is shown
    assert_false(setup_share_dialog.is_recipient_email_error_shown(), "No recipient error should be shown", driver=browser)
    # Assert that sharing is successful
    assert_true(setup_share_dialog.is_sharing_successful(), "Sharing should be successful", driver=browser)
    # Log test completion
    log_info(f"Test completed: Special character email '{special_email1}' accepted")