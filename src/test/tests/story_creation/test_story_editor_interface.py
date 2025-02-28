import pytest  # pytest 7.3+
from src.test.pages.story_editor_page import StoryEditorPage  # Page object for story editor page interactions
from src.test.pages.dashboard_page import DashboardPage  # Page object for dashboard page interactions
from src.test.locators.story_editor_locators import StoryEditorLocators  # Locators for story editor page elements
from src.test.utilities.wait_helper import wait_for_element_visible  # Helper function for waiting until elements are visible
from src.test.utilities.assertion_helper import assert_element_present  # Helper function for asserting elements are present
from src.test.fixtures.browser_fixtures import browser  # Fixture providing configured WebDriver instance
from src.test.fixtures.user_fixtures import authenticated_user  # Fixture providing authenticated user session
from src.test.utilities.screenshot_manager import take_screenshot  # Function for capturing screenshots during test execution

@pytest.mark.story_creation
def test_story_editor_page_loads(browser, authenticated_user):
    """Test that the story editor page loads correctly when creating a new story"""
    # Initialize DashboardPage with browser
    dashboard_page = DashboardPage(browser)
    
    # Click create story button on dashboard
    dashboard_page.click_create_story_button()
    
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    
    # Assert that story editor page is loaded
    assert story_editor_page.is_loaded(), "Story editor page did not load correctly"
    
    # Assert that all key elements are present on the page
    assert_element_present(browser, StoryEditorLocators.STORY_TITLE_INPUT, "Story Title Input Field")
    assert_element_present(browser, StoryEditorLocators.TEMPLATE_OPTIONS, "Template Options")
    assert_element_present(browser, StoryEditorLocators.SAVE_BUTTON, "Save Button")
    assert_element_present(browser, StoryEditorLocators.CONTENT_EDITOR, "Content Editor")

@pytest.mark.story_creation
def test_story_title_input(browser, authenticated_user):
    """Test that the story title input field accepts input correctly"""
    # Initialize DashboardPage with browser
    dashboard_page = DashboardPage(browser)
    
    # Click create story button on dashboard
    dashboard_page.click_create_story_button()
    
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    
    # Wait for story editor page to load
    story_editor_page.wait_for_editor_load()
    
    # Enter a test title in the title field
    test_title = "Test Story Title"
    story_editor_page.enter_story_title(test_title)
    
    # Verify that the title was correctly entered
    assert story_editor_page.get_story_title() == test_title, "Story title was not correctly entered"

@pytest.mark.story_creation
def test_template_selection(browser, authenticated_user):
    """Test that templates can be selected in the story editor"""
    # Initialize DashboardPage with browser
    dashboard_page = DashboardPage(browser)
    
    # Click create story button on dashboard
    dashboard_page.click_create_story_button()
    
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    
    # Wait for story editor page to load
    story_editor_page.wait_for_editor_load()
    
    # Assert that template options are displayed
    assert_element_present(browser, StoryEditorLocators.TEMPLATE_OPTIONS, "Template Options")
    
    # Select a template
    template_name = "Basic"  # Replace with a valid template name
    story_editor_page.select_template(template_name)
    
    # Verify that the template was selected correctly
    assert story_editor_page.get_selected_template() == template_name, "Template was not correctly selected"

@pytest.mark.story_creation
def test_content_editor_visibility(browser, authenticated_user):
    """Test that the content editor area is visible and interactive"""
    # Initialize DashboardPage with browser
    dashboard_page = DashboardPage(browser)
    
    # Click create story button on dashboard
    dashboard_page.click_create_story_button()
    
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    
    # Wait for story editor page to load
    story_editor_page.wait_for_editor_load()
    
    # Assert that content editor is visible
    assert_element_present(browser, StoryEditorLocators.CONTENT_EDITOR, "Content Editor")
    
    # Verify that content editor is interactive
    # This can be done by attempting to input text and verifying it
    test_content = "This is a test content"
    story_editor_page.input_content(test_content)
    assert story_editor_page.get_content() == test_content, "Content editor is not interactive"

@pytest.mark.story_creation
def test_save_button_functionality(browser, authenticated_user):
    """Test that the save button is present and functional"""
    # Initialize DashboardPage with browser
    dashboard_page = DashboardPage(browser)
    
    # Click create story button on dashboard
    dashboard_page.click_create_story_button()
    
    # Initialize StoryEditorPage with browser
    story_editor_page = StoryEditorPage(browser)
    
    # Wait for story editor page to load
    story_editor_page.wait_for_editor_load()
    
    # Enter a test title
    test_title = "Test Story for Save"
    story_editor_page.enter_story_title(test_title)
    
    # Assert that save button is visible and enabled
    assert_element_present(browser, StoryEditorLocators.SAVE_BUTTON, "Save Button")
    
    # Click save button
    story_editor_page.save_story()
    
    # Verify that save operation was successful
    assert story_editor_page.is_story_saved(), "Save operation was not successful"