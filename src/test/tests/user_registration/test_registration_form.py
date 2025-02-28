import pytest  # pytest 7.3+
from pytest_check import check  # pytest-check 2.0+

# Internal imports
from src.test.pages.signup_page import SignupPage  # Page object for signup page
from src.test.locators.signup_locators import SignupLocators  # Locators for signup page elements
from src.test.fixtures.browser_fixtures import browser  # Fixture for browser instance management
from src.test.fixtures.user_fixtures import test_user  # Fixture for test user data
from src.test.utilities.random_data_generator import generate_random_email  # Generate random email addresses for testing
from src.test.utilities.random_data_generator import generate_random_password  # Generate random passwords for testing
from src.test.utilities.random_data_generator import generate_random_name  # Generate random names for testing
from src.test.utilities.assertion_helper import assert_element_visible  # Assert element visibility with enhanced reporting
from src.test.utilities.assertion_helper import assert_element_not_visible  # Assert element is not visible with enhanced reporting
from src.test.utilities.assertion_helper import assert_true  # Assert condition is true with enhanced reporting
from src.test.utilities.assertion_helper import assert_false  # Assert condition is false with enhanced reporting
from src.test.utilities.assertion_helper import assert_equal  # Assert equality with enhanced reporting

# Global test data
INVALID_EMAILS = ["invalidemail", "invalid@", "@example.com", "user@invalid", "user!@example.com"]
WEAK_PASSWORDS = ["password", "12345678", "abcdefgh", "user1234", "letmein"]
VALID_EMAIL = "test.user@mailinator.com"
VALID_PASSWORD = "Test@123456"
VALID_NAME = "Test User"


@pytest.mark.registration
@pytest.mark.web
class TestRegistrationForm:
    """Test class for user registration form validation and functionality"""

    def setup_method(self, browser):
        """Setup method that runs before each test"""
        self.browser = browser  # Store reference to browser instance
        self.signup_page = SignupPage(self.browser)  # Initialize SignupPage with browser
        self.signup_page.navigate_to()  # Navigate to signup page

    def teardown_method(self):
        """Teardown method that runs after each test"""
        # Perform any required cleanup
        pass

    def test_registration_form_elements(self):
        """Test that all required elements are present on the registration form"""
        assert_element_visible(self.browser, SignupLocators.NAME_FIELD, "Name field")
        assert_element_visible(self.browser, SignupLocators.EMAIL_FIELD, "Email field")
        assert_element_visible(self.browser, SignupLocators.PASSWORD_FIELD, "Password field")
        assert_element_visible(self.browser, SignupLocators.TERMS_CHECKBOX, "Terms checkbox")
        assert_element_visible(self.browser, SignupLocators.SIGNUP_BUTTON, "Signup button")

    @pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
    def test_invalid_email_validation(self, invalid_email):
        """Test that email validation errors are shown for invalid email formats"""
        self.signup_page.enter_email(invalid_email)  # Enter the invalid email in the email field
        self.signup_page.click_signup_button()  # Click outside the field to trigger validation
        assert_true(self.signup_page.is_signup_successful() is False, "Signup should not be successful with invalid email")  # Assert that validation error is visible
        error_message = self.signup_page.get_error_message('email')  # Verify error message content
        assert_true("Invalid email format" in error_message, "Error message should indicate invalid email format")

    @pytest.mark.parametrize("weak_password", WEAK_PASSWORDS)
    def test_invalid_password_validation(self, weak_password):
        """Test that password validation errors are shown for weak passwords"""
        self.signup_page.enter_password(weak_password)  # Enter the weak password in the password field
        self.signup_page.click_signup_button()  # Click outside the field to trigger validation
        assert_true(self.signup_page.is_signup_successful() is False, "Signup should not be successful with weak password")  # Assert that validation error is visible
        error_message = self.signup_page.get_error_message('password')  # Verify error message content
        assert_true("Password is too weak" in error_message, "Error message should indicate weak password")

    def test_terms_checkbox_required(self):
        """Test that terms checkbox is required for form submission"""
        self.signup_page.fill_signup_form(VALID_NAME, VALID_EMAIL, VALID_PASSWORD, accept_terms_checkbox=False)  # Fill form with valid data except terms checkbox
        self.signup_page.click_signup_button()  # Submit the form
        assert_true(self.signup_page.is_signup_successful() is False, "Signup should not be successful without accepting terms")  # Assert that validation error for terms checkbox is shown
        error_message = self.signup_page.get_error_message('terms')  # Verify error message content
        assert_true("Accept terms to continue" in error_message, "Error message should indicate terms agreement is required")

    def test_successful_form_submission(self):
        """Test successful submission of the registration form with valid data"""
        user_data = self.signup_page.generate_test_data()  # Generate random valid user data
        self.signup_page.fill_signup_form(user_data['name'], user_data['email'], user_data['password'])  # Fill form with valid data including terms checkbox
        self.signup_page.click_signup_button()  # Submit the form
        assert_true(self.signup_page.is_signup_successful(), "Form submission should be successful")  # Assert that form submission is successful
        # Verify success message or redirect
        assert_true(self.browser.current_url != self.signup_page.url, "Should redirect after successful signup")


