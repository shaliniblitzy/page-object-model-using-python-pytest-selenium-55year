# Page Objects in Storydoc Automation Framework

## Introduction

Page Objects are a design pattern used in test automation to enhance test maintenance and reduce code duplication. In the Storydoc automation framework, Page Objects represent a key architectural component that encapsulates the interactions with different screens of the application. This document explains how Page Objects are implemented and used within the framework.

## Page Object Model Pattern

The Page Object Model (POM) pattern creates an object repository for web UI elements. Each page in the application is represented by a corresponding Page Object class. These classes contain methods that perform actions on the UI elements of that page and provide an interface for tests to interact with the page.

The core concept is separating the test logic from the page-specific code, which enhances maintainability, readability, and reusability of the test code.

## Benefits of Page Object Model

The POM pattern offers several significant benefits to our automation framework:

1. **Improved Maintainability**: When the UI changes, only the Page Object needs to be updated, not the tests.
2. **Reduced Code Duplication**: Common interactions with pages are defined once and reused across multiple tests.
3. **Increased Readability**: Tests express business workflows rather than complex UI interactions.
4. **Better Test Organization**: Clear separation between test logic and page interaction logic.
5. **Abstraction**: Tests are isolated from the details of UI elements and their locators.
6. **Reusability**: Page Objects can be shared across multiple test cases.

## Framework Implementation

In the Storydoc automation framework, the POM pattern is implemented with a clear hierarchy:

- A **BasePage** class contains common functionality shared across all pages
- Specific **Page Objects** (e.g., SignupPage, DashboardPage) inherit from BasePage
- **Locators** are separated into dedicated files for better maintainability
- **Tests** use Page Objects to express business workflows

This structure allows for a clean separation of concerns and makes the tests more resilient to UI changes.

# Base Page Structure

## BasePage Class

