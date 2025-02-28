import pytest  # pytest 7.3+
import time  # standard library
from typing import Dict  # built-in

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.fixtures.story_fixtures import story_title  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.story_fixtures import story_content  # src/test/fixtures/story_fixtures.py
from src.test.fixtures.template_fixtures import random_template  # src/test/fixtures/template_fixtures.py
from src.test.utilities.logger import log_info  # src/test/utilities/logger.py
from src.test.utilities.random_data_generator import generate_random_story_title  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_story_content  # src/test/utilities/random_data_generator.py

TEST_TEMPLATES = ["basic", "presentation", "product", "portfolio", "blank"]
DEFAULT_WAIT_TIME = 10


class TestStoryCreation:
    """Test class for story creation functionality"""

    def test_navigate_to_story_editor(self, browser, authenticated_user):
        """Test navigation from dashboard to story editor"""
        # Initialize dashboard page with browser
        dashboard_page = DashboardPage(browser)
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()
        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Log successful navigation to story editor
        log_info("Successfully navigated to story editor")

    def test_story_editor_elements(self, browser, authenticated_user):
        """Test that all expected elements are present in the story editor"""
        # Initialize dashboard page with browser
        dashboard_page = DashboardPage(browser)
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()
        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Verify title input field is present
        assert story_editor_page.is_element_present(story_editor_page.STORY_TITLE_INPUT), "Title input field is not present"
        # Verify template options are present
        assert story_editor_page.is_element_present(story_editor_page.TEMPLATE_OPTIONS), "Template options are not present"
        # Verify content editor is present
        assert story_editor_page.is_element_present(story_editor_page.CONTENT_EDITOR), "Content editor is not present"
        # Verify save button is present
        assert story_editor_page.is_element_present(story_editor_page.SAVE_BUTTON), "Save button is not present"

        # Log successful verification of story editor elements
        log_info("Successfully verified story editor elements")

    def test_story_creation_workflow(self, browser, authenticated_user, story_title, random_template, story_content):
        """Test the complete story creation workflow"""
        # Initialize dashboard page with browser
        dashboard_page = DashboardPage(browser)
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()

        # Record initial story count on dashboard
        initial_story_count = dashboard_page.get_story_count()

        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Enter the provided story title
        story_editor_page.enter_story_title(story_title)
        # Select the provided template
        story_editor_page.select_template(random_template)
        # Enter the provided content
        story_editor_page.input_content(story_content)

        # Save the story
        story_editor_page.save_story()
        # Verify story is saved successfully
        assert story_editor_page.is_story_saved(), "Story was not saved successfully"

        # Navigate back to dashboard
        dashboard_page.navigate_to()

        # Verify story count has increased by 1
        new_story_count = dashboard_page.get_story_count()
        assert new_story_count == initial_story_count + 1, "Story count did not increase"

        # Verify the created story appears in the dashboard with correct title
        assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

        # Log successful completion of story creation workflow
        log_info("Successfully completed story creation workflow")

    def test_story_auto_save(self, browser, authenticated_user):
        """Test that story is automatically saved during editing"""
        # Initialize dashboard page with browser
        dashboard_page = DashboardPage(browser)
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()
        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Generate a random story title
        story_title = generate_random_story_title()
        # Enter the story title
        story_editor_page.enter_story_title(story_title)

        # Wait for auto-save to trigger
        time.sleep(5)
        # Verify auto-save indicator appears
        assert story_editor_page.is_element_present(story_editor_page.AUTOSAVE_INDICATOR), "Auto-save indicator did not appear"

        # Enter additional content
        story_editor_page.input_content("Additional content for auto-save test")
        # Wait for auto-save to trigger again
        time.sleep(5)
        # Verify auto-save indicator appears again
        assert story_editor_page.is_element_present(story_editor_page.AUTOSAVE_INDICATOR), "Auto-save indicator did not appear after adding content"

        # Navigate back to dashboard
        dashboard_page.navigate_to()
        # Verify the created story appears in the dashboard
        assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

        # Log successful auto-save test
        log_info("Successfully completed auto-save test")

    def test_create_story_cancel(self, browser, authenticated_user):
        """Test cancelling story creation"""
        # Initialize dashboard page with browser
        dashboard_page = DashboardPage(browser)
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()

        # Record initial story count on dashboard
        initial_story_count = dashboard_page.get_story_count()

        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Generate a random story title
        story_title = generate_random_story_title()
        # Enter the story title
        story_editor_page.enter_story_title(story_title)

        # Click cancel button
        story_editor_page.click(story_editor_page.CANCEL_BUTTON)

        # Handle unsaved changes prompt if it appears
        # Verify dashboard page is loaded after cancellation
        dashboard_page.is_loaded()

        # Verify story count has not changed
        final_story_count = dashboard_page.get_story_count()
        assert final_story_count == initial_story_count, "Story count changed after cancellation"

        # Log successful cancellation test
        log_info("Successfully completed cancellation test")


