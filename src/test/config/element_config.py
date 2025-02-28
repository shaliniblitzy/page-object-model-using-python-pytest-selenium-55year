"""
Element Configuration module for Storydoc test automation framework.

This module defines configuration settings for UI elements including default settings for 
element interactions, wait strategies, retry configurations, and error messages. These 
configurations ensure consistent element handling and reliable test execution across the framework.

The configuration defined here addresses the following requirements:
- Reliability: Supports consistent test execution with minimal flakiness
- Error Handling: Implements a robust strategy for handling element interaction failures
- Explicit Waits: Configures appropriate wait strategies for handling timing and synchronization issues
"""

from selenium.webdriver.common.by import By  # selenium 4.10+
from .timeout_config import (
    ELEMENT_TIMEOUT,
    ELEMENT_CLICKABLE_TIMEOUT,
    ELEMENT_PRESENCE_TIMEOUT,
    ELEMENT_DISAPPEAR_TIMEOUT
)

# Define TIMEOUT_DEFAULTS dictionary for element configurations
TIMEOUT_DEFAULTS = {
    'element': ELEMENT_TIMEOUT,
    'visibility': ELEMENT_TIMEOUT,
    'clickable': ELEMENT_CLICKABLE_TIMEOUT,
    'presence': ELEMENT_PRESENCE_TIMEOUT,
    'disappear': ELEMENT_DISAPPEAR_TIMEOUT
}

# Global default timeouts
DEFAULT_ELEMENT_TIMEOUT = TIMEOUT_DEFAULTS['element']
DEFAULT_VISIBILITY_TIMEOUT = TIMEOUT_DEFAULTS['visibility']
DEFAULT_CLICKABLE_TIMEOUT = TIMEOUT_DEFAULTS['clickable']
DEFAULT_PRESENCE_TIMEOUT = TIMEOUT_DEFAULTS['presence']

# Element configuration for the framework
ELEMENT_CONFIG = {
    # Wait strategy configuration
    'wait_strategy': {
        'default_strategy': 'visibility',  # Default wait strategy: visibility, presence, clickable
        'timeout': DEFAULT_ELEMENT_TIMEOUT,  # Default timeout in seconds
        'polling_interval': 0.5,  # Default polling interval in seconds
        'ignored_exceptions': [  # Exceptions to ignore during waits
            'StaleElementReferenceException',
            'NoSuchElementException',
            'ElementNotVisibleException',
            'ElementNotInteractableException',
        ],
    },
    
    # Retry configuration for flaky operations
    'retry_config': {
        'enabled': True,  # Enable retry mechanism
        'max_attempts': 3,  # Maximum number of retry attempts
        'retry_interval': 1,  # Time to wait between retries in seconds
        'backoff_factor': 2,  # Exponential backoff factor for retry intervals
        'retry_on_exceptions': [  # Exceptions that should trigger a retry
            'StaleElementReferenceException',
            'ElementClickInterceptedException',
            'TimeoutException',
            'WebDriverException',
        ],
    },
    
    # General element interaction settings
    'screenshot_on_failure': True,  # Capture screenshot on element interaction failures
    'highlight_elements': False,  # Highlight elements during interactions (for debugging)
    'default_polling_interval': 0.5,  # Default polling interval for waits
    'strict_visible_check': True,  # Enforce strict visibility check (element must be fully visible)
    'scroll_into_view': True,  # Auto-scroll elements into view before interaction
    'stale_element_retry': True,  # Automatically retry on stale element reference exceptions
}

# Mapping between friendly names and Selenium's By locator strategies
LOCATOR_STRATEGIES = {
    'id': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR,
    'class_name': By.CLASS_NAME,
    'link_text': By.LINK_TEXT,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag_name': By.TAG_NAME,
}

# Preferred order of locator strategies (from most to least reliable)
PREFERRED_LOCATOR_ORDER = [
    'id',
    'name',
    'css',
    'xpath',
    'class_name',
    'link_text',
    'partial_link_text',
    'tag_name',
]