The BasePage class serves as the foundation for all page objects in the framework. It encapsulates common functionality that is shared across all pages and provides a consistent interface for interacting with web elements.

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import os

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, driver):
        """Initialize the base page with WebDriver instance
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.url = None
        self.logger = logging.getLogger(__name__)
    
    # Additional methods will be described below
```

## Common Methods

The BasePage class provides a set of common methods that are used by all page objects to interact with the web elements:

```python
def open(self):
    """Open the page URL in the browser"""
    if self.url:
        self.logger.info(f"Opening URL: {self.url}")
        self.driver.get(self.url)
    else:
        self.logger.error("URL not defined for page")
        raise ValueError("URL not defined for page")

def find_element(self, locator):
    """Find an element using the provided locator
    
    Args:
        locator: Tuple containing locator strategy and value
        
    Returns:
        WebElement: The found element
    """
    try:
        self.logger.debug(f"Finding element: {locator}")
        return self.driver.find_element(*locator)
    except NoSuchElementException as e:
        self.logger.error(f"Element not found: {locator}")
        self.take_screenshot(f"element_not_found_{locator[1]}")
        raise e

def click(self, locator):
    """Click on the element identified by the locator
    
    Args:
        locator: Tuple containing locator strategy and value
    """
    self.logger.debug(f"Clicking element: {locator}")
    element = self.wait_for_element(locator)
    element.click()

def input_text(self, locator, text):
    """Enter text into the element identified by the locator
    
    Args:
        locator: Tuple containing locator strategy and value
        text: Text to enter
    """
    self.logger.debug(f"Entering text '{text}' into element: {locator}")
    element = self.wait_for_element(locator)
    element.clear()
    element.send_keys(text)

def get_text(self, locator):
    """Get text from the element identified by the locator
    
    Args:
        locator: Tuple containing locator strategy and value
        
    Returns:
        str: Text of the element
    """
    self.logger.debug(f"Getting text from element: {locator}")
    element = self.wait_for_element(locator)
    return element.text
```

## Wait Strategies

Proper synchronization is crucial for reliable test automation. The BasePage class implements explicit wait strategies to handle timing issues:

```python
def wait_for_element(self, locator, timeout=10):
    """Wait for the element to be visible and return it
    
    Args:
        locator: Tuple containing locator strategy and value
        timeout: Maximum time to wait for element
        
    Returns:
        WebElement: The found element
    """
    try:
        self.logger.debug(f"Waiting for element: {locator}")
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    except TimeoutException as e:
        self.logger.error(f"Timeout waiting for element: {locator}")
        self.take_screenshot(f"timeout_{locator[1]}")
        raise e

def wait_for_element_to_disappear(self, locator, timeout=10):
    """Wait for the element to disappear from the page
    
    Args:
        locator: Tuple containing locator strategy and value
        timeout: Maximum time to wait for element to disappear
        
    Returns:
        bool: True if element disappeared, False otherwise
    """
    try:
        self.logger.debug(f"Waiting for element to disappear: {locator}")
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )
        return True
    except TimeoutException:
        self.logger.debug(f"Element still visible: {locator}")
        return False

def is_element_visible(self, locator, timeout=10):
    """Check if the element is visible on the page
    
    Args:
        locator: Tuple containing locator strategy and value
        timeout: Maximum time to wait for element visibility
        
    Returns:
        bool: True if element is visible, False otherwise
    """
    try:
        self.logger.debug(f"Checking if element is visible: {locator}")
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return True
    except TimeoutException:
        self.logger.debug(f"Element not visible: {locator}")
        return False
```

## Error Handling

The BasePage class implements robust error handling strategies to capture and diagnose issues:

```python
def take_screenshot(self, filename):
    """Capture a screenshot and save it with the given filename
    
    Args:
        filename: Name for the screenshot file
        
    Returns:
        str: Path to the saved screenshot
    """
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    
    filepath = os.path.join(screenshots_dir, f"{filename}.png")
    self.driver.save_screenshot(filepath)
    self.logger.info(f"Screenshot saved: {filepath}")
    return filepath
```

# Application Page Objects

The framework includes several page objects that represent different screens of the Storydoc application. Each page object inherits from the BasePage class and implements page-specific methods.

## SignupPage

The SignupPage object encapsulates interactions with the signup page:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from .locators import SignupLocators

class SignupPage(BasePage):
    """Page object for the signup page"""
    
    def __init__(self, driver):
        """Initialize the signup page
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.url = "https://editor-staging.storydoc.com/sign-up"
    
    def navigate_to(self):
        """Navigate to the signup page"""
        self.open()
    
    def enter_email(self, email):
        """Enter the email address in the email field
        
        Args:
            email: Email address to enter
        """
        self.input_text(SignupLocators.EMAIL_FIELD, email)
    
    def enter_password(self, password):
        """Enter the password in the password field
        
        Args:
            password: Password to enter
        """
        self.input_text(SignupLocators.PASSWORD_FIELD, password)
    
    def enter_name(self, name):
        """Enter the name in the name field
        
        Args:
            name: Name to enter
        """
        self.input_text(SignupLocators.NAME_FIELD, name)
    
    def accept_terms(self):
        """Check the terms and conditions checkbox"""
        self.click(SignupLocators.TERMS_CHECKBOX)
    
    def click_signup_button(self):
        """Click the signup button"""
        self.click(SignupLocators.SIGNUP_BUTTON)
    
    def is_signup_successful(self):
        """Verify if signup was successful
        
        Returns:
            bool: True if signup was successful, False otherwise
        """
        return self.is_element_visible(SignupLocators.SIGNUP_SUCCESS)
    
    def complete_signup(self, email, password, name):
        """Complete the entire signup process
        
        Args:
            email: Email address to use
            password: Password to use
            name: Name to use
            
        Returns:
            bool: True if signup was successful, False otherwise
        """
        self.navigate_to()
        self.enter_email(email)
        self.enter_password(password)
        self.enter_name(name)
        self.accept_terms()
        self.click_signup_button()
        return self.is_signup_successful()
```

## SigninPage

The SigninPage object encapsulates interactions with the signin page:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from .locators import SigninLocators

class SigninPage(BasePage):
    """Page object for the signin page"""
    
    def __init__(self, driver):
        """Initialize the signin page
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.url = "https://editor-staging.storydoc.com/sign-in"
    
    def navigate_to(self):
        """Navigate to the signin page"""
        self.open()
    
    def enter_email(self, email):
        """Enter the email address in the email field
        
        Args:
            email: Email address to enter
        """
        self.input_text(SigninLocators.EMAIL_FIELD, email)
    
    def enter_password(self, password):
        """Enter the password in the password field
        
        Args:
            password: Password to enter
        """
        self.input_text(SigninLocators.PASSWORD_FIELD, password)
    
    def click_signin_button(self):
        """Click the signin button"""
        self.click(SigninLocators.SIGNIN_BUTTON)
    
    def is_signin_successful(self):
        """Verify if signin was successful
        
        Returns:
            bool: True if signin was successful, False otherwise
        """
        # Success is determined by redirecting to the dashboard
        # This could be implemented by checking for dashboard elements
        # or by checking the current URL
        return "dashboard" in self.driver.current_url
    
    def complete_signin(self, email, password):
        """Complete the entire signin process
        
        Args:
            email: Email address to use
            password: Password to use
            
        Returns:
            bool: True if signin was successful, False otherwise
        """
        self.navigate_to()
        self.enter_email(email)
        self.enter_password(password)
        self.click_signin_button()
        return self.is_signin_successful()
```