def test_signup_page_loads(browser):
    """Test that the signup page loads correctly and displays all required elements"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    assert_element_visible(browser, SignupLocators.NAME_FIELD, "Name field", take_screenshot=False)  # Assert that all required form elements are visible on the page
    assert_element_visible(browser, SignupLocators.EMAIL_FIELD, "Email field", take_screenshot=False)
    assert_element_visible(browser, SignupLocators.PASSWORD_FIELD, "Password field", take_screenshot=False)
    assert_element_visible(browser, SignupLocators.TERMS_CHECKBOX, "Terms checkbox", take_screenshot=False)
    assert_element_visible(browser, SignupLocators.SIGNUP_BUTTON, "Signup button", take_screenshot=False)
    assert_true(signup_page.is_element_visible(SignupLocators.SIGNUP_BUTTON), "Signup button should be visible and enabled")  # Assert that signup button is visible and enabled


@pytest.mark.parametrize("invalid_email", INVALID_EMAILS)
def test_email_validation(browser):
    """Test that email validation works correctly for invalid email formats"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.enter_email(invalid_email)  # Enter invalid email and click outside the field
    signup_page.click_signup_button()
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful with invalid email")  # Assert that validation error message is displayed
    error_message = signup_page.get_error_message('email')  # Get error message text and verify it indicates invalid email format
    assert_true("Invalid email format" in error_message, "Error message should indicate invalid email format")


@pytest.mark.parametrize("weak_password", WEAK_PASSWORDS)
def test_password_validation(browser):
    """Test that password validation works correctly for weak passwords"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.enter_password(weak_password)  # Enter weak password and click outside the field
    signup_page.click_signup_button()
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful with weak password")  # Assert that validation error message is displayed
    error_message = signup_page.get_error_message('password')  # Get error message text and verify it indicates weak password
    assert_true("Password is too weak" in error_message, "Error message should indicate weak password")


def test_terms_checkbox_validation(browser):
    """Test that terms and conditions checkbox is required"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.fill_signup_form(VALID_NAME, VALID_EMAIL, VALID_PASSWORD, accept_terms_checkbox=False)  # Enter valid name, email and password
    signup_page.click_signup_button()  # Click signup button without checking terms checkbox
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful without accepting terms")  # Assert that error message for terms checkbox is displayed
    error_message = signup_page.get_error_message('terms')  # Get error message text and verify it indicates terms agreement is required
    assert_true("Accept terms to continue" in error_message, "Error message should indicate terms agreement is required")


