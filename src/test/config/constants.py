"""
Constants module for Storydoc test automation framework.

This module defines all constant values used throughout the test automation framework
including timeouts, URLs, browser settings, email configuration, and other essential
constants needed for test execution and configuration.
"""

import os
from pathlib import Path

# Directory Structure
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_ROOT = PROJECT_ROOT / 'test'
CONFIG_DIR = TEST_ROOT / 'config'
DATA_DIR = TEST_ROOT / 'data'
REPORTS_DIR = TEST_ROOT / 'reports'
SCREENSHOTS_DIR = REPORTS_DIR / 'screenshots'
LOGS_DIR = REPORTS_DIR / 'logs'

# Timeout Constants
TIMEOUTS = {
    'DEFAULT': int(os.getenv('DEFAULT_TIMEOUT', 10)),
    'ELEMENT': int(os.getenv('ELEMENT_TIMEOUT', 20)),
    'PAGE_LOAD': int(os.getenv('PAGE_LOAD_TIMEOUT', 30)),
    'SCRIPT': int(os.getenv('SCRIPT_TIMEOUT', 30)),
    'EMAIL': int(os.getenv('EMAIL_TIMEOUT', 60))
}

# Performance Thresholds
PERFORMANCE = {
    'PAGE_LOAD_THRESHOLD': int(os.getenv('PAGE_LOAD_THRESHOLD', 5)),
    'ELEMENT_INTERACTION_THRESHOLD': int(os.getenv('ELEMENT_INTERACTION_THRESHOLD', 2)),
    'FORM_SUBMISSION_THRESHOLD': int(os.getenv('FORM_SUBMISSION_THRESHOLD', 3)),
    'EMAIL_DELIVERY_THRESHOLD': int(os.getenv('EMAIL_DELIVERY_THRESHOLD', 30))
}

# URL Constants
URLS = {
    'BASE': os.getenv('BASE_URL', 'https://editor-staging.storydoc.com'),
    'SIGNUP': '/sign-up',
    'SIGNIN': '/sign-in',
    'DASHBOARD': '/dashboard',
    'STORY_EDITOR': '/editor',
    'TEMPLATE_SELECTION': '/templates',
    'SHARED_STORY': '/shared'
}

# Browser Constants
BROWSERS = {
    'CHROME': 'chrome',
    'FIREFOX': 'firefox',
    'EDGE': 'edge'
}

# Mailinator Configuration
MAILINATOR = {
    'BASE_URL': os.getenv('MAILINATOR_API_URL', 'https://api.mailinator.com/api/v2'),
    'INBOX_ENDPOINT': '/domains/{domain}/inboxes/{inbox}',
    'MESSAGE_ENDPOINT': '/message/{message_id}',
    'PUBLIC_URL': 'https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox}'
}

# Email Patterns
EMAIL_PATTERNS = {
    'VERIFICATION': os.getenv('VERIFICATION_PATTERN', 'verify|confirm|activate'),
    'SHARING': os.getenv('SHARING_PATTERN', 'story|share|view')
}

# Service Level Agreement Thresholds
SLA = {
    'USER_REGISTRATION': 30,
    'USER_AUTHENTICATION': 20,
    'STORY_CREATION': 45,
    'STORY_SHARING': 60,
    'FULL_WORKFLOW': 180
}

# Element Type Constants
ELEMENT_TYPES = {
    'INPUT': 'input',
    'BUTTON': 'button',
    'LINK': 'link',
    'CHECKBOX': 'checkbox',
    'RADIO': 'radio',
    'DROPDOWN': 'dropdown',
    'TEXT': 'text',
    'IMAGE': 'image'
}

# Locator Type Constants
LOCATOR_TYPES = {
    'ID': 'id',
    'NAME': 'name',
    'CLASS_NAME': 'class name',
    'CSS_SELECTOR': 'css selector',
    'XPATH': 'xpath',
    'LINK_TEXT': 'link text',
    'PARTIAL_LINK_TEXT': 'partial link text',
    'TAG_NAME': 'tag name'
}

# File Type Constants
FILE_TYPES = {
    'SCREENSHOT': 'png',
    'LOG': 'log',
    'REPORT': 'html',
    'DATA': 'json'
}

# Test Status Constants
STATUS = {
    'PASS': 'PASS',
    'FAIL': 'FAIL',
    'SKIP': 'SKIP',
    'ERROR': 'ERROR',
    'BLOCKED': 'BLOCKED'
}

# Test User Constants
TEST_USER = {
    'EMAIL_PREFIX': 'test.storydoc',
    'PASSWORD': os.getenv('TEST_PASSWORD', 'Test@123'),
    'NAME': os.getenv('TEST_USER_NAME', 'Test User')
}

# Test Data Constants
TEST_DATA = {
    'STORY_TITLE_PREFIX': 'Test Story',
    'TEMPLATE_NAME': 'Basic',
    'RECIPIENT_EMAIL_PREFIX': 'recipient.storydoc'
}

# Retry Constants
RETRY = {
    'MAX_ATTEMPTS': int(os.getenv('MAX_RETRY_ATTEMPTS', 3)),
    'BASE_DELAY': int(os.getenv('RETRY_BASE_DELAY', 2)),
    'MAX_DELAY': int(os.getenv('RETRY_MAX_DELAY', 10)),
    'BACKOFF_FACTOR': float(os.getenv('RETRY_BACKOFF_FACTOR', 1.5))
}


def get_absolute_path(relative_path: str) -> Path:
    """
    Converts a relative path to an absolute path based on project root
    
    Args:
        relative_path: Relative path from project root
        
    Returns:
        Path: The absolute path
    """
    return PROJECT_ROOT / relative_path


def get_url(page_name: str) -> str:
    """
    Constructs a complete URL for a specific page
    
    Args:
        page_name: Name of the page as defined in URLS dictionary
        
    Returns:
        str: The complete URL
    """
    base_url = URLS['BASE']
    if page_name in URLS:
        return f"{base_url}{URLS[page_name]}"
    return base_url


def get_timeout(timeout_name: str) -> int:
    """
    Gets the appropriate timeout value for a specific operation
    
    Args:
        timeout_name: Name of the timeout as defined in TIMEOUTS dictionary
        
    Returns:
        int: Timeout value in seconds
    """
    if timeout_name in TIMEOUTS:
        return TIMEOUTS[timeout_name]
    return TIMEOUTS['DEFAULT']


def get_sla_threshold(operation_name: str) -> int:
    """
    Gets the SLA threshold for a specific operation
    
    Args:
        operation_name: Name of the operation as defined in SLA dictionary
        
    Returns:
        int: SLA threshold in seconds or None if not found
    """
    return SLA.get(operation_name)