## DashboardPage

The DashboardPage object encapsulates interactions with the dashboard page:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from .locators import DashboardLocators

class DashboardPage(BasePage):
    """Page object for the dashboard page"""
    
    def __init__(self, driver):
        """Initialize the dashboard page
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.url = "https://editor-staging.storydoc.com/dashboard"
    
    def is_loaded(self):
        """Verify if the dashboard page is loaded
        
        Returns:
            bool: True if dashboard is loaded, False otherwise
        """
        return self.is_element_visible(DashboardLocators.CREATE_STORY_BUTTON)
    
    def click_create_story_button(self):
        """Click the create story button"""
        self.click(DashboardLocators.CREATE_STORY_BUTTON)
    
    def get_story_list(self):
        """Get the list of available stories
        
        Returns:
            List[WebElement]: List of story elements
        """
        return self.driver.find_elements(*DashboardLocators.STORY_ITEMS)
    
    def open_story(self, story_name):
        """Open a specific story by name
        
        Args:
            story_name: Name of the story to open
            
        Returns:
            bool: True if story was found and opened, False otherwise
        """
        stories = self.get_story_list()
        for story in stories:
            if story_name in story.text:
                # Find the edit button within this story element
                edit_button = story.find_element(*DashboardLocators.EDIT_BUTTON)
                edit_button.click()
                return True
        
        self.logger.warning(f"Story '{story_name}' not found in the dashboard")
        return False
```

## StoryEditorPage

The StoryEditorPage object encapsulates interactions with the story editor:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from .locators import StoryEditorLocators

class StoryEditorPage(BasePage):
    """Page object for the story editor page"""
    
    def is_loaded(self):
        """Verify if the story editor is loaded
        
        Returns:
            bool: True if story editor is loaded, False otherwise
        """
        return self.is_element_visible(StoryEditorLocators.STORY_TITLE_INPUT)
    
    def enter_story_title(self, title):
        """Enter the story title
        
        Args:
            title: Title to enter
        """
        self.input_text(StoryEditorLocators.STORY_TITLE_INPUT, title)
    
    def select_template(self, template_name):
        """Select a template for the story
        
        Args:
            template_name: Name of the template to select
            
        Returns:
            bool: True if template was found and selected, False otherwise
        """
        templates = self.driver.find_elements(*StoryEditorLocators.TEMPLATE_OPTIONS)
        for template in templates:
            if template_name in template.text:
                template.click()
                return True
        
        self.logger.warning(f"Template '{template_name}' not found")
        return False
    
    def save_story(self):
        """Save the current story"""
        self.click(StoryEditorLocators.SAVE_BUTTON)
        
        # Wait for save confirmation
        return self.wait_for_element(StoryEditorLocators.SAVE_SUCCESS_MESSAGE, 15)
    
    def is_story_saved(self):
        """Check if the story has been saved successfully
        
        Returns:
            bool: True if save success message is visible, False otherwise
        """
        return self.is_element_visible(StoryEditorLocators.SAVE_SUCCESS_MESSAGE)
    
    def click_share_button(self):
        """Click the share button to open the share dialog"""
        self.click(StoryEditorLocators.SHARE_BUTTON)
```

## ShareDialogPage

The ShareDialogPage object encapsulates interactions with the share dialog:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from .locators import ShareDialogLocators

class ShareDialogPage(BasePage):
    """Page object for the share dialog"""
    
    def enter_recipient_email(self, email):
        """Enter the recipient's email address
        
        Args:
            email: Email address to enter
        """
        self.input_text(ShareDialogLocators.RECIPIENT_EMAIL_INPUT, email)
    
    def enter_personal_message(self, message):
        """Enter a personal message
        
        Args:
            message: Message to enter
        """
        self.input_text(ShareDialogLocators.PERSONAL_MESSAGE_TEXTAREA, message)
    
    def click_share_button(self):
        """Click the share button"""
        self.click(ShareDialogLocators.SHARE_BUTTON)
    
    def is_sharing_successful(self):
        """Verify if sharing was successful
        
        Returns:
            bool: True if sharing was successful, False otherwise
        """
        return self.is_element_visible(ShareDialogLocators.SHARE_SUCCESS_MESSAGE)
    
    def complete_sharing(self, email, message=None):
        """Complete the entire sharing process
        
        Args:
            email: Recipient email address
            message: Optional personal message
            
        Returns:
            bool: True if sharing was successful, False otherwise
        """
        self.enter_recipient_email(email)
        
        if message:
            self.enter_personal_message(message)
        
        self.click_share_button()
        return self.is_sharing_successful()
```

## MailinatorPage

Although the framework primarily uses Mailinator's API for email verification, we also have a page object for UI interactions with Mailinator:

```python
from selenium.webdriver.common.by import By
from .base_page import BasePage

class MailinatorPage(BasePage):
    """Page object for Mailinator email verification"""
    
    def __init__(self, driver):
        """Initialize the Mailinator page
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.base_url = "https://www.mailinator.com/v4/public/inboxes.jsp?to="
    
    def navigate_to_inbox(self, email_address):
        """Navigate to the inbox for the specified email address
        
        Args:
            email_address: Email address to check
        """
        username = email_address.split('@')[0]
        self.url = f"{self.base_url}{username}"
        self.open()
    
    def find_email_by_subject(self, subject):
        """Find an email by subject
        
        Args:
            subject: Subject of the email to find
            
        Returns:
            WebElement: The found email element, or None if not found
        """
        # Implementation would depend on Mailinator's UI structure
        # This is a simplified example
        emails = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{subject}')]")
        if emails:
            return emails[0]
        return None
    
    def open_email(self, email_element):
        """Open an email
        
        Args:
            email_element: Email element to open
        """
        email_element.click()
    
    def get_verification_link(self):
        """Extract verification link from the email content
        
        Returns:
            str: Verification link, or None if not found
        """
        # Implementation would depend on Mailinator's UI structure
        # This is a simplified example
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'verify') or contains(@href, 'confirm')]")
        if links:
            return links[0].get_attribute("href")
        return None