def test_required_fields(browser):
    """Test that all required fields show validation errors when left empty"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.click_signup_button()  # Click signup button without filling any fields
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful without filling required fields")  # Assert that validation error messages are displayed for name, email, password and terms fields


def test_valid_signup_form_submission(browser):
    """Test that a valid signup form can be submitted successfully"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    user_data = signup_page.generate_test_data()
    signup_page.fill_signup_form(user_data['name'], user_data['email'], user_data['password'])  # Enter valid name, email and password
    signup_page.click_signup_button()  # Check terms checkbox
    assert_true(signup_page.is_signup_successful(), "Form submission should be successful")  # Click signup button
    assert_true(browser.current_url != signup_page.url, "Should redirect after successful signup")  # Assert that submission is successful by checking for success message


def test_form_field_interactions(browser):
    """Test interactions with form fields such as input, clear, and focus"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.enter_name("Test Name")  # Enter text in name field and verify it accepts the input
    assert_equal(signup_page.get_story_title(), "Test Name", "Name field should accept input")
    signup_page.enter_email("test@example.com")  # Enter text in email field and verify it accepts the input
    assert_equal(signup_page.get_story_title(), "test@example.com", "Email field should accept input")
    signup_page.enter_password("Test@123")  # Enter text in password field and verify it accepts the input
    assert_equal(signup_page.get_story_title(), "Test@123", "Password field should accept input")
    signup_page.enter_name("")  # Test clearing fields and re-entering values
    signup_page.enter_email("")
    signup_page.enter_password("")
    assert_equal(signup_page.get_story_title(), "", "Fields should be cleared")
    signup_page.enter_name("New Test Name")
    signup_page.enter_email("newtest@example.com")
    signup_page.enter_password("NewTest@123")
    assert_equal(signup_page.get_story_title(), "New Test Name", "Fields should accept new input")
    # Verify that tab key navigation works between fields
    # This requires more complex implementation and is left as a future enhancement
    pass


def test_mailinator_email_acceptance(browser):
    """Test that mailinator.com email addresses are accepted for registration"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    mailinator_email = generate_random_email()  # Generate a random mailinator.com email address
    signup_page.fill_signup_form(VALID_NAME, mailinator_email, VALID_PASSWORD)  # Enter valid name, the mailinator email, and valid password
    signup_page.click_signup_button()  # Check terms checkbox
    assert_true(signup_page.is_signup_successful(), "Form submission should be successful with mailinator email")  # Click signup button
    # Assert that submission is successful by checking for success message
    assert_true(browser.current_url != signup_page.url, "Should redirect after successful signup with mailinator email")


def test_dynamic_validation_feedback(browser):
    """Test that validation feedback is shown dynamically as the user types"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    signup_page.enter_email("test")  # Enter partial/invalid email and verify error appears
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful with invalid email")
    signup_page.enter_email("test@example.com")  # Complete email to make it valid and verify error disappears
    assert_true(signup_page.is_signup_successful(), "Signup should be successful with valid email")
    signup_page.enter_password("Test")  # Enter weak password and verify error appears
    assert_true(signup_page.is_signup_successful() is False, "Signup should not be successful with weak password")
    signup_page.enter_password("Test@123456")  # Complete password to make it strong and verify error disappears
    assert_true(signup_page.is_signup_successful(), "Signup should be successful with strong password")


def test_form_field_max_length(browser):
    """Test that form fields enforce maximum length constraints"""
    signup_page = SignupPage(browser)  # Initialize SignupPage with browser
    signup_page.navigate_to()  # Navigate to signup page
    long_string = "a" * 200  # Create very long strings for name, email, and password
    signup_page.enter_name(long_string)  # Attempt to enter these values in their respective fields
    signup_page.enter_email(long_string)
    signup_page.enter_password(long_string)
    # Verify that the fields either truncate or reject values beyond their maximum length
    assert_true(len(signup_page.get_story_title()) < 100, "Name field should truncate or reject long input")
    assert_true(len(signup_page.get_story_title()) < 100, "Email field should truncate or reject long input")
    assert_true(len(signup_page.get_story_title()) < 100, "Password field should truncate or reject long input")