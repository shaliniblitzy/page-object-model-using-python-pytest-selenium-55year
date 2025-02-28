"""
Client module for interacting with the Mailinator API to retrieve and process emails
for email verification in the Storydoc automation framework.

This module provides a client class for checking inboxes, retrieving messages,
waiting for emails, and extracting verification links required for testing user
registration and story sharing workflows.
"""

import re
import os
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus

# Import retry decorator for handling API rate limiting
from .retry_helper import retry

# Import logging utilities
from .logger import log_info, log_debug, log_warning, log_error

# Import Mailinator configuration
from ..config.mailinator_config import (
    DEFAULT_DOMAIN,
    MAILINATOR_BASE_URL,
    MAILINATOR_API_KEY,
    MAILINATOR_TIMEOUT,
    MAILINATOR_POLLING_INTERVAL,
    RETRY_CONFIG,
    EMAIL_SUBJECT_CONFIG,
    MAILINATOR_VERIFY_SSL,
    get_headers,
    is_api_accessible_domain
)

# Keywords for identifying verification links in emails
VERIFICATION_KEYWORDS = ['verify', 'confirm', 'activate', 'verification']

# Keywords for identifying sharing links in emails
SHARING_KEYWORDS = ['shared', 'share', 'access', 'view']

# Module logger
logger = logging.getLogger(__name__)


