# Storydoc Automation Framework - Test Cases

## 1. Introduction

This document outlines the automated test cases implemented in the Storydoc Automation Framework. The test suite is designed to validate the core user flows of the Storydoc application, including user registration, authentication, story creation, and story sharing.

The test cases follow the Page Object Model (POM) design pattern, which separates test logic from UI implementation details, improving maintainability and readability.

## 2. Test Organization and Structure

### 2.1 Test Suite Organization

The test cases are organized by functional areas:

| Functional Area | Description | Test File |
|-----------------|-------------|-----------|
| User Registration | Tests for new user registration | `test_signup.py` |
| User Authentication | Tests for user login | `test_signin.py` |
| Story Creation | Tests for story creation and editing | `test_story_creation.py` |
| Story Sharing | Tests for story sharing functionality | `test_story_sharing.py` |
| End-to-End Workflow | Tests for complete user journey | `test_end_to_end.py` |

### 2.2 Test Case Naming Convention

Test cases follow a consistent naming pattern:

```python
test_<feature>_<scenario>_<expected_result>
```

Examples:
- `test_registration_valid_credentials_success`
- `test_signin_invalid_password_failure`
- `test_story_creation_basic_template_success`

### 2.3 Test Case Structure

Each test case follows the Arrange-Act-Assert pattern:

1. **Arrange**: Set up the test environment and data
2. **Act**: Perform the actions being tested
3. **Assert**: Verify the expected outcomes

```python
def test_feature_scenario_result(self, setup):
    # Arrange
    # Set up test data and environment
    
    # Act
    # Perform the actions being tested
    
    # Assert
    # Verify the expected outcomes
```

## 3. User Registration Test Cases

### 3.1 Test Case: Valid User Registration

**Test ID**: TC-REG-001

**Description**: Verify that a new user can successfully register with valid credentials.

**Test Data**:
- Random email with mailinator.com domain
- Valid password (8+ characters, including uppercase, lowercase, and special characters)
- Valid user name

**Preconditions**:
- Application is accessible
- User does not already exist

**Steps**:
1. Navigate to the signup page
2. Enter a valid user name
3. Enter a valid email address (mailinator.com domain)
4. Enter a valid password
5. Accept the terms and conditions
6. Click the "Create account" button
7. Verify successful registration
8. Verify welcome email is received in Mailinator

**Expected Results**:
- User account is created successfully
- Success message is displayed
- Welcome email is received in the Mailinator inbox

**Code Example**:
```python
def test_registration_valid_credentials_success(self, setup):
    # Arrange
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    name = f"Test User {int(time.time())}"
    
    # Act
    self.signup_page.navigate_to()
    self.signup_page.enter_name(name)
    self.signup_page.enter_email(email)
    self.signup_page.enter_password(password)
    self.signup_page.check_terms()
    self.signup_page.click_signup_button()
    
    # Assert
    assert self.signup_page.is_signup_successful(), "Registration failed"
    
    # Verify email
    message = self.email_helper.wait_for_email(
        email, 
        "Welcome to Storydoc"
    )
    assert message is not None, "Welcome email not received"
```

### 3.2 Test Case: Registration with Invalid Email Format

**Test ID**: TC-REG-002

**Description**: Verify that the system validates email format during registration.

**Test Data**:
- Invalid email format (e.g., "invalid-email")
- Valid password
- Valid user name

**Preconditions**:
- Application is accessible

**Steps**:
1. Navigate to the signup page
2. Enter a valid user name
3. Enter an invalid email format
4. Enter a valid password
5. Accept the terms and conditions
6. Click the "Create account" button
7. Verify validation error message

**Expected Results**:
- Registration is not completed
- Validation error for email format is displayed

**Code Example**:
```python
def test_registration_invalid_email_format_failure(self, setup):
    # Arrange
    invalid_email = "invalid-email"
    password = "Test@123"
    name = f"Test User {int(time.time())}"
    
    # Act
    self.signup_page.navigate_to()
    self.signup_page.enter_name(name)
    self.signup_page.enter_email(invalid_email)
    self.signup_page.enter_password(password)
    self.signup_page.check_terms()
    self.signup_page.click_signup_button()
    
    # Assert
    assert self.signup_page.get_email_validation_error() is not None, "Email validation error not displayed"
    assert not self.signup_page.is_signup_successful(), "Registration succeeded with invalid email"
```

### 3.3 Test Case: Registration without Accepting Terms

**Test ID**: TC-REG-003

**Description**: Verify that registration requires accepting terms and conditions.

