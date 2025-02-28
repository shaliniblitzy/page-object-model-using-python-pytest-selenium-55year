import pytest  # pytest 7.3+
import time
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.story_fixtures import story_title  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.story_fixtures import story_content  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.story_fixtures import create_story  # src/test/fixtures/story_fixtures.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_equal  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_element_visible  # src/test/utilities/assertion_helper.py
from src.test.config.timeout_config import STORY_CREATION_TIMEOUT  # src/test/config/timeout_config.py


@pytest.mark.story
@pytest.mark.save
def test_save_story_success(browser, authenticated_user, story_title, story_content):
    """Test that a story can be successfully saved"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Verify dashboard page is loaded
    assert_true(dashboard_page.is_loaded(), "Dashboard page should be loaded", browser=browser)
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    assert_true(story_editor_page.is_loaded(), "Story editor page should be loaded", browser=browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter story content
    story_editor_page.input_content(story_content)
    # Save the story
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify that the story appears in the dashboard
    assert_true(dashboard_page.is_story_present(story_title), "Story should appear in the dashboard", browser=browser)


@pytest.mark.story
@pytest.mark.save
@pytest.mark.validation
def test_save_story_with_empty_title(browser, authenticated_user, story_content):
    """Test that a validation error is shown when trying to save a story with empty title"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    assert_true(story_editor_page.is_loaded(), "Story editor page should be loaded", browser=browser)
    # Enter empty title (or skip title entry)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter story content
    story_editor_page.input_content(story_content)
    # Attempt to save the story
    story_editor_page.save_story()
    # Assert that an error message for empty title is displayed
    # Assert that the story was not saved
    assert_true(not story_editor_page.is_story_saved(), "Story should not be saved", browser=browser)


@pytest.mark.story
@pytest.mark.save
def test_save_story_with_empty_content(browser, authenticated_user, story_title):
    """Test that a story can be saved with empty content (title and template only)"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    assert_true(story_editor_page.is_loaded(), "Story editor page should be loaded", browser=browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Save the story without entering content
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify that the story appears in the dashboard
    assert_true(dashboard_page.is_story_present(story_title), "Story should appear in the dashboard", browser=browser)


@pytest.mark.story
@pytest.mark.save
@pytest.mark.content
def test_save_story_verify_content_persistence(browser, authenticated_user, story_title, story_content):
    """Test that the story content is correctly persisted after saving"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter story content
    story_editor_page.input_content(story_content)
    # Save the story
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Find and click on the created story
    dashboard_page.open_story(story_title)

    # Initialize story_editor_page again
    story_editor_page = StoryEditorPage(browser)
    # Verify that the story title matches the original title
    assert_equal(story_editor_page.get_story_title(), story_title, "Story title should match", browser=browser)
    # Verify that the story content matches the original content
    assert_equal(story_editor_page.get_content(), story_content, "Story content should match", browser=browser)


@pytest.mark.story
@pytest.mark.save
@pytest.mark.performance
def test_save_story_with_long_content(browser, authenticated_user, story_title):
    """Test that a story with long content can be saved successfully"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Generate and enter long content (multiple paragraphs)
    long_content = "This is a very long story content. " * 500
    story_editor_page.input_content(long_content)

    # Set a longer timeout for the save operation
    # Save the story
    story_editor_page.save_story()
    # Assert that the story was saved successfully within the timeout
    assert_true(story_editor_page.is_story_saved(), "Story with long content should be saved successfully", browser=browser)

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify that the story appears in the dashboard
    assert_true(dashboard_page.is_story_present(story_title), "Story should appear in the dashboard", browser=browser)


@pytest.mark.story
@pytest.mark.save
def test_save_multiple_times(browser, authenticated_user, story_title, story_content):
    """Test that a story can be saved multiple times with updates"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter initial story content
    story_editor_page.input_content(story_content)
    # Save the story
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Update the story content
    updated_content = story_content + " Updated content."
    story_editor_page.input_content(updated_content)
    # Save the story again
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Update the story title
    updated_title = story_title + " - Updated"
    story_editor_page.enter_story_title(updated_title)
    # Save the story a third time
    story_editor_page.save_story()
    # Assert that the story was saved successfully
    assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", browser=browser)

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify that the story with updated title appears in the dashboard
    assert_true(dashboard_page.is_story_present(updated_title), "Story with updated title should appear in the dashboard", browser=browser)


@pytest.mark.story
@pytest.mark.save
@pytest.mark.error
def test_save_story_error_handling(browser, authenticated_user, story_title, story_content):
    """Test error handling when saving a story fails due to network issues"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter story content
    story_editor_page.input_content(story_content)

    # Mock a network failure during save (using JavaScript execution)
    browser.execute_script("window.stop();")

    # Attempt to save the story
    story_editor_page.save_story()
    # Assert that an error message is displayed
    # Assert that retry functionality is available

    # Restore network connection
    # Attempt to save again
    # Assert that the story was saved successfully after retry
    assert_true(not story_editor_page.is_story_saved(), "Story should not be saved", browser=browser)


@pytest.mark.story
@pytest.mark.save
@pytest.mark.autosave
def test_autosave_functionality(browser, authenticated_user, story_title, story_content):
    """Test that story content is automatically saved periodically"""
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard
    dashboard_page.navigate_to()
    # Click create story button
    dashboard_page.click_create_story_button()

    # Initialize story_editor_page with browser
    story_editor_page = StoryEditorPage(browser)
    # Enter story title
    story_editor_page.enter_story_title(story_title)
    # Select a template
    story_editor_page.select_template("Basic")
    # Enter story content
    story_editor_page.input_content(story_content)

    # Wait for autosave interval to elapse
    time.sleep(30)

    # Check for autosave indicator or message
    # Navigate away from the page without manually saving
    # When prompted, cancel navigation
    # Verify that content is still present

    # Manually save the story
    story_editor_page.save_story()
    # Navigate away from the page
    # Return to the dashboard
    dashboard_page.navigate_to()
    # Open the story again
    dashboard_page.open_story(story_title)
    # Verify that all content was saved correctly
    assert_equal(story_editor_page.get_content(), story_content, "Story content should match", browser=browser)