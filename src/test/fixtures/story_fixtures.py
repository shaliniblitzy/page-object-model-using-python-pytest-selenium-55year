"""
Provides pytest fixtures for creating and managing test stories in the Storydoc application.
These fixtures support test cases that require story creation, editing, and manipulation.
"""

import pytest  # pytest 7.3+
import os
import json  # standard library
import time  # standard library
from typing import Dict, List  # built-in

# Internal imports
from .browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from .user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from .template_fixtures import random_template  # src/test/fixtures/template_fixtures.py
from ..pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from ..pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from ..utilities.random_data_generator import generate_random_story_title  # src/test/utilities/random_data_generator.py
from ..utilities.random_data_generator import generate_random_story_content  # src/test/utilities/random_data_generator.py
from ..utilities.random_data_generator import generate_test_story_data  # src/test/utilities/random_data_generator.py
from ..utilities.logger import log_info, log_debug, log_error  # src/test/utilities/logger.py
from pytest import FixtureRequest


def load_story_data() -> Dict:
    """Load story test data from JSON file

    Returns:
        dict: Dictionary containing story test data
    """
    try:
        # Get current directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to data directory
        data_dir = os.path.join(current_dir, "..", "data")
        # Construct full path to story_data.json
        story_data_path = os.path.join(data_dir, "story_data.json")

        # Open and read story_data.json file
        with open(story_data_path, "r") as file:
            data = json.load(file)

        # Parse JSON data into Python dictionary
        # Return the parsed data
        return data
    except FileNotFoundError:
        # Handle exceptions and return empty dictionary if file not found
        log_error("Story data file not found.")
        return {}
    except json.JSONDecodeError:
        log_error("Error decoding story data JSON.")
        return {}


def create_story(browser, title, template_name, content) -> Dict:
    """Create a new story in the Storydoc application

    Args:
        browser (webdriver.WebDriver): browser
        title (str): title
        template_name (str): template_name
        content (str): content

    Returns:
        dict: Dictionary containing created story details or None if creation failed
    """
    try:
        # Initialize dashboard_page with browser
        dashboard_page = DashboardPage(browser)
        # Navigate to dashboard page
        dashboard_page.navigate_to()
        # Verify dashboard page is loaded
        dashboard_page.is_loaded()
        # Click create story button
        dashboard_page.click_create_story_button()

        # Initialize story_editor_page with browser
        story_editor_page = StoryEditorPage(browser)
        # Verify story editor page is loaded
        story_editor_page.is_loaded()
        # Enter story title
        story_editor_page.enter_story_title(title)
        # Select template if provided
        story_editor_page.select_template(template_name)
        # Enter content if provided
        story_editor_page.edit_story_content(content)
        # Save story
        story_editor_page.save_story()
        # Verify story was saved successfully
        story_editor_page.is_story_saved()

        # Return dictionary with story details if successful
        return {"title": title, "template_name": template_name, "content": content}
    except Exception as e:
        # Log error and return None if any step fails
        log_error(f"Failed to create story: {e}")
        return None


@pytest.fixture
def story_title() -> str:
    """Fixture that generates a random story title

    Returns:
        str: Random story title
    """
    # Generate a random story title using generate_random_story_title()
    random_title = generate_random_story_title()
    # Log the generated title
    log_info(f"Generated story title: {random_title}")
    # Return the generated title
    return random_title


@pytest.fixture
def story_content(paragraphs: int = 3) -> str:
    """Fixture that generates random story content

    Args:
        paragraphs (int): paragraphs

    Returns:
        str: Random story content
    """
    # Set default paragraphs to 3 if not provided
    # Generate random content using generate_random_story_content(paragraphs)
    random_content = generate_random_story_content(paragraphs)
    # Log the content length
    log_info(f"Generated story content (length: {len(random_content)} characters)")
    # Return the generated content
    return random_content


@pytest.fixture
def sample_stories() -> List:
    """Fixture that provides sample story data from test data file

    Returns:
        list: List of sample story data dictionaries
    """
    # Load story data using load_story_data()
    story_data = load_story_data()
    # Extract the 'stories' list from the data
    stories = story_data.get("stories", [])
    # Log the number of sample stories loaded
    log_info(f"Loaded {len(stories)} sample stories")
    # Return the list of sample stories
    return stories


@pytest.fixture
def created_story(browser, authenticated_user, story_title, random_template, story_content) -> Dict:
    """Fixture that creates a new story and returns its details

    Args:
        browser (webdriver.WebDriver): browser
        authenticated_user (dict): authenticated_user
        story_title (str): story_title
        random_template (str): random_template
        story_content (str): story_content

    Returns:
        dict: Dictionary containing created story details
    """
    # Log creating story with provided title and template
    log_info(f"Creating story with title '{story_title}' and template '{random_template}'")
    # Create a story using create_story() function
    story_details = create_story(browser, story_title, random_template, story_content)
    # Verify story was created successfully
    assert story_details is not None, "Failed to create story"
    # Return story details dictionary
    return story_details
    # No specific cleanup required as browser fixture will handle cleanup


@pytest.fixture
def multiple_stories(browser, authenticated_user, random_template, request: FixtureRequest) -> List:
    """Fixture that creates multiple stories for testing

    Args:
        browser (webdriver.WebDriver): browser
        authenticated_user (dict): authenticated_user
        random_template (str): random_template
        request (pytest.FixtureRequest): request

    Returns:
        list: List of dictionaries containing created story details
    """
    # Get count parameter from request (default to 3)
    count = request.param if hasattr(request, 'param') else 3
    # Initialize empty list for story details
    story_details_list = []
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Loop count times:
    for i in range(count):
        # Generate a random story title
        story_title = generate_random_story_title()
        # Generate random story content
        story_content = generate_random_story_content()
        # Create a story using create_story() function
        story_details = create_story(browser, story_title, random_template, story_content)
        # Add story details to the list
        story_details_list.append(story_details)
        # Navigate back to dashboard if more stories to create
        if i < count - 1:
            dashboard_page.navigate_to()
    # Log number of stories created
    log_info(f"Created {len(story_details_list)} stories")
    # Return the list of story details
    return story_details_list
    # No specific cleanup required as browser fixture will handle cleanup


def delete_stories(browser, story_titles: List) -> bool:
    """Helper function to delete stories by title

    Args:
        browser (webdriver.WebDriver): browser
        story_titles (list): story_titles

    Returns:
        bool: True if all stories were deleted, False otherwise
    """
    # Initialize dashboard_page with browser
    dashboard_page = DashboardPage(browser)
    # Navigate to dashboard page
    dashboard_page.navigate_to()
    # Verify dashboard page is loaded
    dashboard_page.is_loaded()
    # Loop through story_titles:
    for title in story_titles:
        # Check if story is present
        if dashboard_page.is_story_present(title):
            # Delete the story if present
            dashboard_page.delete_story(title)
    # Return True if all stories were deleted, False otherwise
    return True