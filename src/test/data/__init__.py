"""
Initialization file for the data package of the Storydoc test automation framework.

It exports functions for loading test data from JSON files and accessing test data generators.
This package serves as a central point for all test data management needs.
"""

import json
import os
import pathlib
from pathlib import Path

# Internal imports
from ..utilities.config_manager import ConfigManager
from ..utilities.logger import log_info
from ..utilities.random_data_generator import (
    generate_random_email,
    generate_random_password,
    generate_random_name,
    generate_random_story_title,
    generate_test_user_data,
    generate_test_story_data
)

# Global variables
DATA_DIR = str(pathlib.Path(__file__).parent)
config_manager = ConfigManager()

def load_json_data(file_name):
    """
    Load data from a JSON file in the data directory
    
    Args:
        file_name: Name of the JSON file
        
    Returns:
        dict: Parsed JSON data as a dictionary
    """
    try:
        # Construct the file path using DATA_DIR and file_name
        file_path = os.path.join(DATA_DIR, file_name)
        
        # Open the file and read its contents
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Log info message about successful data loading
        log_info(f"Successfully loaded data from {file_name}")
        
        return data
    except FileNotFoundError:
        log_info(f"File not found: {file_name}")
        return {}
    except json.JSONDecodeError:
        log_info(f"Invalid JSON format in file: {file_name}")
        return {}

def load_test_data():
    """
    Load the main test data file (test_data.json)
    
    Returns:
        dict: Complete test data dictionary
    """
    return load_json_data('test_data.json')

def load_user_data():
    """
    Load user-specific test data (user_data.json)
    
    Returns:
        dict: User test data dictionary
    """
    return load_json_data('user_data.json')

def load_story_data():
    """
    Load story-specific test data (story_data.json)
    
    Returns:
        dict: Story test data dictionary
    """
    return load_json_data('story_data.json')

def load_template_data():
    """
    Load template-specific test data (template_data.json)
    
    Returns:
        dict: Template test data dictionary
    """
    return load_json_data('template_data.json')

def load_mailinator_domains():
    """
    Load mailinator domains for email testing (mailinator_domains.json)
    
    Returns:
        list: List of mailinator domains
    """
    data = load_json_data('mailinator_domains.json')
    # Extract and return the domains list from the loaded data
    return data.get('domains', ['mailinator.com'])

def generate_user(email_domain=None, password=None):
    """
    Generate a random user for testing
    
    Args:
        email_domain: Optional domain for the email address
        password: Optional password for the user
        
    Returns:
        dict: Generated user data dictionary
    """
    # Get a base user data dictionary
    user_data = generate_test_user_data()
    
    # If email_domain is provided, replace the domain in the email
    if email_domain:
        email_parts = user_data['email'].split('@')
        user_data['email'] = f"{email_parts[0]}@{email_domain}"
    
    # If password is provided, replace the password
    if password:
        user_data['password'] = password
    
    return user_data

def generate_story():
    """
    Generate a random story for testing
    
    Returns:
        dict: Generated story data dictionary
    """
    return generate_test_story_data()

# Re-export random data generator functions for convenience
get_random_email = generate_random_email
get_random_password = generate_random_password
get_random_name = generate_random_name
get_random_story_title = generate_random_story_title