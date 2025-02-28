"""
Utility module for generating test data for the Storydoc automation framework.

This module provides functions to generate data for user registration, authentication,
story creation, and story sharing tests. It offers both standalone functions and a class-based
interface for generating consistent test data for automation tests.
"""

import json
import os
import time
import random
import string

# Internal imports
from ..utilities.random_data_generator import generate_random_string, generate_random_email
from ..config.config import get_config
from ..config.constants import TEST_USER, TEST_DATA, SLA, MAILINATOR
from ..utilities.logger import get_logger


def generate_user_data(email_domain=None, password=None):
    """
    Generate user data for registration and authentication tests
    
    Args:
        email_domain (str): Domain to use for email generation
        password (str): Password to use (if None, a secure password will be generated)
        
    Returns:
        dict: Dictionary containing user data including email, password, and name
    """
    logger = get_logger()
    logger.debug("Generating user data")
    
    # Generate email with specified domain or use default
    if email_domain is None:
        email_domain = get_config("mailinator_domain", "mailinator.com")
    
    email = generate_random_email(TEST_USER["EMAIL_PREFIX"], email_domain)
    
    # Use specified password or default
    if password is None:
        password = TEST_USER["PASSWORD"]
    
    # Generate a random name with test prefix
    name = f"{TEST_USER['NAME']} {int(time.time())}"
    
    user_data = {
        "email": email,
        "password": password,
        "name": name
    }
    
    logger.debug(f"Generated user data: {user_data}")
    return user_data


def generate_story_data(template_name=None):
    """
    Generate story data for story creation tests
    
    Args:
        template_name (str): Template name to use for the story
        
    Returns:
        dict: Dictionary containing story data including title and template
    """
    logger = get_logger()
    logger.debug("Generating story data")
    
    # Generate unique story title with timestamp
    story_title = f"{TEST_DATA['STORY_TITLE_PREFIX']} {int(time.time())}"
    
    # Use specified template or default
    if template_name is None:
        template_name = TEST_DATA["TEMPLATE_NAME"]
    
    story_data = {
        "title": story_title,
        "template": template_name
    }
    
    logger.debug(f"Generated story data: {story_data}")
    return story_data


def generate_sharing_data(num_recipients=1, email_domain=None):
    """
    Generate sharing data for story sharing tests
    
    Args:
        num_recipients (int): Number of recipient email addresses to generate
        email_domain (str): Domain to use for email generation
        
    Returns:
        dict: Dictionary containing sharing data including recipient emails and message
    """
    logger = get_logger()
    logger.debug(f"Generating sharing data for {num_recipients} recipients")
    
    # Use specified domain or default
    if email_domain is None:
        email_domain = get_config("mailinator_domain", "mailinator.com")
    
    # Generate recipient emails
    recipient_emails = []
    for i in range(num_recipients):
        recipient_email = generate_random_email(f"{TEST_DATA['RECIPIENT_EMAIL_PREFIX']}{i+1}", email_domain)
        recipient_emails.append(recipient_email)
    
    # Generate a random message
    message = f"Sharing test message generated at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    sharing_data = {
        "recipient_emails": recipient_emails,
        "message": message
    }
    
    logger.debug(f"Generated sharing data: {sharing_data}")
    return sharing_data


def load_test_data_template(template_file):
    """
    Load test data template from a JSON file
    
    Args:
        template_file (str): Name of the template file to load
        
    Returns:
        dict: Dictionary containing the loaded test data template
    """
    logger = get_logger()
    logger.debug(f"Loading test data template: {template_file}")
    
    # Get data directory from config
    data_dir = get_config("data_dir", os.path.join("src", "test", "data"))
    
    # Ensure template_file has .json extension
    if not template_file.endswith(".json"):
        template_file = f"{template_file}.json"
    
    # Construct full path to template file
    template_path = os.path.join(data_dir, template_file)
    
    try:
        with open(template_path, "r") as file:
            template_data = json.load(file)
            logger.debug(f"Loaded test data template: {template_file}")
            return template_data
    except FileNotFoundError:
        logger.error(f"Test data template not found: {template_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing test data template {template_path}: {str(e)}")
        return {}


def generate_unique_email(prefix=None, domain=None):
    """
    Generate a unique email address using a mailinator domain
    
    Args:
        prefix (str): Prefix for the email address
        domain (str): Domain for the email address
        
    Returns:
        str: Unique email address
    """
    # Use specified prefix or generate random one
    if prefix is None:
        prefix = f"test.user.{generate_random_string(5)}"
    
    # Add timestamp to ensure uniqueness
    timestamp = str(int(time.time()))
    
    # Use specified domain or default
    if domain is None:
        domain = get_config("mailinator_domain", "mailinator.com")
    
    # Construct email address
    email = f"{prefix}.{timestamp}@{domain}"
    
    return email


