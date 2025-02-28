"""
Configuration module for Mailinator service integration.

This module provides settings and utilities for Mailinator API access,
domain configuration, and email verification required for user registration
and story sharing test workflows.
"""

import os
import json
import time
import random

# Internal imports
from .environment_config import get_mailinator_domain
from .constants import (
    MAILINATOR,
    TIMEOUTS,
    RETRY,
    TEST_USER,
    DATA_DIR
)

# Default domain from environment configuration
DEFAULT_DOMAIN = get_mailinator_domain()

# Mailinator API configuration
MAILINATOR_BASE_URL = os.getenv('MAILINATOR_API_URL', MAILINATOR['BASE_URL'])
MAILINATOR_INBOX_ENDPOINT = MAILINATOR['INBOX_ENDPOINT']
MAILINATOR_MESSAGE_ENDPOINT = MAILINATOR['MESSAGE_ENDPOINT']
MAILINATOR_API_KEY = os.getenv('MAILINATOR_API_KEY', None)
MAILINATOR_TIMEOUT = int(os.getenv('MAILINATOR_TIMEOUT', TIMEOUTS['EMAIL']))
MAILINATOR_POLLING_INTERVAL = int(os.getenv('MAILINATOR_POLLING_INTERVAL', 5))
MAILINATOR_VERIFY_SSL = os.getenv('MAILINATOR_VERIFY_SSL', 'True').lower() == 'true'

# Retry configuration for API operations
RETRY_CONFIG = {
    'max_attempts': RETRY['MAX_ATTEMPTS'],
    'delay': RETRY['BASE_DELAY'],
    'backoff_factor': RETRY['BACKOFF_FACTOR']
}

# Email subject configuration for different workflow types
EMAIL_SUBJECT_CONFIG = {
    'registration': os.getenv('REGISTRATION_EMAIL_SUBJECT', 'Welcome to Storydoc'),
    'sharing': os.getenv('SHARING_EMAIL_SUBJECT', 'Story shared with you')
}

# Path to the domains configuration file
DOMAINS_FILE = DATA_DIR / 'mailinator_domains.json'


def _load_domains():
    """
    Loads Mailinator domains from the JSON configuration file
    
    Returns:
        dict: Dictionary containing domain configurations
    """
    try:
        if DOMAINS_FILE.exists():
            with open(DOMAINS_FILE, 'r') as file:
                return json.load(file)
        else:
            # Return default domain configuration if file doesn't exist
            return {
                'available_domains': ['mailinator.com'],
                'domain_attributes': {
                    'mailinator.com': {
                        'supports_api': True,
                        'public_access': True,
                        'retention_days': 1
                    }
                }
            }
    except (json.JSONDecodeError, IOError) as e:
        # Return default domain configuration on error
        print(f"Error loading domains file: {e}")
        return {
            'available_domains': ['mailinator.com'],
            'domain_attributes': {
                'mailinator.com': {
                    'supports_api': True,
                    'public_access': True,
                    'retention_days': 1
                }
            }
        }


# Load domains configuration
DOMAINS = _load_domains()


def get_headers():
    """
    Returns headers for Mailinator API requests including authentication if API key is available
    
    Returns:
        dict: Headers dictionary for API requests
    """
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Add authorization header if API key is available
    if MAILINATOR_API_KEY:
        headers['Authorization'] = f'Bearer {MAILINATOR_API_KEY}'
    
    return headers


def generate_email_address(prefix=None, domain=None):
    """
    Generates a unique email address for testing purposes
    
    Args:
        prefix (str): Optional prefix for the email address
        domain (str): Optional domain for the email address
    
    Returns:
        str: Generated unique email address
    """
    # Use default prefix if none provided
    if prefix is None:
        prefix = TEST_USER['EMAIL_PREFIX']
    
    # Add timestamp and random digits to ensure uniqueness
    timestamp = int(time.time())
    random_digits = random.randint(1000, 9999)
    unique_part = f"{timestamp}.{random_digits}"
    
    # Use default domain if none provided
    if domain is None:
        domain = DEFAULT_DOMAIN
    
    # Combine components to form the email address
    email = f"{prefix}.{unique_part}@{domain}"
    return email


def get_domain_attribute(domain, attribute):
    """
    Returns a specific attribute for a Mailinator domain
    
    Args:
        domain (str): Domain name
        attribute (str): Attribute name to retrieve
    
    Returns:
        any: Value of the requested attribute or None if not found
    """
    # Check if domain exists in domain_attributes
    if domain in DOMAINS.get('domain_attributes', {}):
        # Return attribute if it exists for the domain
        return DOMAINS['domain_attributes'][domain].get(attribute)
    
    return None


def is_api_accessible_domain(domain):
    """
    Checks if a domain supports API access
    
    Args:
        domain (str): Domain name to check
    
    Returns:
        bool: True if domain supports API access, False otherwise
    """
    supports_api = get_domain_attribute(domain, 'supports_api')
    return supports_api if supports_api is not None else False


def get_public_inbox_url(email_address):
    """
    Returns the public URL for accessing a Mailinator inbox in browser
    
    Args:
        email_address (str): Email address
    
    Returns:
        str: Public URL for the inbox
    """
    # Extract username and domain from email address
    parts = email_address.split('@')
    if len(parts) != 2:
        return None
    
    username, domain = parts
    
    # Check if domain is supported
    if domain in DOMAINS.get('domain_attributes', {}) and get_domain_attribute(domain, 'public_access'):
        # Format the URL using the public URL template from MAILINATOR settings
        public_url_template = MAILINATOR.get('PUBLIC_URL', 'https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox}')
        return public_url_template.replace('{inbox}', username)
    
    return None