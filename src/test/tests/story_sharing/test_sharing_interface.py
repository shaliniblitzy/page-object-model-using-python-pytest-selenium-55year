# src/test/tests/story_sharing/test_sharing_interface.py
import pytest  # pytest 7.3+
import time  # standard library

# Internal imports
from ..fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from ..fixtures.story_fixtures import created_story  # src/test/fixtures/story_fixtures.py
from ..fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from ...pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from ...pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from ...locators.share_dialog_locators import ShareDialogLocators  # src/test/locators/share_dialog_locators.py
from ...utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from ...utilities.logger import log_info, log_error  # src/test/utilities/logger.py

EMAIL_SUBJECT = "Story shared with you"
SHARING_TIMEOUT = 30


def test_share_dialog_opens(browser, created_story):
    """Verify that the share dialog opens when the share button is clicked"""
    log_info("Starting test: test_share_dialog_opens")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the share dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog did not open"
    log_info("Verified that the share dialog is open")

    # Assert that all expected UI elements are present in the dialog
    assert browser.find_element(*ShareDialogLocators.DIALOG_CONTAINER), "Dialog container not found"
    assert browser.find_element(*ShareDialogLocators.DIALOG_TITLE), "Dialog title not found"
    assert browser.find_element(*ShareDialogLocators.RECIPIENT_EMAIL_INPUT), "Recipient email input not found"
    assert browser.find_element(*ShareDialogLocators.PERSONAL_MESSAGE_TEXTAREA), "Personal message textarea not found"
    assert browser.find_element(*ShareDialogLocators.SHARE_BUTTON), "Share button not found"
    log_info("Verified that all expected UI elements are present in the dialog")


def test_share_dialog_has_expected_elements(browser, created_story):
    """Verify that the share dialog contains all expected UI elements"""
    log_info("Starting test: test_share_dialog_has_expected_elements")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog title is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.DIALOG_TITLE), "Dialog title is not visible"
    log_info("Verified that the dialog title is visible")

    # Verify that the recipient email input field is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.RECIPIENT_EMAIL_INPUT), "Recipient email input is not visible"
    log_info("Verified that the recipient email input field is visible")

    # Verify that the personal message textarea is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.PERSONAL_MESSAGE_TEXTAREA), "Personal message textarea is not visible"
    log_info("Verified that the personal message textarea is visible")

    # Verify that the share button is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.SHARE_BUTTON), "Share button is not visible"
    log_info("Verified that the share button is visible")

    # Verify that the cancel button is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.CANCEL_BUTTON), "Cancel button is not visible"
    log_info("Verified that the cancel button is visible")

    # Verify that the close button is visible
    assert share_dialog_page.is_element_visible(ShareDialogLocators.CLOSE_BUTTON), "Close button is not visible"
    log_info("Verified that the close button is visible")


def test_share_dialog_cancel_button_closes_dialog(browser, created_story):
    """Verify that clicking the cancel button closes the share dialog"""
    log_info("Starting test: test_share_dialog_cancel_button_closes_dialog")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Click the cancel button
    share_dialog_page.click_cancel_button()
    log_info("Clicked the cancel button")

    # Verify that the dialog is no longer visible
    assert not share_dialog_page.is_dialog_open(), "Share dialog is still open"
    log_info("Verified that the dialog is no longer visible")

    # Assert that the story editor page is still visible
    assert story_editor_page.is_loaded(), "Story editor page is not visible"
    log_info("Asserted that the story editor page is still visible")


def test_share_dialog_close_button_closes_dialog(browser, created_story):
    """Verify that clicking the X (close) button closes the share dialog"""
    log_info("Starting test: test_share_dialog_close_button_closes_dialog")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Click the close button (X)
    share_dialog_page.click_close_button()
    log_info("Clicked the close button (X)")

    # Verify that the dialog is no longer visible
    assert not share_dialog_page.is_dialog_open(), "Share dialog is still open"
    log_info("Verified that the dialog is no longer visible")

    # Assert that the story editor page is still visible
    assert story_editor_page.is_loaded(), "Story editor page is not visible"
    log_info("Asserted that the story editor page is still visible")


