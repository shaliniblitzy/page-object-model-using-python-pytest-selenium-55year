import os  # standard library

# Base URLs
BASE_URL = "https://editor-staging.storydoc.com"

# Storydoc application paths
SIGNUP_PATH = "/sign-up"
SIGNIN_PATH = "/sign-in"
DASHBOARD_PATH = "/dashboard"
STORY_EDITOR_PATH = "/editor"
STORY_PATH = "/story/{id}"
SHARE_STORY_PATH = "/share-story"
SHARED_STORY_PATH = "/shared/{token}"
VERIFY_PATH = "/verify"

# Mailinator URLs
MAILINATOR_BASE_URL = "https://www.mailinator.com"
MAILINATOR_INBOX_PATH = "/v3/inbox.jsp?zone=public&query={email}"
MAILINATOR_API_URL = "https://api.mailinator.com/api/v2"


def get_base_url():
    """
    Returns the base URL for the current environment

    Returns:
        str: Base URL for the current environment
    """
    # Get environment setting from environment variable or default to staging
    env = os.environ.get("TEST_ENVIRONMENT", "staging")
    
    # Return the appropriate base URL based on the environment
    if env == "staging":
        return BASE_URL
    elif env == "dev":
        return "https://editor-dev.storydoc.com"
    elif env == "prod":
        return "https://editor.storydoc.com"
    else:
        return BASE_URL


def get_full_url(path):
    """
    Returns a full URL by combining the base URL and the specified path

    Args:
        path (str): The path to append to the base URL

    Returns:
        str: Full URL with base URL and path
    """
    # Get base URL using get_base_url()
    base_url = get_base_url()
    
    # Combine base URL and path
    # Ensure there's no double slash between base and path
    if base_url.endswith('/') and path.startswith('/'):
        full_url = base_url + path[1:]
    else:
        full_url = base_url + path
    
    # Return the full URL
    return full_url


def get_signup_url():
    """
    Returns the full URL for the signup page

    Returns:
        str: Full URL for the signup page
    """
    return get_full_url(SIGNUP_PATH)


def get_signin_url():
    """
    Returns the full URL for the signin page

    Returns:
        str: Full URL for the signin page
    """
    return get_full_url(SIGNIN_PATH)


def get_dashboard_url():
    """
    Returns the full URL for the dashboard page

    Returns:
        str: Full URL for the dashboard page
    """
    return get_full_url(DASHBOARD_PATH)


def get_story_editor_url():
    """
    Returns the full URL for the story editor page

    Returns:
        str: Full URL for the story editor page
    """
    return get_full_url(STORY_EDITOR_PATH)


def get_story_url(story_id):
    """
    Returns the full URL for a specific story

    Args:
        story_id (str): The ID of the story

    Returns:
        str: Full URL for the specific story
    """
    # Replace {id} in STORY_PATH with story_id
    formatted_path = STORY_PATH.replace("{id}", str(story_id))
    
    # Return get_full_url(formatted_path)
    return get_full_url(formatted_path)


def get_shared_story_url(token):
    """
    Returns the full URL for a shared story

    Args:
        token (str): The sharing token

    Returns:
        str: Full URL for the shared story
    """
    # Replace {token} in SHARED_STORY_PATH with token
    formatted_path = SHARED_STORY_PATH.replace("{token}", str(token))
    
    # Return get_full_url(formatted_path)
    return get_full_url(formatted_path)


def get_verification_url(token):
    """
    Returns the full URL for email verification

    Args:
        token (str): The verification token

    Returns:
        str: Full URL for email verification
    """
    return get_full_url(f"{VERIFY_PATH}?token={token}")


def get_mailinator_inbox_url(email):
    """
    Returns the URL for a Mailinator inbox for a specific email

    Args:
        email (str): The email address to check

    Returns:
        str: URL for the Mailinator inbox
    """
    # Extract username from email address
    username = email.split('@')[0]
    
    # Replace {email} in MAILINATOR_INBOX_PATH with username
    formatted_path = MAILINATOR_INBOX_PATH.replace("{email}", username)
    
    # Return MAILINATOR_BASE_URL + formatted_path
    return MAILINATOR_BASE_URL + formatted_path


def get_mailinator_api_inbox_url(email):
    """
    Returns the API URL for a Mailinator inbox for a specific email

    Args:
        email (str): The email address to check

    Returns:
        str: API URL for the Mailinator inbox
    """
    # Extract username from email address
    username = email.split('@')[0]
    
    # Return f'{MAILINATOR_API_URL}/domains/mailinator.com/inboxes/{username}'
    return f"{MAILINATOR_API_URL}/domains/mailinator.com/inboxes/{username}"


def get_mailinator_api_message_url(message_id):
    """
    Returns the API URL for a specific Mailinator message

    Args:
        message_id (str): The ID of the message

    Returns:
        str: API URL for the Mailinator message
    """
    return f"{MAILINATOR_API_URL}/message/{message_id}"