**Test Data**:
- Valid email with mailinator.com domain
- Valid password
- Valid user name

**Preconditions**:
- Application is accessible

**Steps**:
1. Navigate to the signup page
2. Enter a valid user name
3. Enter a valid email address
4. Enter a valid password
5. Do NOT accept the terms and conditions
6. Click the "Create account" button
7. Verify validation error message

**Expected Results**:
- Registration is not completed
- Validation error for terms acceptance is displayed

**Code Example**:
```python
def test_registration_without_terms_acceptance_failure(self, setup):
    # Arrange
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    name = f"Test User {int(time.time())}"
    
    # Act
    self.signup_page.navigate_to()
    self.signup_page.enter_name(name)
    self.signup_page.enter_email(email)
    self.signup_page.enter_password(password)
    # Do not check terms
    self.signup_page.click_signup_button()
    
    # Assert
    assert self.signup_page.get_terms_validation_error() is not None, "Terms validation error not displayed"
    assert not self.signup_page.is_signup_successful(), "Registration succeeded without accepting terms"
```

## 4. User Authentication Test Cases

### 4.1 Test Case: Valid User Authentication

**Test ID**: TC-AUTH-001

**Description**: Verify that a registered user can successfully sign in with valid credentials.

**Test Data**:
- Registered user email (created in setup)
- Valid password for the registered user

**Preconditions**:
- User account exists in the system

**Steps**:
1. Navigate to the signin page
2. Enter the registered email
3. Enter the correct password
4. Click the "Sign in" button
5. Verify successful login (dashboard loaded)

**Expected Results**:
- User is successfully authenticated
- User is redirected to the dashboard

**Code Example**:
```python
def test_authentication_valid_credentials_success(self, setup):
    # Arrange - Create a user first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    
    # Act
    self.signin_page.navigate_to()
    self.signin_page.enter_email(email)
    self.signin_page.enter_password(password)
    self.signin_page.click_signin_button()
    
    # Assert
    assert self.dashboard_page.is_loaded(), "Dashboard not loaded after signin"
```

### 4.2 Test Case: Authentication with Invalid Password

**Test ID**: TC-AUTH-002

**Description**: Verify that the system validates password during authentication.

**Test Data**:
- Registered user email
- Invalid password

**Preconditions**:
- User account exists in the system

**Steps**:
1. Navigate to the signin page
2. Enter the registered email
3. Enter an incorrect password
4. Click the "Sign in" button
5. Verify error message

**Expected Results**:
- Authentication fails
- Error message is displayed

**Code Example**:
```python
def test_authentication_invalid_password_failure(self, setup):
    # Arrange - Create a user first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    
    # Act
    self.signin_page.navigate_to()
    self.signin_page.enter_email(email)
    self.signin_page.enter_password("WrongPassword123!")
    self.signin_page.click_signin_button()
    
    # Assert
    assert self.signin_page.is_error_displayed(), "Error message not displayed"
    assert not self.dashboard_page.is_loaded(), "Dashboard loaded despite invalid credentials"
```

### 4.3 Test Case: Authentication with Unregistered User

**Test ID**: TC-AUTH-003

**Description**: Verify that the system validates user existence during authentication.

**Test Data**:
- Unregistered email address
- Valid password format

**Preconditions**:
- Application is accessible

**Steps**:
1. Navigate to the signin page
2. Enter an email that is not registered
3. Enter a password
4. Click the "Sign in" button
5. Verify error message

**Expected Results**:
- Authentication fails
- Error message is displayed

**Code Example**:
```python
def test_authentication_unregistered_user_failure(self, setup):
    # Arrange
    unregistered_email = f"unregistered.{int(time.time())}@mailinator.com"
    password = "Test@123"
    
    # Act
    self.signin_page.navigate_to()
    self.signin_page.enter_email(unregistered_email)
    self.signin_page.enter_password(password)
    self.signin_page.click_signin_button()
    
    # Assert
    assert self.signin_page.is_error_displayed(), "Error message not displayed"
    assert not self.dashboard_page.is_loaded(), "Dashboard loaded despite unregistered user"
```

## 5. Story Creation Test Cases

### 5.1 Test Case: Create New Story with Basic Template

**Test ID**: TC-STORY-001

**Description**: Verify that a user can create a new story using a basic template.

**Test Data**:
- Registered user credentials (created in setup)
- Story title

**Preconditions**:
- User is authenticated
- User is on the dashboard

**Steps**:
1. Click "New Story" button
2. Enter a story title
3. Select the "Basic" template
4. Click "Save" button
5. Verify story is saved successfully