def test_create_basic_story(browser, authenticated_user):
    """Test creating a basic story with title only"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Click create story button to navigate to story editor
    dashboard_page.click_create_story_button()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    story_editor_page.is_loaded()

    # Generate a random story title
    story_title = generate_random_story_title()
    # Enter the story title
    story_editor_page.enter_story_title(story_title)

    # Save the story
    story_editor_page.save_story()
    # Verify story is saved successfully
    assert story_editor_page.is_story_saved(), "Story was not saved successfully"

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify the created story appears in the dashboard
    assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Log successful story creation
    log_info("Successfully created basic story")


def test_create_story_with_template(browser, authenticated_user, random_template):
    """Test creating a story with a specific template"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Click create story button to navigate to story editor
    dashboard_page.click_create_story_button()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    story_editor_page.is_loaded()

    # Generate a random story title
    story_title = generate_random_story_title()
    # Enter the story title
    story_editor_page.enter_story_title(story_title)

    # Select the provided template
    story_editor_page.select_template(random_template)
    # Verify template is selected correctly
    assert story_editor_page.get_selected_template() == random_template, "Template was not selected correctly"

    # Save the story
    story_editor_page.save_story()
    # Verify story is saved successfully
    assert story_editor_page.is_story_saved(), "Story was not saved successfully"

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify the created story appears in the dashboard
    assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Log successful story creation with template
    log_info("Successfully created story with template")


def test_create_story_with_content(browser, authenticated_user, random_template, story_content):
    """Test creating a story with title, template, and content"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Click create story button to navigate to story editor
    dashboard_page.click_create_story_button()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    story_editor_page.is_loaded()

    # Generate a random story title
    story_title = generate_random_story_title()
    # Enter the story title
    story_editor_page.enter_story_title(story_title)

    # Select the provided template
    story_editor_page.select_template(random_template)
    # Enter the provided content
    story_editor_page.input_content(story_content)

    # Save the story
    story_editor_page.save_story()
    # Verify story is saved successfully
    assert story_editor_page.is_story_saved(), "Story was not saved successfully"

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify the created story appears in the dashboard
    assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Log successful story creation with content
    log_info("Successfully created story with content")


def test_create_story_without_title(browser, authenticated_user):
    """Test validation when creating a story without a title"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Click create story button to navigate to story editor
    dashboard_page.click_create_story_button()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    story_editor_page.is_loaded()

    # Try to save story without entering a title
    story_editor_page.save_story()
    # Verify error message is displayed
    assert story_editor_page.is_element_present(story_editor_page.ERROR_MESSAGE), "Error message is not displayed"
    # Verify story is not saved
    assert not story_editor_page.is_story_saved(), "Story was saved without a title"

    # Log validation test result
    log_info("Successfully validated story creation without title")


def test_create_multiple_stories(browser, authenticated_user):
    """Test creating multiple stories in succession"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()

    # Define number of stories to create (3)
    num_stories = 3
    # Create a list to store story titles
    story_titles = []

    # For each story to create:
    for i in range(num_stories):
        # Click create story button to navigate to story editor
        dashboard_page.click_create_story_button()

        # Initialize story editor page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()

        # Generate a random story title and add to list
        story_title = generate_random_story_title()
        story_titles.append(story_title)
        # Enter the story title
        story_editor_page.enter_story_title(story_title)

        # Save the story
        story_editor_page.save_story()
        # Verify story is saved successfully
        assert story_editor_page.is_story_saved(), "Story was not saved successfully"

        # Navigate back to dashboard
        dashboard_page.navigate_to()

        # Verify the created story appears in the dashboard
        assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Verify all created stories are present in the dashboard
    for story_title in story_titles:
        assert dashboard_page.is_story_present(story_title), f"Story '{story_title}' is not present in dashboard"

    # Log successful creation of multiple stories
    log_info("Successfully created multiple stories")


def test_create_story_using_helper_method(browser, authenticated_user, story_title, random_template, story_content):
    """Test story creation using the create_story helper method"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)

    # Use story_editor_page.create_story() helper method with title, template, and content
    story_editor_page.create_story(story_title, random_template, story_content)

    # Verify story is created successfully
    assert story_editor_page.is_story_saved(), "Story was not saved successfully"

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify the created story appears in the dashboard
    assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Log successful story creation using helper method
    log_info("Successfully created story using helper method")


@pytest.mark.parametrize('template_name', TEST_TEMPLATES)
def test_template_selection(browser, authenticated_user):
    """Test selecting different templates for a story"""
    # Initialize dashboard page with browser
    dashboard_page = DashboardPage(browser)
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Click create story button to navigate to story editor
    dashboard_page.click_create_story_button()

    # Initialize story editor page with browser
    story_editor_page = StoryEditorPage(browser)
    # Verify story editor page is loaded
    story_editor_page.is_loaded()

    # Generate a random story title
    story_title = generate_random_story_title()
    # Enter the story title
    story_editor_page.enter_story_title(story_title)

    # Select the template specified by the parametrize decorator
    story_editor_page.select_template(template_name)
    # Verify the correct template is selected
    assert story_editor_page.get_selected_template() == template_name, "Template was not selected correctly"

    # Save the story
    story_editor_page.save_story()
    # Verify story is saved successfully
    assert story_editor_page.is_story_saved(), "Story was not saved successfully"

    # Navigate back to dashboard
    dashboard_page.navigate_to()
    # Verify the created story appears in the dashboard
    assert dashboard_page.is_story_present(story_title), "Created story is not present in dashboard"

    # Log successful template selection test
    log_info("Successfully completed template selection test")