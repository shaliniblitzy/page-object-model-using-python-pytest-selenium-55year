import pytest  # pytest >=7.0.0

from src.test.pages.story_editor_page import StoryEditorPage
from src.test.pages.template_selection_page import TemplateSelectionPage
from src.test.fixtures.browser_fixtures import browser
from src.test.fixtures.template_fixtures import template_data, template_selection_page, story_editor_page, random_template
from src.test.utilities.assertion_helper import assert_true, assert_equal, assert_in


def test_template_selection_page_loads(browser, template_selection_page):
    """Test that the template selection page loads correctly"""
    # Verify that the template selection page loads successfully
    assert_true(template_selection_page.is_loaded(), "Template selection page should load successfully", driver=browser)
    # Check that template section is visible
    assert_true(template_selection_page.is_element_visible(template_selection_page.TEMPLATE_SECTION), "Template section should be visible", driver=browser)
    # Check that template options are visible
    assert_true(template_selection_page.is_element_visible(template_selection_page.TEMPLATE_OPTIONS), "Template options should be visible", driver=browser)


def test_available_templates_displayed(browser, template_selection_page, template_data):
    """Test that available templates are displayed correctly"""
    # Get list of available templates from the page
    available_templates = template_selection_page.get_available_templates()
    # Get list of templates from test data
    expected_templates = [template['name'] for template in template_data['templates']]
    # Verify that the number of displayed templates matches the expected count
    assert_equal(len(available_templates), len(expected_templates), "Number of displayed templates should match expected count", driver=browser)
    # Verify that each template in the test data is displayed on the page
    for template in expected_templates:
        assert_in(template, available_templates, f"Template '{template}' should be displayed on the page", driver=browser)


def test_template_selection_by_name(browser, template_selection_page, template_data):
    """Test selecting a template by name"""
    # Get the name of the default template from test data
    default_template_name = template_data['templates'][0]['name']
    # Select the template by name
    story_editor = template_selection_page.select_template_by_name(default_template_name)
    # Verify that the StoryEditorPage is returned after selection
    assert_true(isinstance(story_editor, StoryEditorPage), "Selecting a template should return a StoryEditorPage instance", driver=browser)
    # Verify that the selected template in the editor matches the template that was selected
    assert_equal(story_editor.get_selected_template(), default_template_name, "Selected template in editor should match the template that was selected", driver=browser)


def test_template_selection_by_index(browser, template_selection_page):
    """Test selecting a template by index"""
    # Get the list of available templates
    available_templates = template_selection_page.get_available_templates()
    # Select the first template by index (0)
    story_editor = template_selection_page.select_template_by_index(0)
    # Verify that the StoryEditorPage is returned after selection
    assert_true(isinstance(story_editor, StoryEditorPage), "Selecting a template should return a StoryEditorPage instance", driver=browser)
    # Verify that a template was successfully selected in the editor
    assert_true(story_editor.get_selected_template() is not None, "A template should be selected in the editor", driver=browser)


def test_template_filtering_by_category(browser, template_selection_page, template_data):
    """Test filtering templates by category"""
    # Get list of available categories from the page
    available_categories = template_selection_page.get_available_categories()
    # Select a specific category (e.g., 'Business Templates')
    category_name = 'Business Templates'
    # Get filtered templates
    template_selection_page.filter_templates_by_category(category_name)
    # Verify that only templates from the selected category are displayed
    filtered_templates = template_selection_page.get_available_templates()
    # Verify the count of filtered templates matches the expected count for the category
    expected_count = len([t for t in template_data['templates'] if t['category'] == 'business'])
    assert_equal(len(filtered_templates), expected_count, f"Number of templates in '{category_name}' category should match expected count", driver=browser)


def test_template_description_displayed(browser, template_selection_page, template_data):
    """Test that template descriptions are displayed correctly"""
    # Get the first template from test data
    first_template = template_data['templates'][0]
    # Get the description for that template from the page
    template_description = template_selection_page.get_template_description(first_template['name'])
    # Verify that the displayed description matches the expected description from test data
    assert_equal(template_description, first_template['description'], "Template description should match expected description", driver=browser)


def test_select_random_template(browser, template_selection_page, random_template):
    """Test selecting a random template"""
    # Get random template name from the random_template fixture
    template_name = random_template['name']
    # Verify that the template exists on the page
    assert_true(template_selection_page.is_template_available(template_name), f"Template '{template_name}' should be available", driver=browser)
    # Select the random template
    story_editor = template_selection_page.select_template_by_name(template_name)
    # Verify that the StoryEditorPage is returned after selection
    assert_true(isinstance(story_editor, StoryEditorPage), "Selecting a template should return a StoryEditorPage instance", driver=browser)
    # Verify that the selected template in the editor matches the random template
    assert_equal(story_editor.get_selected_template(), template_name, "Selected template in editor should match the random template", driver=browser)


def test_blank_template_selection(browser, template_selection_page):
    """Test selecting the blank template option"""
    # Select the blank template using select_blank_template method
    story_editor = template_selection_page.select_blank_template()
    # Verify that the StoryEditorPage is returned after selection
    assert_true(isinstance(story_editor, StoryEditorPage), "Selecting a template should return a StoryEditorPage instance", driver=browser)
    # Verify that the selected template in the editor is the blank template
    assert_equal(story_editor.get_selected_template(), "Blank", "Selected template in editor should be the blank template", driver=browser)


def test_template_selection_in_story_editor(browser, story_editor_page, template_data):
    """Test template selection directly in the story editor"""
    # Verify that the story editor page is loaded
    assert_true(story_editor_page.is_loaded(), "Story editor page should be loaded", driver=browser)
    # Get list of available templates from the editor
    available_templates = story_editor_page.get_available_templates()
    # Select a specific template from the list
    template_name = template_data['templates'][0]['name']
    story_editor_page.select_template(template_name)
    # Verify that the selected template is applied in the editor
    assert_true(story_editor_page.is_template_available(template_name), f"Template '{template_name}' should be available in the editor", driver=browser)
    # Get the selected template name from the editor
    selected_template = story_editor_page.get_selected_template()
    # Verify it matches the expected template name
    assert_equal(selected_template, template_name, "Selected template in editor should match the selected template", driver=browser)


def test_changing_template_after_selection(browser, story_editor_page, template_data):
    """Test changing the template after initial selection"""
    # Verify that the story editor page is loaded
    assert_true(story_editor_page.is_loaded(), "Story editor page should be loaded", driver=browser)
    # Select an initial template
    initial_template_name = template_data['templates'][0]['name']
    story_editor_page.select_template(initial_template_name)
    # Verify the initial template is selected correctly
    assert_equal(story_editor_page.get_selected_template(), initial_template_name, "Initial template should be selected correctly", driver=browser)
    # Select a different template
    new_template_name = template_data['templates'][1]['name']
    story_editor_page.select_template(new_template_name)
    # Verify that the template has changed to the new selection
    assert_equal(story_editor_page.get_selected_template(), new_template_name, "Template should have changed to the new selection", driver=browser)