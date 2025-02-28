import pytest  # pytest 7.3+
import time  # Provides timing and sleep functions for test operations
import logging  # Logging test execution and results

# Internal imports
from src.test.pages.story_editor_page import StoryEditorPage  # Page object for interacting with the Story Editor interface
from src.test.fixtures.browser_fixtures import browser  # Provides browser instance for test execution
from src.test.fixtures.user_fixtures import authenticated_user  # Provides authenticated user session for story creation
from src.test.fixtures.story_fixtures import story_title  # Provides random story title for testing
from src.test.fixtures.story_fixtures import story_content  # Provides random story content for testing
from src.test.fixtures.story_fixtures import created_story  # Creates a story and returns its details for testing
from src.test.utilities.assertion_helper import assert_equal  # Enhanced assertion for equality checking with screenshots
from src.test.utilities.assertion_helper import assert_true  # Enhanced assertion for boolean conditions with screenshots
from src.test.utilities.assertion_helper import assert_element_visible  # Enhanced assertion for element visibility with screenshots
from src.test.utilities.assertion_helper import assert_text_in_element  # Enhanced assertion for text content with screenshots

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
SHORT_CONTENT = "This is a short test content."
MEDIUM_CONTENT = "This is a medium length content that spans multiple sentences. It is used to test the text entry and retrieval functionality of the story editor."
LONG_CONTENT = "This is a long test content with multiple paragraphs.\n\nIt contains line breaks and formatting to test rich content handling.\n\n- Bullet point 1\n- Bullet point 2\n- Bullet point 3\n\nThis ensures the editor can handle complex content structures."


@pytest.mark.usefixtures('authenticated_user')
class TestStoryContent:
    """Test class for validating story content functionality in the Storydoc application"""

    def __init__(self):
        """Default constructor"""
        # Initialize class attributes
        pass

    def test_story_title_entry(self, browser, story_title):
        """Test that story title can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter story title using enter_story_title method
        story_editor_page.enter_story_title(story_title)
        # Retrieve entered title using get_story_title method
        retrieved_title = story_editor_page.get_story_title()
        # Assert that retrieved title matches the entered title
        assert_equal(retrieved_title, story_title, "Retrieved title should match entered title", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested story title entry")

    def test_story_content_entry_short(self, browser):
        """Test that short content can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter short content using input_content method with SHORT_CONTENT
        story_editor_page.input_content(SHORT_CONTENT)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content matches the entered content
        assert_equal(retrieved_content, SHORT_CONTENT, "Retrieved content should match entered short content", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested short story content entry")

    def test_story_content_entry_medium(self, browser):
        """Test that medium length content can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter medium content using input_content method with MEDIUM_CONTENT
        story_editor_page.input_content(MEDIUM_CONTENT)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content matches the entered content
        assert_equal(retrieved_content, MEDIUM_CONTENT, "Retrieved content should match entered medium content", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested medium story content entry")

    def test_story_content_entry_long(self, browser):
        """Test that long, formatted content can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter long, formatted content using input_content method with LONG_CONTENT
        story_editor_page.input_content(LONG_CONTENT)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content contains the expected formatting elements
        assert_true("- Bullet point 1" in retrieved_content, "Retrieved content should contain bullet points", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested long story content entry")

    def test_content_persistence_after_save(self, browser, story_title, story_content):
        """Test that content persists after saving the story"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter story title using enter_story_title method
        story_editor_page.enter_story_title(story_title)
        # Enter content using input_content method with provided story_content
        story_editor_page.input_content(story_content)
        # Save the story using save_story method
        story_editor_page.save_story()
        # Assert that save was successful using is_story_saved method
        assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully", driver=browser)
        # Refresh the page to ensure content is loaded from server
        browser.refresh()
        # Retrieve title and content after refresh
        retrieved_title = story_editor_page.get_story_title()
        retrieved_content = story_editor_page.get_content()
        # Assert that title and content match what was entered before saving
        assert_equal(retrieved_title, story_title, "Retrieved title should match entered title after save", driver=browser)
        assert_equal(retrieved_content, story_content, "Retrieved content should match entered content after save", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested content persistence after save")

    def test_content_edit_after_save(self, browser, created_story):
        """Test that content can be edited after saving"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Get original content using get_content method
        original_content = story_editor_page.get_content()
        # Create new content by appending text to original content
        modified_content = original_content + "\nThis is the modified content."
        # Enter modified content using input_content method
        story_editor_page.input_content(modified_content)
        # Save the story using save_story method
        story_editor_page.save_story()
        # Assert that save was successful using is_story_saved method
        assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully after edit", driver=browser)
        # Refresh the page to ensure content is loaded from server
        browser.refresh()
        # Retrieve content after refresh
        retrieved_content = story_editor_page.get_content()
        # Assert that content matches the modified content
        assert_equal(retrieved_content, modified_content, "Retrieved content should match modified content after save", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested content edit after save")

    def test_empty_content_allowed(self, browser, story_title):
        """Test that empty content is allowed (no content validation errors)"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Enter story title using enter_story_title method
        story_editor_page.enter_story_title(story_title)
        # Clear content if any exists
        story_editor_page.input_content("")
        # Save the story using save_story method
        story_editor_page.save_story()
        # Assert that save was successful using is_story_saved method
        assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully with empty content", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested empty content allowed")

    def test_content_with_special_characters(self, browser):
        """Test that content with special characters can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Create content with special characters (!@#$%^&*()_+{}[]|\':;<>,.?/)
        special_content = "!@#$%^&*()_+{}[]|\\':;<>,.?/"
        # Enter special content using input_content method
        story_editor_page.input_content(special_content)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content matches the entered content with special characters
        assert_equal(retrieved_content, special_content, "Retrieved content should match entered content with special characters", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested content with special characters")

    def test_very_long_content(self, browser):
        """Test that very long content can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Generate very long content (multiple paragraphs with repeated text)
        long_content = "This is a repeated sentence. " * 2000
        # Enter long content using input_content method
        story_editor_page.input_content(long_content)
        # Save the story using save_story method
        story_editor_page.save_story()
        # Assert that save was successful using is_story_saved method
        assert_true(story_editor_page.is_story_saved(), "Story should be saved successfully with very long content", driver=browser)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content contains expected text patterns
        assert_true("This is a repeated sentence." in retrieved_content, "Retrieved content should contain expected text patterns", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested very long content")

    def test_content_with_line_breaks(self, browser):
        """Test that content with line breaks can be entered and retrieved correctly"""
        # Initialize StoryEditorPage with browser
        story_editor_page = StoryEditorPage(browser)
        # Create content with multiple line breaks
        line_break_content = "This is line 1.\nThis is line 2.\nThis is line 3."
        # Enter content using input_content method
        story_editor_page.input_content(line_break_content)
        # Retrieve entered content using get_content method
        retrieved_content = story_editor_page.get_content()
        # Assert that retrieved content maintains line breaks
        assert_equal(retrieved_content, line_break_content, "Retrieved content should maintain line breaks", driver=browser)
        # Log successful test completion
        logger.info("Successfully tested content with line breaks")