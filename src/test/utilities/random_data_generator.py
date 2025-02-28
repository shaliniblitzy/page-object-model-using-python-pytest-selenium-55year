"""
Utility module for generating random test data for Storydoc automation tests.

This module provides functions to generate various types of random data required for
testing Storydoc features including user registration, story creation, and story sharing.
"""

import random
import string
import time
import uuid
from datetime import datetime, timedelta
from faker import Faker  # faker 8.0.0

# Internal imports
from ..config.constants import TEST_USER, TEST_DATA
from ..config.mailinator_config import DEFAULT_DOMAIN, generate_email_address

# Initialize Faker
faker = Faker()

def generate_random_string(length=10, char_set=None):
    """
    Generate a random string of specified length.
    
    Args:
        length (int): Length of the string to generate. Default is 10.
        char_set (str): Set of characters to use. Default is alphanumeric.
        
    Returns:
        str: A random string of specified length
    """
    if char_set is None:
        char_set = string.ascii_letters + string.digits
    
    return ''.join(random.choices(char_set, k=length))

def generate_random_email(prefix=None, domain=None):
    """
    Generate a random email address using mailinator.com domain.
    
    Args:
        prefix (str): Prefix for the email address. Default is None.
        domain (str): Domain for the email address. Default is None.
        
    Returns:
        str: A random email address
    """
    return generate_email_address(prefix, domain)

def generate_random_password(length=12):
    """
    Generate a random password that meets security requirements.
    
    Args:
        length (int): Length of the password to generate. Default is 12.
        
    Returns:
        str: A random password
    """
    if length < 8:
        length = 8  # Ensure minimum secure length
    
    # Ensure at least one of each character type
    password_chars = [
        random.choice(string.ascii_uppercase),  # At least one uppercase
        random.choice(string.ascii_lowercase),  # At least one lowercase
        random.choice(string.digits),           # At least one digit
        random.choice('!@#$%^&*()-_=+[]{}|;:,.<>?')  # At least one special char
    ]
    
    # Fill the rest with random characters
    remaining_length = length - len(password_chars)
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    password_chars.extend(random.choices(all_chars, k=remaining_length))
    
    # Shuffle to ensure the required characters aren't always at the beginning
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

def generate_random_name():
    """
    Generate a random full name.
    
    Returns:
        str: A random full name
    """
    return faker.name()

def generate_random_story_title():
    """
    Generate a random story title.
    
    Returns:
        str: A random story title
    """
    return f"{TEST_DATA['STORY_TITLE_PREFIX']} - {faker.catch_phrase()}"

def generate_random_story_content(paragraphs=3):
    """
    Generate random content for a story.
    
    Args:
        paragraphs (int): Number of paragraphs to generate. Default is 3.
        
    Returns:
        str: Random story content
    """
    return '\n\n'.join(faker.paragraphs(nb=paragraphs))

def generate_random_timestamp(start_date=None, end_date=None):
    """
    Generate a random timestamp within a specified range.
    
    Args:
        start_date (datetime): Start date for the range. Default is 30 days ago.
        end_date (datetime): End date for the range. Default is current date/time.
        
    Returns:
        datetime: A random timestamp
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date is None:
        end_date = datetime.now()
    
    delta_seconds = int((end_date - start_date).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    
    return start_date + timedelta(seconds=random_seconds)

def generate_test_user_data():
    """
    Generate a complete set of user data for testing.
    
    Returns:
        dict: Dictionary containing user data
    """
    return {
        'name': generate_random_name(),
        'email': generate_random_email(TEST_USER['EMAIL_PREFIX']),
        'password': generate_random_password()
    }

def generate_test_story_data():
    """
    Generate a complete set of story data for testing.
    
    Returns:
        dict: Dictionary containing story data
    """
    return {
        'title': generate_random_story_title(),
        'content': generate_random_story_content(),
        'created_at': generate_random_timestamp()
    }

def generate_test_sharing_data():
    """
    Generate data for story sharing tests.
    
    Returns:
        dict: Dictionary containing sharing data
    """
    return {
        'recipient_email': generate_random_email(TEST_DATA['RECIPIENT_EMAIL_PREFIX']),
        'message': faker.paragraph()
    }

def generate_uuid():
    """
    Generate a unique identifier.
    
    Returns:
        str: Unique identifier string
    """
    return str(uuid.uuid4())