**Expected Results**:
- Story is created successfully
- Success message is displayed
- Story appears in the user's dashboard

**Code Example**:
```python
def test_story_creation_basic_template_success(self, setup):
    # Arrange - Sign in first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    # Act
    story_title = f"Test Story {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    
    assert self.story_editor_page.is_loaded(), "Story editor not loaded"
    
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    # Assert
    assert self.story_editor_page.is_story_saved(), "Story not saved successfully"
    
    # Navigate back to dashboard and verify story exists
    self.dashboard_page.navigate_to()
    assert self.dashboard_page.is_story_visible(story_title), "Story not visible on dashboard"
```

### 5.2 Test Case: Create Story Without Title

**Test ID**: TC-STORY-002

**Description**: Verify that the system validates story title during creation.

**Test Data**:
- Registered user credentials (created in setup)
- Empty story title

**Preconditions**:
- User is authenticated
- User is on the dashboard

**Steps**:
1. Click "New Story" button
2. Leave the story title empty
3. Select the "Basic" template
4. Click "Save" button
5. Verify validation error message

**Expected Results**:
- Story is not created
- Validation error for title is displayed

**Code Example**:
```python
def test_story_creation_without_title_failure(self, setup):
    # Arrange - Sign in first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    # Act
    self.dashboard_page.click_create_story_button()
    
    assert self.story_editor_page.is_loaded(), "Story editor not loaded"
    
    # Leave title empty
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    # Assert
    assert self.story_editor_page.get_title_validation_error() is not None, "Title validation error not displayed"
    assert not self.story_editor_page.is_story_saved(), "Story saved despite missing title"
```

### 5.3 Test Case: Create Story with Different Templates

**Test ID**: TC-STORY-003

**Description**: Verify that a user can create stories using different templates.

**Test Data**:
- Registered user credentials (created in setup)
- Story title
- Template options (e.g., "Basic", "Professional", "Creative")

**Preconditions**:
- User is authenticated
- User is on the dashboard

**Steps**:
1. Click "New Story" button
2. Enter a story title
3. Select a specific template
4. Click "Save" button
5. Verify story is saved successfully
6. Repeat for different templates

**Expected Results**:
- Stories are created successfully with different templates
- Each story appears in the user's dashboard

**Code Example**:
```python
@pytest.mark.parametrize("template", ["Basic", "Professional", "Creative"])
def test_story_creation_different_templates_success(self, setup, template):
    # Arrange - Sign in first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    # Act
    story_title = f"Test Story {template} {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    
    assert self.story_editor_page.is_loaded(), "Story editor not loaded"
    
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template(template)
    self.story_editor_page.save_story()
    
    # Assert
    assert self.story_editor_page.is_story_saved(), f"Story not saved with {template} template"
```

## 6. Story Sharing Test Cases

### 6.1 Test Case: Share Story with Valid Recipient

**Test ID**: TC-SHARE-001

**Description**: Verify that a user can share a story with a valid recipient.

**Test Data**:
- Registered user credentials (created in setup)
- Story title (created in setup)
- Recipient email with mailinator.com domain

**Preconditions**:
- User is authenticated
- User has created a story

**Steps**:
1. Navigate to a created story
2. Click "Share" button
3. Enter a valid recipient email
4. Click "Share" button in the sharing dialog
5. Verify sharing success message
6. Verify sharing email is received in Mailinator

**Expected Results**:
- Story is shared successfully
- Success message is displayed
- Sharing email is received by the recipient
- Email contains a link to the shared story

**Code Example**:
```python
def test_story_sharing_valid_recipient_success(self, setup):
    # Arrange - Sign in and create a story first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    story_title = f"Test Story {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    # Act
    recipient_email = self.email_helper.generate_email_address("recipient")
    self.story_editor_page.click_share_button()
    
    self.share_dialog_page.enter_recipient_email(recipient_email)
    self.share_dialog_page.click_share_button()
    
    # Assert
    assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"
    
    # Verify email received
    message = self.email_helper.wait_for_email(
        recipient_email, 
        "Story shared with you"
    )
    assert message is not None, "Sharing email not received"
    
    # Verify sharing link
    sharing_link = self.email_helper.extract_verification_link(message)
    assert sharing_link is not None, "Sharing link not found in email"
```

### 6.2 Test Case: Share Story with Invalid Email Format

**Test ID**: TC-SHARE-002

**Description**: Verify that the system validates recipient email format during sharing.

