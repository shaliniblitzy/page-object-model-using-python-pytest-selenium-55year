"""
Utility module for parsing HTML content from emails and web pages.

This module provides functions and classes for parsing HTML content, extracting links,
and getting specific data from HTML elements. Primarily used for email verification 
and extracting verification links from Mailinator emails.
"""

import re
import logging
from bs4 import BeautifulSoup  # v4.10.0
import urllib.parse

# Set up logging
logger = logging.getLogger(__name__)

def parse_html(html_content, parser_type='html.parser'):
    """
    Parse HTML content using BeautifulSoup
    
    Args:
        html_content (str): HTML content to parse
        parser_type (str): Parser type to use (default: 'html.parser')
        
    Returns:
        BeautifulSoup: BeautifulSoup object representing the parsed HTML
    """
    logger.debug(f"Parsing HTML content with parser: {parser_type}")
    return BeautifulSoup(html_content, parser_type)

def extract_links(html_content, base_url=None):
    """
    Extract all links from HTML content
    
    Args:
        html_content (str): HTML content to extract links from
        base_url (str): Base URL for resolving relative links (default: None)
        
    Returns:
        list: List of extracted URL strings
    """
    soup = parse_html(html_content)
    links = []
    
    # Find all 'a' tags in the HTML
    a_tags = soup.find_all('a')
    
    # Extract href attribute from each tag
    for tag in a_tags:
        href = tag.get('href')
        if href and href.strip():
            # Normalize URL if base_url is provided
            if base_url and not href.startswith(('http://', 'https://')):
                href = urllib.parse.urljoin(base_url, href)
            
            links.append(href.strip())
    
    logger.debug(f"Extracted {len(links)} links from HTML content")
    return links

def extract_verification_link(html_content, keywords=None, base_url=None):
    """
    Extract verification link from email HTML content
    
    Args:
        html_content (str): HTML content to extract verification link from
        keywords (list): List of keywords to identify verification links (default: None)
            If None, uses default keywords ['verify', 'confirm', 'activate', 'shared']
        base_url (str): Base URL for resolving relative links (default: None)
            
    Returns:
        str: Extracted verification link or None if not found
    """
    if keywords is None:
        keywords = ['verify', 'confirm', 'activate', 'shared']
    
    links = extract_links(html_content, base_url)
    
    # Check each link for verification keywords
    for link in links:
        for keyword in keywords:
            if keyword.lower() in link.lower():
                logger.info(f"Found verification link with keyword '{keyword}': {link}")
                return link
    
    logger.warning("No verification link found in HTML content")
    return None

def extract_element_text(html_content, element_tag, attributes=None):
    """
    Extract text from a specific HTML element
    
    Args:
        html_content (str): HTML content to extract text from
        element_tag (str): HTML tag to look for
        attributes (dict): Attributes to match (default: None)
            
    Returns:
        str: Text content of the found element or None if not found
    """
    if attributes is None:
        attributes = {}
    
    soup = parse_html(html_content)
    element = soup.find(element_tag, attributes)
    
    if element:
        logger.debug(f"Found element {element_tag} with text: {element.text.strip()}")
        return element.text.strip()
    
    logger.warning(f"Element {element_tag} with attributes {attributes} not found")
    return None

def clean_html(html_content):
    """
    Clean HTML content to get plain text
    
    Args:
        html_content (str): HTML content to clean
        
    Returns:
        str: Cleaned text without HTML tags
    """
    soup = parse_html(html_content)
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    logger.debug(f"Cleaned HTML content to: {text[:100]}...")
    return text

def find_pattern_in_html(html_content, pattern):
    """
    Find text matching a regex pattern in HTML content
    
    Args:
        html_content (str): HTML content to search in
        pattern (str): Regular expression pattern to search for
        
    Returns:
        list: List of matches found
    """
    text = clean_html(html_content)
    matches = re.findall(pattern, text)
    
    logger.debug(f"Found {len(matches)} matches for pattern '{pattern}'")
    return matches

