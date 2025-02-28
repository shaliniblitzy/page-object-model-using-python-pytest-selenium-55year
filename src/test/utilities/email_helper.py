import requests  # version 2.31+
import time
import re
import logging
import os
from dotenv import load_dotenv  # version 1.0+

class EmailHelper:
    """Helper class for interacting with Mailinator API to verify emails during testing"""
    
    def __init__(self):
        """Initialize the EmailHelper with Mailinator API configuration"""
        # Load environment variables
        load_dotenv()
        
        # Set the base URL for the Mailinator API
        self.base_url = "https://api.mailinator.com/api/v2"
        
        # Get the API key from environment variables if available
        self.api_key = os.getenv("MAILINATOR_API_KEY")
        
        # Initialize logger for email verification activities
        self.logger = logging.getLogger(__name__)
    
    def generate_email_address(self, prefix=None):
        """
        Generate a unique email address using mailinator.com domain
        
        Args:
            prefix (str, optional): Email prefix. If None, a timestamp will be used
            
        Returns:
            str: Generated email address in the format prefix@mailinator.com
        """
        if prefix is None:
            # Generate a unique prefix using timestamp
            prefix = f"test.user.{int(time.time())}"
        
        # Get the mailinator domain from environment variables
        domain = os.getenv("TEST_EMAIL_DOMAIN", "mailinator.com")
        
        # Return the email address
        return f"{prefix}@{domain}"
    
    def get_inbox(self, email_address):
        """
        Get the inbox for a specified email address via Mailinator API
        
        Args:
            email_address (str): Email address to check
            
        Returns:
            dict: Inbox data including messages
        """
        # Extract username from email address (part before @)
        username = email_address.split('@')[0]
        
        # Construct the API URL for retrieving the inbox
        url = f"{self.base_url}/domains/mailinator.com/inboxes/{username}"
        
        # Prepare headers with API key if available
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Log the API request
        self.logger.info(f"Checking inbox for: {email_address}")
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            else:
                # Log error and return empty inbox
                self.logger.error(f"Failed to get inbox: {response.status_code} - {response.text}")
                return {"msgs": []}
        except Exception as e:
            # Log any exceptions and return empty inbox
            self.logger.error(f"Exception while getting inbox: {str(e)}")
            return {"msgs": []}
    
    def get_message(self, message_id):
        """
        Get a specific message by ID from Mailinator API
        
        Args:
            message_id (str): ID of the message to retrieve
            
        Returns:
            dict: Message data including content and parts
        """
        # Construct the API URL for retrieving the message
        url = f"{self.base_url}/message/{message_id}"
        
        # Prepare headers with API key if available
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Log the API request
        self.logger.info(f"Getting message: {message_id}")
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            else:
                # Log error and return empty message
                self.logger.error(f"Failed to get message: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            # Log any exceptions and return empty message
            self.logger.error(f"Exception while getting message: {str(e)}")
            return {}
    
    def wait_for_email(self, email_address, subject, timeout=60, polling_interval=5):
        """
        Wait for an email with the specified subject to arrive in the inbox
        
        Args:
            email_address (str): Email address to check
            subject (str): Subject of the email to wait for
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 60.
            polling_interval (int, optional): Time between checks in seconds. Defaults to 5.
            
        Returns:
            dict: Message data or None if not found within timeout
        """
        # Log that we're waiting for an email
        self.logger.info(f"Waiting for email with subject '{subject}' for {email_address}")
        
        # Record the start time
        start_time = time.time()
        
        # Continue checking until timeout is reached
        while time.time() - start_time < timeout:
            # Get the inbox for the email address
            inbox = self.get_inbox(email_address)
            
            # Check if any message has the specified subject
            for message in inbox.get("msgs", []):
                if subject.lower() in message.get("subject", "").lower():
                    # Log that we found the email
                    self.logger.info(f"Found email with subject: {subject}")
                    # Get and return the full message
                    return self.get_message(message.get("id"))
            
            # If no matching email found, wait before checking again
            self.logger.debug(f"Email not found, waiting {polling_interval} seconds...")
            time.sleep(polling_interval)
        
        # If timeout reached, log warning and return None
        self.logger.warning(f"Timeout waiting for email with subject: {subject}")
        return None
    
    def extract_verification_link(self, message):
        """
        Extract verification or sharing link from an email message
        
        Args:
            message (dict): Message data
            
        Returns:
            str or None: Verification link or None if not found
        """
        # Check if message is valid
        if not message:
            return None
        
        # Extract parts from the message
        parts = message.get("parts", [])
        for part in parts:
            # Check if the part is HTML content
            if part.get("headers", {}).get("content-type", "").startswith("text/html"):
                # Get the body content
                content = part.get("body", "")
                
                # Use regex to find all URLs in the content
                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
                
                # Filter for verification-related URLs
                for url in urls:
                    if "verify" in url or "confirm" in url or "activate" in url or "shared" in url:
                        # Log the found verification link
                        self.logger.info(f"Found verification link: {url}")
                        return url
        
        # If no verification link found, log warning and return None
        self.logger.warning("No verification link found in email")
        return None
    
    def verify_email_received(self, email_address, subject, timeout=60):
        """
        Verify that an email with the specified subject was received
        
        Args:
            email_address (str): Email address to check
            subject (str): Subject of the email to verify
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 60.
            
        Returns:
            bool: True if email was received, False otherwise
        """
        # Wait for the email and check if it was received
        message = self.wait_for_email(email_address, subject, timeout)
        return message is not None