def generate_secure_password(length=12):
    """
    Generate a secure password for testing
    
    Args:
        length (int): Length of the password
        
    Returns:
        str: Generated secure password
    """
    # Ensure minimum length
    if length < 8:
        length = 8
    
    # Ensure we have at least one of each character type
    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+")
    
    # Generate remaining characters
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    remaining_chars = ''.join(random.choice(all_chars) for _ in range(remaining_length))
    
    # Combine and shuffle
    password = lowercase + uppercase + digit + special + remaining_chars
    password_list = list(password)
    random.shuffle(password_list)
    
    return ''.join(password_list)


def generate_test_data_set():
    """
    Generate a complete set of test data for an end-to-end test
    
    Returns:
        dict: Dictionary containing all necessary test data for an end-to-end test
    """
    logger = get_logger()
    logger.info("Generating complete test data set")
    
    # Generate all required test data
    user_data = generate_user_data()
    story_data = generate_story_data()
    sharing_data = generate_sharing_data()
    
    # Combine into a single data set
    test_data = {
        "user": user_data,
        "story": story_data,
        "sharing": sharing_data,
        "timeouts": {
            "registration": SLA["USER_REGISTRATION"],
            "authentication": SLA["USER_AUTHENTICATION"],
            "story_creation": SLA["STORY_CREATION"],
            "story_sharing": SLA["STORY_SHARING"]
        }
    }
    
    logger.debug(f"Generated complete test data set: {test_data}")
    return test_data


class TestDataGenerator:
    """
    Class for generating test data for the Storydoc automation framework
    
    This class provides methods for generating various types of test data needed for
    testing the Storydoc application, including user data, story data, and sharing data.
    """
    
    def __init__(self):
        """Initialize the TestDataGenerator with configuration"""
        # Load configuration
        self._config = {
            "mailinator_domain": get_config("mailinator_domain", "mailinator.com"),
            "data_dir": get_config("data_dir", os.path.join("src", "test", "data")),
            "default_password": TEST_USER["PASSWORD"]
        }
        
        # Initialize logger
        self._logger = get_logger()
        self._logger.debug("TestDataGenerator initialized")
    
    def generate_user(self, email_domain=None, password=None):
        """
        Generate a user for testing
        
        Args:
            email_domain (str): Domain to use for email generation
            password (str): Password to use
            
        Returns:
            dict: User data dictionary
        """
        # Use instance config if parameters not provided
        if email_domain is None:
            email_domain = self._config["mailinator_domain"]
        
        if password is None:
            password = self._config["default_password"]
        
        # Generate user data using the function
        user_data = generate_user_data(email_domain, password)
        
        self._logger.debug(f"Generated user: {user_data}")
        return user_data
    
    def generate_story(self, template_name=None):
        """
        Generate a story for testing
        
        Args:
            template_name (str): Template name to use for the story
            
        Returns:
            dict: Story data dictionary
        """
        # Generate story data using the function
        story_data = generate_story_data(template_name)
        
        self._logger.debug(f"Generated story: {story_data}")
        return story_data
    
    def generate_sharing(self, num_recipients=1, email_domain=None):
        """
        Generate sharing data for testing
        
        Args:
            num_recipients (int): Number of recipient email addresses to generate
            email_domain (str): Domain to use for email generation
            
        Returns:
            dict: Sharing data dictionary
        """
        # Use instance config if parameter not provided
        if email_domain is None:
            email_domain = self._config["mailinator_domain"]
        
        # Generate sharing data using the function
        sharing_data = generate_sharing_data(num_recipients, email_domain)
        
        self._logger.debug(f"Generated sharing data: {sharing_data}")
        return sharing_data
    
    def load_template(self, template_type):
        """
        Load a test data template
        
        Args:
            template_type (str): Type of template to load (user, story, sharing)
            
        Returns:
            dict: Template data dictionary
        """
        # Determine template file name based on type
        template_file = f"{template_type}_template.json"
        
        # Load template using the function
        template_data = load_test_data_template(template_file)
        
        self._logger.debug(f"Loaded template '{template_type}': {template_data}")
        return template_data
    
    def generate_complete_test_data(self):
        """
        Generate a complete set of test data for an end-to-end test
        
        Returns:
            dict: Complete test data dictionary
        """
        self._logger.info("Generating complete test data set")
        
        # Generate all data using class methods
        user_data = self.generate_user()
        story_data = self.generate_story()
        sharing_data = self.generate_sharing()
        
        # Combine into a single data set
        test_data = {
            "user": user_data,
            "story": story_data,
            "sharing": sharing_data,
            "timeouts": {
                "registration": SLA["USER_REGISTRATION"],
                "authentication": SLA["USER_AUTHENTICATION"],
                "story_creation": SLA["STORY_CREATION"],
                "story_sharing": SLA["STORY_SHARING"]
            }
        }
        
        self._logger.debug(f"Generated complete test data set: {test_data}")
        return test_data