```

# Locator Strategy

## Locator Organization

In the Storydoc automation framework, locators are organized into separate files to improve maintainability. Each page has its corresponding locator file.

```python
# locators/base_locators.py
from selenium.webdriver.common.by import By

class BaseLocators:
    """Base locators used across multiple pages"""
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading-spinner")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".success-message")

# locators/signup_locators.py
from selenium.webdriver.common.by import By
from .base_locators import BaseLocators

class SignupLocators(BaseLocators):
    """Locators for the signup page"""
    EMAIL_FIELD = (By.ID, "email")
    PASSWORD_FIELD = (By.ID, "password")
    NAME_FIELD = (By.ID, "name")
    TERMS_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SIGNUP_SUCCESS = (By.CSS_SELECTOR, ".signup-success")
```

## Selector Types

The framework uses different types of selectors based on the stability and uniqueness of the elements:

1. **ID Selectors**: The most reliable, used whenever an element has a stable ID
   ```python
   EMAIL_FIELD = (By.ID, "email")
   ```

2. **CSS Selectors**: Used for elements without IDs but with distinct CSS classes or attributes
   ```python
   SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
   ```

3. **XPath Selectors**: Used as a last resort for complex element identification
   ```python
   COMPLEX_ELEMENT = (By.XPATH, "//div[@class='container']//button[contains(text(), 'Submit')]")
   ```

4. **Other Selectors**: Link text, partial link text, tag name, and class name selectors are used where appropriate
   ```python
   SIGNUP_LINK = (By.LINK_TEXT, "Sign up")
   ```

## Maintaining Locators

When the application UI changes, only the locator files need to be updated, not the page objects or tests. This separation makes maintenance much easier.

## Best Practices

- Use the most stable locator strategy available (ID > CSS > XPath)
- Keep locators in separate files to improve maintainability
- Use descriptive names for locators to improve readability
- Add comments for complex locators to explain their purpose
- Regularly verify locators to ensure they still work with the latest application version

# Using Page Objects in Tests

## Page Object Initialization

Page objects are typically initialized in test fixtures or in the test methods themselves:

```python
@pytest.fixture
def signup_page(driver):
    """Fixture that returns a SignupPage instance"""
    return SignupPage(driver)

