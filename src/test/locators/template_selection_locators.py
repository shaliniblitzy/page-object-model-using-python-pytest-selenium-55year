"""
Contains Selenium WebDriver locators for the template selection interface in the Storydoc application.

This module provides the locator strategies needed for automated testing of the template selection
functionality, which is part of the Story Creation feature (F-003).
"""

from selenium.webdriver.common.by import By  # version: 4.10+


class TemplateSelectionLocators:
    """Contains locators for the template selection interface in the Storydoc application."""

    # Main template section container
    TEMPLATE_SECTION = (By.CSS_SELECTOR, '.template-section')
    
    # Container for all template options
    TEMPLATE_OPTIONS = (By.CSS_SELECTOR, '.template-options')
    
    # Individual template item
    TEMPLATE_ITEM = (By.CSS_SELECTOR, '.template-item')
    
    # Template name element
    TEMPLATE_NAME = (By.CSS_SELECTOR, '.template-name')
    
    # Template preview image
    TEMPLATE_PREVIEW = (By.CSS_SELECTOR, '.template-preview')
    
    # Template description text
    TEMPLATE_DESCRIPTION = (By.CSS_SELECTOR, '.template-description')
    
    # Button to select a template
    SELECT_TEMPLATE_BUTTON = (By.CSS_SELECTOR, '.select-template-button')
    
    # Visual indicator for selected template
    SELECTED_TEMPLATE_INDICATOR = (By.CSS_SELECTOR, '.selected-template-indicator')
    
    # Search input for filtering templates
    SEARCH_TEMPLATES_INPUT = (By.CSS_SELECTOR, '.search-templates-input')
    
    # Container for template categories
    TEMPLATE_CATEGORIES = (By.CSS_SELECTOR, '.template-categories')
    
    # Individual category item
    TEMPLATE_CATEGORY_ITEM = (By.CSS_SELECTOR, '.template-category-item')
    
    # Filter control for templates
    TEMPLATE_FILTER = (By.CSS_SELECTOR, '.template-filter')
    
    # Loading indicator displayed during template loading
    LOADING_INDICATOR = (By.CSS_SELECTOR, '.loading-indicator')