def is_element_present(html_content, element_tag, attributes=None):
    """
    Check if an element with specified attributes exists in HTML
    
    Args:
        html_content (str): HTML content to check
        element_tag (str): HTML tag to look for
        attributes (dict): Attributes to match (default: None)
        
    Returns:
        bool: True if element exists, False otherwise
    """
    if attributes is None:
        attributes = {}
    
    soup = parse_html(html_content)
    element = soup.find(element_tag, attributes)
    
    exists = element is not None
    logger.debug(f"Element {element_tag} with attributes {attributes} exists: {exists}")
    return exists

class HTMLParser:
    """
    Class for parsing HTML content and extracting information
    """
    
    def __init__(self):
        """
        Initialize the HTMLParser
        """
        self.logger = logging.getLogger(__name__)
    
    def parse(self, html_content, parser_type='html.parser'):
        """
        Parse HTML content
        
        Args:
            html_content (str): HTML content to parse
            parser_type (str): Parser type to use (default: 'html.parser')
            
        Returns:
            BeautifulSoup: Parsed HTML object
        """
        self.logger.debug(f"Parsing HTML content with parser: {parser_type}")
        return BeautifulSoup(html_content, parser_type)
    
    def extract_links(self, html_content, base_url=None):
        """
        Extract all links from HTML content
        
        Args:
            html_content (str): HTML content to extract links from
            base_url (str): Base URL for resolving relative links (default: None)
            
        Returns:
            list: List of extracted URL strings
        """
        soup = self.parse(html_content)
        links = []
        
        # Find all 'a' tags in the HTML
        a_tags = soup.find_all('a')
        
        # Extract href attribute from each tag
        for tag in a_tags:
            href = tag.get('href')
            if href and href.strip():
                # Normalize URL if base_url is provided
                if base_url and not href.startswith(('http://', 'https://')):
                    href = urllib.parse.urljoin(base_url, href)
                
                links.append(href.strip())
        
        self.logger.debug(f"Extracted {len(links)} links from HTML content")
        return links
    
    def extract_verification_link(self, html_content, keywords=None, base_url=None):
        """
        Extract verification link from email HTML content
        
        Args:
            html_content (str): HTML content to extract verification link from
            keywords (list): List of keywords to identify verification links (default: None)
                If None, uses default keywords ['verify', 'confirm', 'activate', 'shared']
            base_url (str): Base URL for resolving relative links (default: None)
                
        Returns:
            str: Extracted verification link or None if not found
        """
        if keywords is None:
            keywords = ['verify', 'confirm', 'activate', 'shared']
        
        links = self.extract_links(html_content, base_url)
        
        # Check each link for verification keywords
        for link in links:
            for keyword in keywords:
                if keyword.lower() in link.lower():
                    self.logger.info(f"Found verification link with keyword '{keyword}': {link}")
                    return link
        
        self.logger.warning("No verification link found in HTML content")
        return None
    
    def extract_element_text(self, html_content, element_tag, attributes=None):
        """
        Extract text from a specific HTML element
        
        Args:
            html_content (str): HTML content to extract text from
            element_tag (str): HTML tag to look for
            attributes (dict): Attributes to match (default: None)
                
        Returns:
            str: Text content of the found element or None if not found
        """
        if attributes is None:
            attributes = {}
        
        soup = self.parse(html_content)
        element = soup.find(element_tag, attributes)
        
        if element:
            self.logger.debug(f"Found element {element_tag} with text: {element.text.strip()}")
            return element.text.strip()
        
        self.logger.warning(f"Element {element_tag} with attributes {attributes} not found")
        return None
    
    def clean_html(self, html_content):
        """
        Clean HTML content to get plain text
        
        Args:
            html_content (str): HTML content to clean
            
        Returns:
            str: Cleaned text without HTML tags
        """
        soup = self.parse(html_content)
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        self.logger.debug(f"Cleaned HTML content to: {text[:100]}...")
        return text
    
    def find_pattern(self, html_content, pattern):
        """
        Find text matching a regex pattern in HTML content
        
        Args:
            html_content (str): HTML content to search in
            pattern (str): Regular expression pattern to search for
            
        Returns:
            list: List of matches found
        """
        text = self.clean_html(html_content)
        matches = re.findall(pattern, text)
        
        self.logger.debug(f"Found {len(matches)} matches for pattern '{pattern}'")
        return matches