def test_valid_user_registration(signup_page):
    """Test that a user can register with valid credentials"""
    email = f"test.user.{int(time.time())}@mailinator.com"
    password = "Test@123"
    name = "Test User"
    
    # Use the page object to interact with the page
    signup_page.navigate_to()
    signup_page.enter_email(email)
    signup_page.enter_password(password)
    signup_page.enter_name(name)
    signup_page.accept_terms()
    signup_page.click_signup_button()
    
    # Verify the registration was successful
    assert signup_page.is_signup_successful(), "Registration failed"
```

## Method Chaining

For more concise test code, page objects can be designed to support method chaining:

```python
def enter_email(self, email):
    """Enter the email address in the email field
    
    Args:
        email: Email address to enter
        
    Returns:
        self: For method chaining
    """
    self.input_text(SignupLocators.EMAIL_FIELD, email)
    return self

# Usage in a test
signup_page.navigate_to() \
    .enter_email(email) \
    .enter_password(password) \
    .enter_name(name) \
    .accept_terms() \
    .click_signup_button()
```

## Handling Page Transitions

When an action on one page leads to another page, the page object method should return the new page object:

```python
def click_signup_button(self):
    """Click the signup button
    
    Returns:
        DashboardPage: If signup is successful
        self: If still on signup page
    """
    self.click(SignupLocators.SIGNUP_BUTTON)
    
    if self.is_signup_successful():
        from .dashboard_page import DashboardPage
        return DashboardPage(self.driver)
    return self

# Usage in a test
dashboard_page = signup_page.navigate_to() \
    .enter_email(email) \
    .enter_password(password) \
    .enter_name(name) \
    .accept_terms() \
    .click_signup_button()

# Verify we're on the dashboard
assert dashboard_page.is_loaded(), "Dashboard not loaded after signup"
```

## Assertions

While page objects can include verification methods (like `is_signup_successful()`), the actual assertions should be made in the test code, not in the page objects:

```python
# Good practice - assertion in test code
assert signup_page.is_signup_successful(), "Registration failed"

# Bad practice - assertion in page object
def verify_signup_successful(self):
    """Verify signup was successful"""
    assert self.is_element_visible(SignupLocators.SIGNUP_SUCCESS), "Registration failed"
```

# Best Practices

## Single Responsibility Principle

Each page object should represent a single page or component of the application. Methods in the page object should only interact with elements on that page.

```python
# Good - SignupPage only interacts with signup page elements
class SignupPage(BasePage):
    def enter_email(self, email):
        self.input_text(SignupLocators.EMAIL_FIELD, email)

# Bad - SignupPage interacts with dashboard elements
class SignupPage(BasePage):
    def click_create_story_after_signup(self):
        self.click(DashboardLocators.CREATE_STORY_BUTTON)
```

## Method Naming Conventions

Page object methods should clearly describe the action being performed:

- Use verb-noun format for action methods: `enter_email()`, `click_signup_button()`
- Use is/has prefix for boolean methods: `is_signup_successful()`, `has_error_message()`
- Use get prefix for retrieval methods: `get_error_message()`, `get_story_list()`

## Error Handling

Page objects should handle expected exceptions and provide clear error messages:

```python
def click_signup_button(self):
    """Click the signup button"""
    try:
        self.click(SignupLocators.SIGNUP_BUTTON)
    except Exception as e:
        self.logger.error(f"Failed to click signup button: {str(e)}")
        self.take_screenshot("signup_button_click_error")
        raise
```

## Synchronization

Page objects should handle synchronization to ensure reliable test execution:

```python
def wait_for_dashboard_to_load(self):
    """Wait for the dashboard to fully load"""
    try:
        self.wait_for_element(DashboardLocators.CREATE_STORY_BUTTON)
        self.wait_for_element_to_disappear(BaseLocators.LOADING_INDICATOR)
        return True
    except TimeoutException:
        self.logger.error("Dashboard did not load within expected time")
        self.take_screenshot("dashboard_load_timeout")
        return False