**Test Data**:
- Registered user credentials (created in setup)
- Story title (created in setup)
- Invalid email format (e.g., "invalid-email")

**Preconditions**:
- User is authenticated
- User has created a story

**Steps**:
1. Navigate to a created story
2. Click "Share" button
3. Enter an invalid email format
4. Click "Share" button in the sharing dialog
5. Verify validation error message

**Expected Results**:
- Story is not shared
- Validation error for email format is displayed

**Code Example**:
```python
def test_story_sharing_invalid_email_format_failure(self, setup):
    # Arrange - Sign in and create a story first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    story_title = f"Test Story {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    # Act
    invalid_email = "invalid-email"
    self.story_editor_page.click_share_button()
    
    self.share_dialog_page.enter_recipient_email(invalid_email)
    self.share_dialog_page.click_share_button()
    
    # Assert
    assert self.share_dialog_page.get_email_validation_error() is not None, "Email validation error not displayed"
    assert not self.share_dialog_page.is_sharing_successful(), "Sharing succeeded with invalid email"
```

### 6.3 Test Case: Share Story with Multiple Recipients

**Test ID**: TC-SHARE-003

**Description**: Verify that a user can share a story with multiple recipients.

**Test Data**:
- Registered user credentials (created in setup)
- Story title (created in setup)
- Multiple recipient emails with mailinator.com domain

**Preconditions**:
- User is authenticated
- User has created a story

**Steps**:
1. Navigate to a created story
2. Click "Share" button
3. Enter multiple recipient emails
4. Click "Share" button in the sharing dialog
5. Verify sharing success message
6. Verify sharing emails are received in Mailinator for all recipients

**Expected Results**:
- Story is shared successfully with all recipients
- Success message is displayed
- Sharing emails are received by all recipients
- Emails contain links to the shared story

**Code Example**:
```python
def test_story_sharing_multiple_recipients_success(self, setup):
    # Arrange - Sign in and create a story first
    email = self.email_helper.generate_email_address()
    password = "Test@123"
    self.signup_page.complete_signup(
        f"Test User {int(time.time())}", 
        email, 
        password
    )
    self.signin_page.complete_signin(email, password)
    
    story_title = f"Test Story {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    # Act
    recipient_emails = [
        self.email_helper.generate_email_address("recipient1"),
        self.email_helper.generate_email_address("recipient2"),
        self.email_helper.generate_email_address("recipient3")
    ]
    
    self.story_editor_page.click_share_button()
    
    for recipient_email in recipient_emails:
        self.share_dialog_page.enter_recipient_email(recipient_email)
        self.share_dialog_page.add_another_recipient()
    
    self.share_dialog_page.click_share_button()
    
    # Assert
    assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"
    
    # Verify emails received for all recipients
    for recipient_email in recipient_emails:
        message = self.email_helper.wait_for_email(
            recipient_email, 
            "Story shared with you"
        )
        assert message is not None, f"Sharing email not received for {recipient_email}"
        
        # Verify sharing link
        sharing_link = self.email_helper.extract_verification_link(message)
        assert sharing_link is not None, f"Sharing link not found in email for {recipient_email}"
```

## 7. End-to-End Workflow Test Cases

### 7.1. Test Case: Complete User Journey

**Test ID**: TC-E2E-001

**Description**: Verify the complete user journey from registration to story sharing.

**Test Data**:
- New user information (random email, password, name)
- Story title
- Recipient email with mailinator.com domain

**Preconditions**:
- Application is accessible

**Steps**:
1. Register a new user
2. Sign in with the newly created user
3. Create a new story
4. Share the story with a recipient
5. Verify sharing email is received
6. Access the shared story via the sharing link

**Expected Results**:
- User registration is successful
- User authentication is successful
- Story creation is successful
- Story sharing is successful
- Sharing email is received
- Shared story is accessible via the sharing link