# Configuration for different types of element interactions
ELEMENT_INTERACTIONS = {
    'click': {
        'wait_strategy': 'clickable',
        'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        'retry_on_failure': True,
        'move_to_element': True,  # Move to element before clicking
        'custom_js': False,  # Use JavaScript for click (useful for certain elements)
        'double_check': False,  # Verify click was successful
    },
    'input': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'clear_before_input': True,  # Clear field before entering text
        'press_enter': False,  # Press Enter after text input
        'validate_input': False,  # Validate input was accepted correctly
    },
    'select': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'retry_on_failure': True,
        'by_visible_text': True,  # Select by visible text (alternative: by value)
    },
    'drag_and_drop': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'retry_on_failure': True,
        'html5': False,  # Use HTML5 drag and drop API
        'custom_js': True,  # Use JavaScript for drag and drop (more reliable)
    },
    'hover': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'custom_js': False,  # Use JavaScript for hover
    },
    'double_click': {
        'wait_strategy': 'clickable',
        'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        'retry_on_failure': True,
        'custom_js': False,  # Use JavaScript for double click
    },
    'right_click': {
        'wait_strategy': 'clickable',
        'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        'retry_on_failure': True,
        'custom_js': False,  # Use JavaScript for right click
    },
    'clear': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'retry_on_failure': True,
        'custom_js': False,  # Use JavaScript for clear
    },
    'get_text': {
        'wait_strategy': 'visibility',
        'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        'trim': True,  # Trim whitespace from text
        'normalize': True,  # Normalize whitespace (replace multiple with single space)
    },
    'get_attribute': {
        'wait_strategy': 'presence',
        'timeout': DEFAULT_PRESENCE_TIMEOUT,
    },
    'is_selected': {
        'wait_strategy': 'presence',
        'timeout': DEFAULT_PRESENCE_TIMEOUT,
    },
    'is_enabled': {
        'wait_strategy': 'presence',
        'timeout': DEFAULT_PRESENCE_TIMEOUT,
    },
    'is_displayed': {
        'wait_strategy': 'presence',
        'timeout': DEFAULT_PRESENCE_TIMEOUT,
        'strict': False,  # Strict check (element must be in viewport)
    },
}

# Error messages for element interaction failures
ELEMENT_ERROR_MESSAGES = {
    'element_not_found': "Element '{element}' was not found on page '{page}' using locator '{locator}'",
    'element_not_visible': "Element '{element}' was found but not visible on page '{page}'",
    'element_not_clickable': "Element '{element}' was found but not clickable on page '{page}'. Reason: {reason}",
    'element_not_enabled': "Element '{element}' was found but not enabled on page '{page}'",
    'stale_element': "Element '{element}' reference is stale or no longer attached to the DOM",
    'timeout': "Timed out after {timeout} seconds waiting for element '{element}' on page '{page}'",
}

# Specific element configurations for different areas of the application
ELEMENT_SPECIFIC_CONFIG = {
    'signup': {
        'form_fields': {
            'email': {
                'required': True,
                'validation': {
                    'pattern': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                    'error_message': 'Please enter a valid email address',
                },
            },
            'password': {
                'required': True,
                'validation': {
                    'min_length': 8,
                    'error_message': 'Password must be at least 8 characters long',
                },
            },
            'name': {
                'required': True,
                'validation': {
                    'min_length': 2,
                    'error_message': 'Please enter your name',
                },
            },
            'terms': {
                'required': True,
                'validation': {
                    'checked': True,
                    'error_message': 'You must accept the terms and conditions',
                },
            },
        },
        'submit_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
    },
    'signin': {
        'form_fields': {
            'email': {
                'required': True,
                'validation': {
                    'pattern': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                    'error_message': 'Please enter a valid email address',
                },
            },
            'password': {
                'required': True,
            },
        },
        'submit_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
    },
    'dashboard': {
        'create_story_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
        'story_list': {
            'wait_strategy': 'visibility',
            'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        },
    },
    'story_editor': {
        'title_field': {
            'required': True,
            'wait_strategy': 'visibility',
            'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        },
        'template_options': {
            'wait_strategy': 'visibility',
            'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        },
        'save_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
        'share_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
    },
    'share_dialog': {
        'recipient_email': {
            'required': True,
            'validation': {
                'pattern': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                'error_message': 'Please enter a valid email address',
            },
            'wait_strategy': 'visibility',
            'timeout': DEFAULT_VISIBILITY_TIMEOUT,
        },
        'share_button': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
        },
    },
    'mailinator': {
        'inbox_refresh': {
            'wait_strategy': 'clickable',
            'timeout': DEFAULT_CLICKABLE_TIMEOUT,
            'polling_interval': 5,  # Polling interval for checking emails
            'timeout_value': 60,  # Maximum time to wait for email
        },
    },
}