```

## Extending Page Objects

As the application grows, page objects may need to be extended. Follow these guidelines:

- Create new page objects for new pages or significant components
- Refactor common functionality into the BasePage or utility classes
- Consider using composition for shared components (e.g., a header or footer that appears on multiple pages)

# Page Object Examples

## Basic Page Object Example

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    # Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def navigate_to(self):
        self.driver.get("https://example.com/login")
        return self
    
    def enter_username(self, username):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT)).send_keys(username)
        return self
    
    def enter_password(self, password):
        self.wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT)).send_keys(password)
        return self
    
    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()
        # Determine whether login was successful
        if "dashboard" in self.driver.current_url:
            return DashboardPage(self.driver)
        return self
    
    def get_error_message(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE)).text
        except:
            return None
    
    def login(self, username, password):
        return (self.navigate_to()
                .enter_username(username)
                .enter_password(password)
                .click_login())
```

## Complex Interactions Example

This example demonstrates handling more complex interactions like drag and drop, file uploads, and working with iframes:

```python
class DocumentEditorPage(BasePage):
    # Locators
    FILE_UPLOAD_INPUT = (By.ID, "fileUpload")
    DRAG_SOURCE = (By.ID, "dragSource")
    DROP_TARGET = (By.ID, "dropTarget")
    EDITOR_IFRAME = (By.ID, "editorFrame")
    EDITOR_CONTENT = (By.CSS_SELECTOR, ".editor-content")
    SAVE_BUTTON = (By.ID, "saveButton")
    
    def upload_file(self, file_path):
        """Upload a file
        
        Args:
            file_path: Path to the file to upload
        """
        # File upload requires the input element, not clicking a button
        upload_input = self.find_element(self.FILE_UPLOAD_INPUT)
        upload_input.send_keys(file_path)
        
        # Wait for upload to complete
        self.wait_for_element_to_disappear((By.CSS_SELECTOR, ".upload-progress"))
        return self
    
    def drag_element_to_target(self):
        """Perform drag and drop operation"""
        from selenium.webdriver.common.action_chains import ActionChains
        
        source = self.wait_for_element(self.DRAG_SOURCE)
        target = self.wait_for_element(self.DROP_TARGET)
        
        actions = ActionChains(self.driver)
        actions.drag_and_drop(source, target).perform()
        return self
    
    def switch_to_editor_frame(self):
        """Switch to the editor iframe"""
        iframe = self.wait_for_element(self.EDITOR_IFRAME)
        self.driver.switch_to.frame(iframe)
        return self
    
    def switch_to_main_content(self):
        """Switch back to main content from iframe"""
        self.driver.switch_to.default_content()
        return self
    
    def edit_content(self, content):
        """Edit content in the editor
        
        Args:
            content: Content to enter
        """
        self.switch_to_editor_frame()
        
        editor = self.wait_for_element(self.EDITOR_CONTENT)
        editor.clear()
        editor.send_keys(content)
        
        self.switch_to_main_content()
        return self
    
    def save_document(self):
        """Save the document"""
        self.click(self.SAVE_BUTTON)
        self.wait_for_element((By.CSS_SELECTOR, ".save-success"))
        return self
```

## Page Factory Pattern

The Page Factory pattern is an extension of the Page Object Model that uses annotations to simplify element location:

```python
class PageFactory:
    """A simple Page Factory implementation"""
    
    @staticmethod
    def init_elements(page_instance):
        """Initialize elements in the page instance
        
        Args:
            page_instance: Page object instance to initialize
        """
        for attr_name, attr_value in page_instance.__class__.__dict__.items():
            if isinstance(attr_value, tuple) and len(attr_value) == 2:
                locator_type, locator_value = attr_value
                
                # Create a property that finds the element when accessed
                def create_getter(locator):
                    def getter(self):
                        return self.driver.find_element(*locator)
                    return getter
                
                # Add the property to the instance
                setattr(page_instance.__class__, attr_name, property(create_getter(attr_value)))
        
        return page_instance

# Usage example
class LoginPageWithFactory:
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    def __init__(self, driver):
        self.driver = driver
        PageFactory.init_elements(self)
    
    def login(self, username, password):
        # Now we can access elements as properties
        self.USERNAME_INPUT.send_keys(username)
        self.PASSWORD_INPUT.send_keys(password)
        self.LOGIN_BUTTON.click()
```

## Page Object with API Interactions

Sometimes page objects need to interact with APIs in addition to UI elements:

