import pytest  # pytest 7.3+
import time  # built-in

# Internal imports
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from src.test.fixtures.template_fixtures import template_data  # src/test/fixtures/template_fixtures.py
from src.test.pages.template_selection_page import TemplateSelectionPage  # src/test/pages/template_selection_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_equal  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_element_visible  # src/test/utilities/assertion_helper.py
from src/test.utilities.assertion_helper import assert_in  # src/test/utilities/assertion_helper.py

# Global variables
TEMPLATE_CATEGORIES = ["basic", "business", "creative"]
TEST_TEMPLATE_NAMES = ["Basic Template", "Blank Canvas", "Presentation Template", "Product Showcase", "Creative Portfolio"]
TEMPLATE_SEARCH_TERMS = [{"term": "Basic", "expected_count": 1}, {"term": "Template", "expected_count": 3}, {"term": "Portfolio", "expected_count": 1}, {"term": "nonexistent", "expected_count": 0}]
DEFAULT_TIMEOUT = 10


def test_navigate_to_template_selection(browser, authenticated_user):
    """Verify that a user can navigate to the template selection page from the dashboard"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Assert that template selection page is loaded successfully
    assert_true(template_selection_page.is_loaded(), "Template selection page should load successfully", driver=browser)
    # Assert that template options are visible on the page
    assert_element_visible(browser, TemplateSelectionPage(browser).TEMPLATE_OPTIONS, "Template options", driver=browser)


def test_template_selection_page_loads_correctly(browser, authenticated_user):
    """Verify that the template selection page loads with all expected elements"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Assert that template selection page is loaded
    assert_true(template_selection_page.is_loaded(), "Template selection page should load", driver=browser)
    # Assert that template categories section is visible
    assert_element_visible(browser, TemplateSelectionPage(browser).TEMPLATE_CATEGORIES, "Template categories section", driver=browser)
    # Assert that template options are visible
    assert_element_visible(browser, TemplateSelectionPage(browser).TEMPLATE_OPTIONS, "Template options", driver=browser)
    # Assert that search input is visible
    assert_element_visible(browser, TemplateSelectionPage(browser).SEARCH_TEMPLATES_INPUT, "Search input", driver=browser)


def test_get_available_templates(browser, authenticated_user, template_data):
    """Verify that the list of available templates matches expected templates from test data"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Get list of available templates using get_available_templates()
    available_templates = template_selection_page.get_available_templates()
    # Get expected template names from template_data fixture
    expected_templates = [template["name"] for template in template_data["templates"]]
    # Assert that all expected templates are in the available templates list
    for template in expected_templates:
        assert_in(template, available_templates, f"Template '{template}' should be in available templates", driver=browser)
    # Assert that the length of available templates matches expected count
    assert_equal(len(available_templates), len(expected_templates), "Number of available templates should match expected count", driver=browser)


@pytest.mark.parametrize("template_name", TEST_TEMPLATE_NAMES)
def test_select_template_by_name(browser, authenticated_user):
    """Verify that a user can select a template by its name and navigate to story editor"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Select template by name using select_template_by_name(template_name)
    story_editor_page = template_selection_page.select_template_by_name(template_name)
    # Initialize StoryEditorPage with browser instance
    # Assert that story editor page is loaded successfully
    assert_true(story_editor_page.is_loaded(), "Story editor page should load successfully", driver=browser)


@pytest.mark.parametrize("index", [0, 1, 2])
def test_select_template_by_index(browser, authenticated_user):
    """Verify that a user can select a template by its index in the list"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Select template by index using select_template_by_index(index)
    story_editor_page = template_selection_page.select_template_by_index(index)
    # Initialize StoryEditorPage with browser instance
    # Assert that story editor page is loaded successfully
    assert_true(story_editor_page.is_loaded(), "Story editor page should load successfully", driver=browser)


@pytest.mark.parametrize("category,expected_count", [("basic", 2), ("business", 2), ("creative", 1)])
def test_filter_templates_by_category(browser, authenticated_user, template_data):
    """Verify that templates can be filtered by category"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Filter templates by category using filter_templates_by_category(category)
    template_selection_page.filter_templates_by_category(category)
    # Get list of templates after filtering
    available_templates = template_selection_page.get_available_templates()
    # Assert that the number of templates matches the expected count
    assert_equal(len(available_templates), expected_count, f"Number of templates in category '{category}' should be {expected_count}", driver=browser)
    # Verify that all displayed templates belong to the selected category
    for template in available_templates:
        template_obj = next((t for t in template_data["templates"] if t["name"] == template), None)
        if template_obj:
            assert_equal(template_obj["category"], category, f"Template '{template}' should belong to category '{category}'", driver=browser)


@pytest.mark.parametrize("search_data", TEMPLATE_SEARCH_TERMS)
def test_search_templates(browser, authenticated_user):
    """Verify that templates can be searched by keywords"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Search templates using search_templates(search_data['term'])
    template_selection_page.search_templates(search_data['term'])
    # Get list of templates after searching
    available_templates = template_selection_page.get_available_templates()
    # Assert that the number of templates matches search_data['expected_count']
    assert_equal(len(available_templates), search_data['expected_count'], f"Number of templates matching '{search_data['term']}' should be {search_data['expected_count']}", driver=browser)
    # Verify that all displayed templates contain the search term in their name or description
    for template in available_templates:
        assert_in(search_data['term'].lower(), template.lower(), f"Template '{template}' should contain search term '{search_data['term']}'", driver=browser)


def test_get_template_description(browser, authenticated_user, template_data):
    """Verify that template descriptions can be retrieved and match expected values"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # For each template in template_data
    for template in template_data["templates"]:
        # Get template description using get_template_description(template_name)
        description = template_selection_page.get_template_description(template["name"])
        # Assert that the retrieved description matches the expected description from template_data
        assert_equal(description, template["description"], f"Description for template '{template['name']}' should match", driver=browser)


def test_blank_template_selection(browser, authenticated_user):
    """Verify that blank template can be selected successfully"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Select blank template using select_template_by_name('Blank Canvas')
    story_editor_page = template_selection_page.select_template_by_name('Blank Canvas')
    # Initialize StoryEditorPage with browser instance
    # Assert that story editor page is loaded successfully
    assert_true(story_editor_page.is_loaded(), "Story editor page should load successfully", driver=browser)
    # Verify that story editor is initialized with blank content
    assert_equal(story_editor_page.get_content(), "", "Story editor should be initialized with blank content", driver=browser)


def test_default_template_selection(browser, authenticated_user, template_data):
    """Verify that default template is correctly identified and can be selected"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Identify the default template from template_data
    default_template = next((t for t in template_data["templates"] if t["default"] == True), None)
    # Select the default template by name
    story_editor_page = template_selection_page.select_template_by_name(default_template["name"])
    # Initialize StoryEditorPage with browser instance
    # Assert that story editor page is loaded successfully
    assert_true(story_editor_page.is_loaded(), "Story editor page should load successfully", driver=browser)


def test_template_count(browser, authenticated_user, template_data):
    """Verify that the number of templates matches the expected count from template data"""
    # Initialize DashboardPage with browser instance
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Click create story button
    template_selection_page = dashboard_page.click_create_story_button()
    # Initialize TemplateSelectionPage with browser instance
    # Get list of available templates
    available_templates = template_selection_page.get_available_templates()
    # Get template count from template_data
    expected_count = len(template_data["templates"])
    # Assert that the number of available templates matches the expected count
    assert_equal(len(available_templates), expected_count, "Number of templates should match expected count", driver=browser)