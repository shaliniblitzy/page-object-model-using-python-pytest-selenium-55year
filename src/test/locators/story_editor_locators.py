from selenium.webdriver.common.by import By  # version: 4.10+
from .base_locators import BaseLocators


class StoryEditorLocators(BaseLocators):
    """
    Defines locators for UI elements on the Story Editor page.
    These locators are used by the StoryEditorPage class to interact with UI elements
    for creating and editing stories.
    """
    
    # Story title input field
    STORY_TITLE_INPUT = (By.CSS_SELECTOR, "input.story-title")
    
    # Template selection section and options
    TEMPLATE_OPTIONS = (By.CSS_SELECTOR, ".template-option")
    TEMPLATE_ITEM = (By.CSS_SELECTOR, ".template-item")
    SELECTED_TEMPLATE = (By.CSS_SELECTOR, ".template-option.selected")
    
    # Content editor area
    CONTENT_EDITOR = (By.CSS_SELECTOR, ".content-editor")
    EDITOR_TOOLBAR = (By.CSS_SELECTOR, ".editor-toolbar")
    
    # Action buttons
    SAVE_BUTTON = (By.CSS_SELECTOR, ".save-button")
    SAVE_SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".save-success-message")
    SHARE_BUTTON = (By.CSS_SELECTOR, ".share-button")
    PREVIEW_BUTTON = (By.CSS_SELECTOR, ".preview-button")
    
    # Status indicators
    AUTOSAVE_INDICATOR = (By.CSS_SELECTOR, ".autosave-indicator")
    
    # Formatting tools
    TEXT_FORMATTING_TOOLS = (By.CSS_SELECTOR, ".formatting-tools")
    INSERT_IMAGE_BUTTON = (By.CSS_SELECTOR, ".insert-image-button")
    INSERT_VIDEO_BUTTON = (By.CSS_SELECTOR, ".insert-video-button")
    INSERT_CHART_BUTTON = (By.CSS_SELECTOR, ".insert-chart-button")
    
    # Page sections
    TEMPLATE_SECTION = (By.CSS_SELECTOR, ".template-section")
    CONTENT_SECTION = (By.CSS_SELECTOR, ".content-section")
    
    # Story editor specific cancel button (overrides BaseLocators.CANCEL_BUTTON)
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".story-editor-cancel-button")
    
    # Dialog elements
    DISCARD_CHANGES_DIALOG = (By.CSS_SELECTOR, ".discard-changes-dialog")
    CONFIRM_DISCARD_BUTTON = (By.CSS_SELECTOR, ".confirm-discard-button")