def test_share_dialog_validates_empty_email(browser, created_story):
    """Verify that an error message is shown when attempting to share without entering a recipient email"""
    log_info("Starting test: test_share_dialog_validates_empty_email")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Click the share button without entering recipient email
    share_dialog_page.click_share_button()
    log_info("Clicked the share button without entering recipient email")

    # Verify that an error message is shown for the recipient email field
    assert share_dialog_page.is_recipient_email_error_shown(), "Recipient email error is not shown"
    log_info("Verified that an error message is shown for the recipient email field")

    # Assert that the dialog remains open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Asserted that the dialog remains open")


def test_share_dialog_validates_invalid_email_format(browser, created_story):
    """Verify that an error message is shown when entering an invalid email format"""
    log_info("Starting test: test_share_dialog_validates_invalid_email_format")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Enter an invalid email format (e.g., 'invalid-email')
    share_dialog_page.enter_recipient_email("invalid-email")
    log_info("Entered an invalid email format (e.g., 'invalid-email')")

    # Click the share button
    share_dialog_page.click_share_button()
    log_info("Clicked the share button")

    # Verify that an error message is shown for the recipient email field
    assert share_dialog_page.is_recipient_email_error_shown(), "Recipient email error is not shown"
    log_info("Verified that an error message is shown for the recipient email field")

    # Assert that the dialog remains open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Asserted that the dialog remains open")


def test_share_dialog_can_add_multiple_recipients(browser, created_story):
    """Verify that multiple recipients can be added to the share dialog"""
    log_info("Starting test: test_share_dialog_can_add_multiple_recipients")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Enter a recipient email
    share_dialog_page.enter_recipient_email("recipient1@example.com")
    log_info("Entered a recipient email")

    # Click the add recipient button
    share_dialog_page.add_additional_recipient()
    log_info("Clicked the add recipient button")

    # Verify that a new recipient field appears
    assert browser.find_elements(*ShareDialogLocators.RECIPIENT_EMAIL_INPUT)[1], "New recipient field did not appear"
    log_info("Verified that a new recipient field appears")

    # Enter a second recipient email
    share_dialog_page.enter_recipient_email("recipient2@example.com")
    log_info("Entered a second recipient email")

    # Click the share button
    share_dialog_page.click_share_button()
    log_info("Clicked the share button")

    # Verify that sharing is successful
    assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
    log_info("Verified that sharing is successful")

    # Assert that the dialog closes after successful sharing
    assert not share_dialog_page.is_dialog_open(), "Share dialog is still open"
    log_info("Asserted that the dialog closes after successful sharing")


def test_share_dialog_optional_message_field(browser, created_story):
    """Verify that a personal message can be added to the share dialog"""
    log_info("Starting test: test_share_dialog_optional_message_field")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Enter a recipient email
    share_dialog_page.enter_recipient_email("recipient@example.com")
    log_info("Entered a recipient email")

    # Enter a personal message in the textarea
    share_dialog_page.enter_personal_message("This is a test message")
    log_info("Entered a personal message in the textarea")

    # Click the share button
    share_dialog_page.click_share_button()
    log_info("Clicked the share button")

    # Verify that sharing is successful
    assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
    log_info("Verified that sharing is successful")

    # Assert that the dialog closes after successful sharing
    assert not share_dialog_page.is_dialog_open(), "Share dialog is still open"
    log_info("Asserted that the dialog closes after successful sharing")


def test_successful_story_sharing(browser, created_story):
    """Verify that a story can be successfully shared with a recipient"""
    log_info("Starting test: test_successful_story_sharing")

    # Initialize EmailHelper
    email_helper = EmailHelper()
    log_info("Initialized EmailHelper")

    # Generate a unique recipient email address using Mailinator
    recipient_email = email_helper.generate_email_address()
    log_info(f"Generated recipient email: {recipient_email}")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Enter the generated recipient email
    share_dialog_page.enter_recipient_email(recipient_email)
    log_info(f"Entered recipient email: {recipient_email}")

    # Enter an optional personal message
    share_dialog_page.enter_personal_message("Check out this awesome story!")
    log_info("Entered an optional personal message")

    # Click the share button
    share_dialog_page.click_share_button()
    log_info("Clicked the share button")

    # Verify that sharing is successful
    assert share_dialog_page.is_sharing_successful(), "Sharing was not successful"
    log_info("Verified that sharing is successful")

    # Assert that the dialog closes after successful sharing
    assert not share_dialog_page.is_dialog_open(), "Share dialog is still open"
    log_info("Asserted that the dialog closes after successful sharing")

    # Verify that a sharing email is received at the recipient address
    assert email_helper.verify_email_received(recipient_email, EMAIL_SUBJECT, SHARING_TIMEOUT), f"Sharing email not received at {recipient_email}"
    log_info(f"Verified that sharing email is received at {recipient_email}")

    # Extract and verify the sharing link from the email
    message = email_helper.wait_for_email(recipient_email, EMAIL_SUBJECT, SHARING_TIMEOUT)
    sharing_link = email_helper.extract_verification_link(message)
    assert sharing_link is not None, "Sharing link not found in the email"
    log_info(f"Extracted and verified the sharing link from the email: {sharing_link}")