```python
import requests

class UserProfilePage(BasePage):
    # Locators
    PROFILE_HEADER = (By.CSS_SELECTOR, ".profile-header")
    NAME_FIELD = (By.ID, "name")
    EMAIL_FIELD = (By.ID, "email")
    SAVE_BUTTON = (By.ID, "saveProfile")
    
    def __init__(self, driver, api_client=None):
        """Initialize the page object
        
        Args:
            driver: WebDriver instance
            api_client: Optional API client for backend operations
        """
        super().__init__(driver)
        self.api_client = api_client
        self.url = "https://example.com/profile"
    
    def get_user_data_from_api(self, user_id):
        """Get user data from the API
        
        Args:
            user_id: ID of the user to get data for
            
        Returns:
            dict: User data from the API
        """
        if not self.api_client:
            self.logger.warning("API client not available")
            return None
        
        response = self.api_client.get(f"/api/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        
        self.logger.error(f"Failed to get user data: {response.status_code}")
        return None
    
    def verify_ui_matches_api(self, user_id):
        """Verify UI data matches API data
        
        Args:
            user_id: ID of the user to verify
            
        Returns:
            bool: True if UI matches API, False otherwise
        """
        api_data = self.get_user_data_from_api(user_id)
        if not api_data:
            return False
        
        name_in_ui = self.get_text(self.NAME_FIELD)
        email_in_ui = self.get_text(self.EMAIL_FIELD)
        
        return (
            name_in_ui == api_data.get("name") and
            email_in_ui == api_data.get("email")
        )
```

# Troubleshooting Common Issues

## Element Not Found

One of the most common issues in test automation is elements not being found. This can happen for several reasons:

1. **The locator is incorrect**: Verify the locator is correct and matches the element in the current version of the application.

2. **Timing issue**: The element might not be loaded when the test tries to interact with it.
   ```python
   # Solution: Use explicit waits
   def click_button(self):
       try:
           self.wait_for_element(self.BUTTON_LOCATOR)
           self.click(self.BUTTON_LOCATOR)
       except TimeoutException:
           self.logger.error("Button not found after waiting")
           self.take_screenshot("button_not_found")
           raise
   ```

3. **Element is in an iframe**: If the element is inside an iframe, you need to switch to the iframe first.
   ```python
   # Solution: Switch to iframe
   def click_button_in_iframe(self):
       iframe = self.wait_for_element(self.IFRAME_LOCATOR)
       self.driver.switch_to.frame(iframe)
       self.click(self.BUTTON_LOCATOR)
       self.driver.switch_to.default_content()
   ```

4. **Element is not visible or is disabled**: The element might be in the DOM but not visible or interactive.
   ```python
   # Solution: Check element state
   def is_button_clickable(self):
       try:
           self.wait.until(EC.element_to_be_clickable(self.BUTTON_LOCATOR))
           return True
       except TimeoutException:
           return False
   ```

## Stale Element References

A stale element reference occurs when an element is no longer attached to the DOM. This commonly happens after page refreshes or navigation:

```python
# Problem
element = self.find_element(self.BUTTON_LOCATOR)
self.driver.refresh()
element.click()  # This will fail with StaleElementReferenceException

# Solution: Re-find the element after page changes
def safe_click(self, locator):
    tries = 0
    while tries < 3:
        try:
            element = self.find_element(locator)
            element.click()
            return
        except StaleElementReferenceException:
            tries += 1
    
    raise Exception(f"Element {locator} is still stale after 3 attempts")
```

## Timing Issues

Timing issues occur when the test execution is faster than the application's response:

```python
# Problem
self.click(self.SUBMIT_BUTTON)
result = self.get_text(self.RESULT_FIELD)  # This might fail if the result isn't loaded yet

# Solution: Wait for the expected condition
def submit_and_get_result(self):
    self.click(self.SUBMIT_BUTTON)
    
    # Wait for the result to be available
    self.wait_for_element(self.RESULT_FIELD)
    
    # Now get the text
    return self.get_text(self.RESULT_FIELD)
```

## Browser Compatibility

Different browsers may render the application differently, causing tests to fail in some browsers but pass in others:

```python
# Solution: Use browser-specific locators if necessary
def get_button_locator(self):
    browser_name = self.driver.capabilities['browserName'].lower()
    
    if browser_name == 'firefox':
        return (By.CSS_SELECTOR, "#button-firefox")
    else:
        return (By.CSS_SELECTOR, "#button-default")

def click_browser_specific_button(self):
    locator = self.get_button_locator()
    self.click(locator)
```

These troubleshooting techniques will help you address the most common issues encountered when working with Page Objects in the Storydoc automation framework.