**Code Example**:
```python
def test_end_to_end_user_journey(self, setup):
    # Step 1: User Registration
    user_email = self.email_helper.generate_email_address()
    user_password = "Test@123"
    user_name = f"Test User {int(time.time())}"
    
    self.signup_page.navigate_to()
    self.signup_page.enter_name(user_name)
    self.signup_page.enter_email(user_email)
    self.signup_page.enter_password(user_password)
    self.signup_page.check_terms()
    self.signup_page.click_signup_button()
    
    assert self.signup_page.is_signup_successful(), "User registration failed"
    
    # Step 2: User Authentication
    self.signin_page.navigate_to()
    self.signin_page.enter_email(user_email)
    self.signin_page.enter_password(user_password)
    self.signin_page.click_signin_button()
    
    assert self.dashboard_page.is_loaded(), "User authentication failed"
    
    # Step 3: Story Creation
    story_title = f"Test Story {int(time.time())}"
    self.dashboard_page.click_create_story_button()
    
    assert self.story_editor_page.is_loaded(), "Story editor not loaded"
    
    self.story_editor_page.enter_story_title(story_title)
    self.story_editor_page.select_template("Basic")
    self.story_editor_page.save_story()
    
    assert self.story_editor_page.is_story_saved(), "Story creation failed"
    
    # Step 4: Story Sharing
    recipient_email = self.email_helper.generate_email_address("recipient")
    self.story_editor_page.click_share_button()
    
    self.share_dialog_page.enter_recipient_email(recipient_email)
    self.share_dialog_page.click_share_button()
    
    assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"
    
    # Step 5: Email Verification
    message = self.email_helper.wait_for_email(
        recipient_email, 
        "Story shared with you"
    )
    assert message is not None, "Sharing email not received"
    
    sharing_link = self.email_helper.extract_verification_link(message)
    assert sharing_link is not None, "Sharing link not found in email"
    
    # Step 6: Access Shared Story
    self.driver.get(sharing_link)
    
    # Verify shared story page is loaded - implementation depends on application UI
    time.sleep(3)  # Wait for page to load
    assert "Storydoc" in self.driver.title, "Shared story page not loaded"
```

## 8. Test Execution Instructions

### 8.1 Prerequisites

Before running the tests, ensure that the following prerequisites are met:

1. Python 3.9 or higher is installed
2. Required packages are installed via pip:
   ```
   pip install -r requirements.txt
   ```
3. Chrome browser is installed (or Firefox/Edge with appropriate configuration)
4. WebDriver is set up (handled automatically by webdriver-manager)
5. Environment variables are configured (or .env file is present)

### 8.2 Running Individual Test Cases

To run a specific test case:

```bash
# Run a specific test file
pytest path/to/test_file.py -v

# Run a specific test case
pytest path/to/test_file.py::TestClassName::test_method_name -v
```

### 8.3 Running Test Suites

To run a complete test suite:

```bash
# Run all tests
pytest -v

# Run tests with specific marker
pytest -m registration -v

# Run tests in parallel (4 processes)
pytest -v -n 4
```

### 8.4 Test Environment Configuration

The tests can be configured using environment variables or a .env file:

```
# Test Environment
BASE_URL=https://editor-staging.storydoc.com
DEFAULT_TIMEOUT=10
HEADLESS_MODE=false

# Test Data
TEST_EMAIL_DOMAIN=mailinator.com
TEST_USER_PASSWORD=Test@123

# Reporting
SCREENSHOT_DIR=reports/screenshots
REPORT_DIR=reports/html
```

## 9. Test Reporting Guidelines

### 9.1 HTML Reports

The test framework generates HTML reports using pytest-html:

```bash
# Generate HTML report
pytest --html=reports/report.html
```

### 9.2 Report Interpretation

The HTML report includes:

- Test results summary (pass/fail/skip)
- Test execution time
- Error messages for failed tests
- Screenshots for failed tests
- Environment information

### 9.3 Failure Analysis

When a test fails:

1. Review the error message in the HTML report
2. Check the screenshot captured at the point of failure
3. Review the logs for detailed information
4. Determine if it's a test issue or an application issue
5. For application issues, document the defect with steps to reproduce

### 9.4 Test Results Communication

Test results should be communicated to the team through:

1. HTML reports attached to CI/CD pipeline results
2. Integration with issue tracking system for failures
3. Regular testing status updates in team meetings
4. Automated notifications for critical test failures

## 10. Test Maintenance Guidelines

### 10.1 When to Update Tests

Tests should be updated in the following scenarios:

1. Application UI changes affecting element locators
2. New features or functionality are added
3. Existing functionality is modified
4. Test framework improvements are needed
5. Test flakiness is detected

### 10.2 Locator Maintenance

To maintain locators:

1. Keep locators in separate files by page
2. Use stable locator strategies (ID, name, CSS selectors)
3. Avoid using XPath when possible
4. Use meaningful names for locators
5. Update locators as soon as UI changes are detected

### 10.3 Test Data Maintenance

To maintain test data:

1. Use dynamic test data generation where possible
2. Avoid hardcoded test data
3. Document any required test data setup
4. Clean up test data after test execution

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2023-07-01 | QA Team | Initial version |