def test_share_dialog_success_message(browser, created_story):
    """Verify that a success message is shown after successfully sharing a story"""
    log_info("Starting test: test_share_dialog_success_message")

    # Initialize EmailHelper
    email_helper = EmailHelper()
    log_info("Initialized EmailHelper")

    # Generate a unique recipient email address using Mailinator
    recipient_email = email_helper.generate_email_address()
    log_info(f"Generated recipient email: {recipient_email}")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Verify that the dialog is open
    assert share_dialog_page.is_dialog_open(), "Share dialog is not open"
    log_info("Verified that the dialog is open")

    # Enter the generated recipient email
    share_dialog_page.enter_recipient_email(recipient_email)
    log_info(f"Entered recipient email: {recipient_email}")

    # Click the share button
    share_dialog_page.click_share_button()
    log_info("Clicked the share button")

    # Verify that a success message is shown
    assert share_dialog_page.is_sharing_successful(), "Sharing success message is not shown"
    log_info("Verified that a success message is shown")

    # Assert that the message indicates successful sharing
    success_message_text = share_dialog_page.get_text(ShareDialogLocators.SHARE_SUCCESS_MESSAGE)
    assert "successfully shared" in success_message_text.lower(), "Success message does not indicate successful sharing"
    log_info("Asserted that the message indicates successful sharing")


def test_access_shared_story_link(browser, created_story):
    """Verify that a shared story link can be accessed by the recipient"""
    log_info("Starting test: test_access_shared_story_link")

    # Initialize EmailHelper
    email_helper = EmailHelper()
    log_info("Initialized EmailHelper")

    # Generate a unique recipient email address using Mailinator
    recipient_email = email_helper.generate_email_address()
    log_info(f"Generated recipient email: {recipient_email}")

    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    log_info("Initialized StoryEditorPage")

    # Open created story in the editor
    story_editor_page.open()
    log_info("Opened created story in the editor")

    # Click the share button
    story_editor_page.click_share_button()
    log_info("Clicked the share button")

    # Initialize ShareDialogPage with browser
    share_dialog_page = ShareDialogPage(browser)
    log_info("Initialized ShareDialogPage")

    # Complete the sharing process with the generated recipient email
    share_dialog_page.complete_sharing(recipient_email)
    log_info(f"Completed the sharing process with recipient email: {recipient_email}")

    # Wait for the sharing email to be received
    message = email_helper.wait_for_email(recipient_email, EMAIL_SUBJECT, SHARING_TIMEOUT)
    assert message is not None, f"Sharing email not received at {recipient_email}"
    log_info(f"Sharing email received at {recipient_email}")

    # Extract the sharing link from the email
    sharing_link = email_helper.extract_verification_link(message)
    assert sharing_link is not None, "Sharing link not found in the email"
    log_info(f"Extracted sharing link: {sharing_link}")

    # Navigate to the extracted link
    browser.get(sharing_link)
    log_info(f"Navigated to the sharing link: {sharing_link}")

    # Verify that the shared story content is visible
    # This is a placeholder, replace with actual verification of shared story content
    assert "Storydoc" in browser.title, "Shared story content is not visible"
    log_info("Verified that the shared story content is visible")

    # Assert that the story title matches the shared story's title
    story_title = created_story['title']
    assert story_title in browser.title, f"Shared story title does not match: expected '{story_title}' in '{browser.title}'"
    log_info(f"Asserted that the story title matches the shared story's title: {story_title}")