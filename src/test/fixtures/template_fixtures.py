"""
Provides pytest fixtures for template-related functionality in the Storydoc automation framework.
These fixtures support tests for template selection and story creation with templates.
"""

import pytest
import json
import os
import random

from ..pages.template_selection_page import TemplateSelectionPage
from ..pages.story_editor_page import StoryEditorPage
from ..utilities.random_data_generator import generate_random_story_title


@pytest.fixture
def template_data():
    """
    Fixture that loads template data from JSON file

    Returns:
        dict: Dictionary containing template data
    """
    # Construct path to template_data.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    template_data_path = os.path.join(data_dir, "template_data.json")

    # Open the file and load JSON data
    with open(template_data_path, "r") as file:
        data = json.load(file)

    return data


@pytest.fixture
def template_selection_page(browser):
    """
    Fixture that provides a TemplateSelectionPage instance

    Args:
        browser: WebDriver instance

    Returns:
        TemplateSelectionPage: Initialized TemplateSelectionPage object
    """
    # Initialize TemplateSelectionPage with the browser fixture
    return TemplateSelectionPage(browser)


@pytest.fixture
def story_editor_page(browser):
    """
    Fixture that provides a StoryEditorPage instance

    Args:
        browser: WebDriver instance

    Returns:
        StoryEditorPage: Initialized StoryEditorPage object
    """
    # Initialize StoryEditorPage with the browser fixture
    return StoryEditorPage(browser)


@pytest.fixture
def random_template(template_data):
    """
    Fixture that provides a randomly selected template

    Args:
        template_data: Dictionary containing template data

    Returns:
        dict: Data for a randomly selected template
    """
    # Extract templates list from template_data
    templates = template_data.get("templates", [])
    
    # Use random.choice to select a random template
    template = random.choice(templates)
    
    return template


@pytest.fixture
def basic_template(template_data):
    """
    Fixture that provides the basic template data

    Args:
        template_data: Dictionary containing template data

    Returns:
        dict: Data for the basic template
    """
    # Filter template_data to find the template with id 'basic'
    templates = template_data.get("templates", [])
    basic_template = next((t for t in templates if t.get("id") == "basic"), None)
    
    return basic_template


@pytest.fixture
def story_with_template(browser, story_editor_page, template_data):
    """
    Fixture that creates a story with a specified template

    Args:
        browser: WebDriver instance
        story_editor_page: StoryEditorPage instance
        template_data: Dictionary containing template data

    Returns:
        tuple: Story title and template ID
    """
    # Generate a random story title
    story_title = generate_random_story_title()
    
    # Get the default template from template_data
    templates = template_data.get("templates", [])
    default_template = templates[0] if templates else None
    template_name = default_template.get("name") if default_template else "Basic"
    template_id = default_template.get("id") if default_template else "basic"
    
    # Enter the story title using story_editor_page
    story_editor_page.enter_story_title(story_title)
    
    # Select the template using story_editor_page
    story_editor_page.select_template(template_name)
    
    # Save the story
    story_editor_page.save_story()
    
    # Return tuple of (story_title, template_id)
    return story_title, template_id


@pytest.fixture
def story_with_random_template(browser, story_editor_page, random_template):
    """
    Fixture that creates a story with a random template

    Args:
        browser: WebDriver instance
        story_editor_page: StoryEditorPage instance
        random_template: Data for a randomly selected template

    Returns:
        tuple: Story title and template ID
    """
    # Generate a random story title
    story_title = generate_random_story_title()
    
    # Get the template name and ID
    template_name = random_template.get("name")
    template_id = random_template.get("id")
    
    # Enter the story title using story_editor_page
    story_editor_page.enter_story_title(story_title)
    
    # Select the random template using story_editor_page
    story_editor_page.select_template(template_name)
    
    # Save the story
    story_editor_page.save_story()
    
    # Return tuple of (story_title, template_id)
    return story_title, template_id


@pytest.fixture(params=["basic", "business", "creative"])
def template_by_category(template_data, request):
    """
    Fixture that provides a template from a specified category

    Args:
        template_data: Dictionary containing template data
        request: Pytest request object with the current parameter value

    Returns:
        dict: Template data from the specified category
    """
    # Use the category_id parameter or the current pytest parameter value
    category_id = request.param
    
    # Filter template_data to find templates in the specified category
    templates = template_data.get("templates", [])
    category_templates = [t for t in templates if t.get("category") == category_id]
    
    # Return the first template in that category, or None if none found
    return category_templates[0] if category_templates else None