class MailinatorAPI:
    """A client class for interacting with the Mailinator API to retrieve and process emails."""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        default_timeout: int = None,
        polling_interval: int = None,
        retry_config: Dict = None,
        verify_ssl: bool = None
    ):
        """Initialize the MailinatorAPI client with configuration settings.
        
        Args:
            api_key: API key for Mailinator authentication, defaults to MAILINATOR_API_KEY
            base_url: Base URL for Mailinator API, defaults to MAILINATOR_BASE_URL
            default_timeout: Default timeout for API operations in seconds, defaults to MAILINATOR_TIMEOUT
            polling_interval: Interval between API polling in seconds, defaults to MAILINATOR_POLLING_INTERVAL
            retry_config: Configuration for retry mechanism, defaults to RETRY_CONFIG
            verify_ssl: Whether to verify SSL certificates, defaults to MAILINATOR_VERIFY_SSL
        """
        # Initialize base URL from parameter or config
        self.base_url = base_url or MAILINATOR_BASE_URL
        
        # Initialize API key from parameter or config
        self.api_key = api_key or MAILINATOR_API_KEY
        
        # Get headers for API requests
        self.headers = get_headers()
        
        # Initialize timeout values
        self.default_timeout = default_timeout or MAILINATOR_TIMEOUT
        self.polling_interval = polling_interval or MAILINATOR_POLLING_INTERVAL
        
        # Initialize retry configuration
        self.retry_config = retry_config or RETRY_CONFIG
        
        # Initialize SSL verification setting
        self.verify_ssl = verify_ssl if verify_ssl is not None else MAILINATOR_VERIFY_SSL
        
        # Log initialization
        log_info(f"Initialized MailinatorAPI with base_url={self.base_url}, " 
                 f"timeout={self.default_timeout}s, polling_interval={self.polling_interval}s")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        additional_headers: Dict = None
    ) -> requests.Response:
        """Make a request to the Mailinator API with retry mechanism.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters for the request
            additional_headers: Additional headers to include with the request
            
        Returns:
            requests.Response: API response
        """
        # Combine base headers with any additional headers
        headers = {**self.headers}
        if additional_headers:
            headers.update(additional_headers)
        
        # Build the complete URL
        url = f"{self.base_url}{endpoint}"
        
        # Log API request
        log_debug(f"Making {method} request to {url}")
        
        # Define the retry-decorated request function
        @retry(
            max_attempts=self.retry_config.get('max_attempts', 3),
            delay=self.retry_config.get('delay', 2),
            backoff_factor=self.retry_config.get('backoff_factor', 1.5),
            exceptions=(requests.RequestException,),
            add_jitter=True
        )
        def request_with_retry():
            return requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                verify=self.verify_ssl
            )
        
        try:
            # Make the request with retry mechanism
            response = request_with_retry()
            
            # Log success
            log_debug(f"API request successful: {response.status_code}")
            
            return response
        except Exception as e:
            # Log error
            log_error(f"API request failed: {str(e)}")
            # Re-raise the exception
            raise
    
    def get_inbox(self, email_address: str) -> Dict:
        """Get the inbox for a specific email address.
        
        Args:
            email_address: Email address to check
            
        Returns:
            Dict: The inbox data containing messages.
        """
        # Split email address into username and domain
        parts = email_address.split('@')
        if len(parts) != 2:
            log_warning(f"Invalid email address format: {email_address}")
            return {"msgs": []}
        
        username, domain = parts
        
        # Check if domain supports API access
        if not is_api_accessible_domain(domain):
            log_warning(f"Domain {domain} does not support API access")
            return {"msgs": []}
        
        # Construct the endpoint
        endpoint = f"/domains/{domain}/inboxes/{username}"
        
        try:
            # Make the API request
            response = self._make_request("GET", endpoint)
            
            # Check if the request was successful
            if response.status_code == 200:
                inbox_data = response.json()
                log_info(f"Retrieved inbox for {email_address} with {len(inbox_data.get('msgs', []))} messages")
                return inbox_data
            else:
                log_warning(f"Failed to get inbox for {email_address}: {response.status_code}")
                return {"msgs": []}
        except Exception as e:
            log_error(f"Error retrieving inbox for {email_address}: {str(e)}")
            return {"msgs": []}
    
    def get_message(self, message_id: str, domain: str = None) -> Dict:
        """Get a specific message by its ID.
        
        Args:
            message_id: ID of the message to retrieve
            domain: Domain of the mailinator inbox, defaults to DEFAULT_DOMAIN
            
        Returns:
            Dict: The detailed message data.
        """
        # Use default domain if not provided
        if domain is None:
            domain = DEFAULT_DOMAIN
        
        # Check if domain supports API access
        if not is_api_accessible_domain(domain):
            log_warning(f"Domain {domain} does not support API access")
            return {}
        
        # Construct the endpoint
        endpoint = f"/message/{message_id}"
        
        try:
            # Make the API request
            response = self._make_request("GET", endpoint)
            
            # Check if the request was successful
            if response.status_code == 200:
                message_data = response.json()
                log_info(f"Retrieved message {message_id}")
                return message_data
            else:
                log_warning(f"Failed to get message {message_id}: {response.status_code}")
                return {}
        except Exception as e:
            log_error(f"Error retrieving message {message_id}: {str(e)}")
            return {}
    
    def wait_for_email(
        self, 
        email_address: str, 
        subject: str, 
        timeout: int = None, 
        polling_interval: int = None
    ) -> Optional[Dict]:
        """Wait for an email with a specific subject to arrive in the inbox.
        
        Args:
            email_address: Email address to check
            subject: Subject of the email to look for (case-insensitive partial match)
            timeout: Maximum time to wait in seconds, defaults to self.default_timeout
            polling_interval: Time between inbox checks in seconds, defaults to self.polling_interval
            
        Returns:
            Dict: The message data if found, or None if timeout occurs.
        """
        log_info(f"Waiting for email with subject '{subject}' for {email_address}")
        
        # Set default timeout and polling interval if not provided
        if timeout is None:
            timeout = self.default_timeout
        
        if polling_interval is None:
            polling_interval = self.polling_interval
        
        # Split email address into username and domain
        parts = email_address.split('@')
        if len(parts) != 2:
            log_warning(f"Invalid email address format: {email_address}")
            return None
        
        username, domain = parts
        
        # Check if domain supports API access
        if not is_api_accessible_domain(domain):
            log_warning(f"Domain {domain} does not support API access")
            return None
        
        # Record start time
        start_time = time.time()
        
        # Loop until timeout
        while time.time() - start_time < timeout:
            # Get inbox data
            inbox = self.get_inbox(email_address)
            
            # Check each message for matching subject
            for message in inbox.get("msgs", []):
                message_subject = message.get("subject", "").lower()
                if subject.lower() in message_subject:
                    # If found, get full message details
                    message_id = message.get("id")
                    if message_id:
                        full_message = self.get_message(message_id, domain)
                        log_info(f"Found email with subject '{subject}'")
                        return full_message
            
            # If not found, wait and try again
            log_debug(f"Email not found, waiting {polling_interval} seconds...")
            time.sleep(polling_interval)
        
        # If timeout reached without finding the email
        log_warning(f"Timeout waiting for email with subject '{subject}' for {email_address}")
        return None
    
    def extract_message_content(self, message: Dict) -> str:
        """Extract HTML content from a message.
        
        Args:
            message: Message data
            
        Returns:
            str: HTML content of the message or empty string if not found.
        """
        if not message:
            return ""
        
        # Get message parts
        parts = message.get("parts", [])
        
        # First, look for HTML content
        for part in parts:
            headers = part.get("headers", {})
            content_type = headers.get("content-type", "")
            if "text/html" in content_type:
                return part.get("body", "")
        
        # If no HTML content, try to get plain text content
        for part in parts:
            headers = part.get("headers", {})
            content_type = headers.get("content-type", "")
            if "text/plain" in content_type:
                return part.get("body", "")
        
        # If no content found
        log_warning("No HTML or text content found in message")
        return ""
    
    def extract_verification_link(self, content: str, keywords: List[str] = None) -> Optional[str]:
        """Extract a verification link from the message content using regex and keywords.
        
        Args:
            content: HTML or text content of the message
            keywords: List of keywords to identify verification links, defaults to VERIFICATION_KEYWORDS
            
        Returns:
            str: The extracted verification link or None if not found.
        """
        if not content:
            return None
        
        # Use default keywords if not provided
        if keywords is None:
            keywords = VERIFICATION_KEYWORDS
        
        # Find all URLs in the content
        urls = re.findall(r'https?://[^\s<>"\']+', content)
        
        # Filter URLs by keywords
        for url in urls:
            # Check if any keyword appears in the URL
            if any(keyword.lower() in url.lower() for keyword in keywords):
                log_debug(f"Found verification link: {url}")
                return url
        
        # If no verification link found
        log_warning("No verification link found in email content")
        return None
    
    def get_verification_link(self, message: Dict) -> Optional[str]:
        """Get verification link from a message.
        
        Args:
            message: Message data
            
        Returns:
            str: Verification link or None if not found.
        """
        if not message:
            return None
        
        # Extract HTML content
        content = self.extract_message_content(message)
        
        # Extract verification link
        return self.extract_verification_link(content, VERIFICATION_KEYWORDS)
    
    def get_sharing_link(self, message: Dict) -> Optional[str]:
        """Get sharing link from a message.
        
        Args:
            message: Message data
            
        Returns:
            str: Sharing link or None if not found.
        """
        if not message:
            return None
        
        # Extract HTML content
        content = self.extract_message_content(message)
        
        # Extract sharing link using sharing keywords
        return self.extract_verification_link(content, SHARING_KEYWORDS)
    
    def verify_email_received(
        self, 
        email_address: str, 
        subject: str, 
        timeout: int = None
    ) -> bool:
        """Verify that an email with a specific subject was received.
        
        Args:
            email_address: Email address to check
            subject: Subject of the email to look for
            timeout: Maximum time to wait in seconds, defaults to self.default_timeout
            
        Returns:
            bool: True if the email was received, False otherwise.
        """
        # Wait for email and return True if received, False otherwise
        message = self.wait_for_email(email_address, subject, timeout)
        return message is not None
    
    def get_registration_verification_link(
        self, 
        email_address: str, 
        timeout: int = None
    ) -> Optional[str]:
        """Wait for registration verification email and extract link.
        
        Args:
            email_address: Email address to check
            timeout: Maximum time to wait in seconds, defaults to self.default_timeout
            
        Returns:
            str: Verification link or None if not found.
        """
        # Get registration email subject from configuration
        subject = EMAIL_SUBJECT_CONFIG.get('registration', 'Welcome to Storydoc')
        
        # Wait for the email
        message = self.wait_for_email(email_address, subject, timeout)
        
        # If email received, extract verification link
        if message:
            return self.get_verification_link(message)
        
        return None
    
    def get_sharing_verification_link(
        self, 
        email_address: str, 
        timeout: int = None
    ) -> Optional[str]:
        """Wait for sharing email and extract link.
        
        Args:
            email_address: Email address to check
            timeout: Maximum time to wait in seconds, defaults to self.default_timeout
            
        Returns:
            str: Sharing link or None if not found.
        """
        # Get sharing email subject from configuration
        subject = EMAIL_SUBJECT_CONFIG.get('sharing', 'Story shared with you')
        
        # Wait for the email
        message = self.wait_for_email(email_address, subject, timeout)
        
        # If email received, extract sharing link
        if message:
            return self.get_sharing_link(message)
        
        return None
    
    def generate_email_address(self, prefix: str = None, domain: str = None) -> str:
        """Generate a unique email address for testing.
        
        Args:
            prefix: Prefix for the email address, defaults to configured default
            domain: Domain for the email address, defaults to DEFAULT_DOMAIN
            
        Returns:
            str: Generated email address.
        """
        # Import here to avoid circular imports
        from ..config.mailinator_config import generate_email_address as gen_email
        
        # Generate email address using the imported function
        return gen_email(prefix, domain)