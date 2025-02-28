import pytest  # pytest 7.3+
import time  # built-in
import logging  # built-in

# Internal imports
from src.test.pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.fixtures.user_fixtures import test_user  # src/test/fixtures/user_fixtures.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.random_data_generator import generate_random_email  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_password  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_name  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_test_user_data  # src/test/utilities/random_data_generator.py
from src.test.utilities.assertion_helper import assert_true  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_element_visible  # src/test/utilities/assertion_helper.py
from src.test.utilities.assertion_helper import assert_url_contains  # src/test/utilities/assertion_helper.py
from src.test.config.timeout_config import EMAIL_DELIVERY_TIMEOUT  # src/test/config/timeout_config.py

# Initialize logger
logger = logging.getLogger(__name__)


def test_valid_user_registration_with_auto_generated_data(browser):
    """Test user registration with automatically generated user data"""
    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Generate random test user data (name, email, password)
    user_data = signup_page.generate_test_data()

    # Log test start with generated email
    logger.info(f"Starting test: test_valid_user_registration_with_auto_generated_data with email {user_data['email']}")

    # Call complete_registration_with_verification with generated data
    registration_result = signup_page.complete_registration_with_verification(
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password']
    )

    # Assert registration was successful
    assert_true(registration_result['success'], "Registration was not successful", driver=browser)

    # Assert verification email was received
    assert_true(registration_result['verification_success'], "Verification email was not received", driver=browser)

    # Assert email verification was completed successfully
    assert_true(registration_result['message'] == 'Registration and verification completed successfully',
                "Email verification was not completed successfully", driver=browser)

    # Log successful test completion
    logger.info("Test completed successfully")


def test_valid_user_registration_with_fixture_data(browser, test_user):
    """Test user registration using test user fixture data"""
    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Log test start with user data from fixture
    logger.info(f"Starting test: test_valid_user_registration_with_fixture_data with email {test_user['email']}")

    # Call complete_signup with user data from fixture
    signup_success = signup_page.complete_signup(
        name=test_user['name'],
        email=test_user['email'],
        password=test_user['password']
    )

    # Assert signup was successful
    assert_true(signup_success, "Signup was not successful", driver=browser)

    # Assert verification email was received
    assert_true(signup_page.verify_registration_email(test_user['email']), "Verification email not received", driver=browser)

    # Get verification link from email
    verification_link = signup_page.get_verification_link(test_user['email'])

    # Complete email verification by accessing the link
    verification_success = signup_page.complete_email_verification(test_user['email'])

    # Assert email verification was completed successfully
    assert_true(verification_success, "Email verification was not completed successfully", driver=browser)

    # Log successful test completion
    logger.info("Test completed successfully")


def test_user_registration_email_verification(browser):
    """Test the email verification part of the registration process"""
    # Initialize SignupPage and EmailHelper
    signup_page = SignupPage(browser)
    email_helper = EmailHelper()

    # Generate a random email address
    email = generate_random_email()

    # Generate random user data with the specific email
    user_data = {
        'name': generate_random_name(),
        'email': email,
        'password': generate_random_password()
    }

    # Complete signup process with generated data
    signup_success = signup_page.complete_signup(
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password']
    )

    # Assert signup was successful
    assert_true(signup_success, "Signup was not successful", driver=browser)

    # Wait for verification email with timeout
    message = email_helper.wait_for_email(
        email,
        "Welcome to Storydoc",
        timeout=EMAIL_DELIVERY_TIMEOUT
    )

    # Assert verification email was received
    assert_true(message is not None, "Verification email not received", driver=browser)

    # Extract verification link from email
    verification_link = email_helper.extract_verification_link(message)

    # Navigate to verification link
    browser.get(verification_link)

    # Assert verification process completed successfully
    assert_element_visible(browser, (".success-message"), "Success Message", driver=browser)

    # Assert redirect to success page or dashboard
    assert_url_contains(browser, "dashboard", driver=browser)


@pytest.mark.parametrize('email_domain', ['mailinator.com', 'mailinater.com', 'mailinator2.com'])
def test_user_registration_with_different_email_domains(browser, email_domain):
    """Test user registration with different Mailinator email domains"""
    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Generate random user data with email using the specified domain
    user_data = {
        'name': generate_random_name(),
        'email': generate_random_email(domain=email_domain),
        'password': generate_random_password()
    }

    # Complete signup process with generated data
    signup_success = signup_page.complete_signup(
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password']
    )

    # Assert signup was successful
    assert_true(signup_success, "Signup was not successful", driver=browser)

    # Assert verification email was received
    assert_true(signup_page.verify_registration_email(user_data['email']), "Verification email not received", driver=browser)

    # Complete email verification
    verification_success = signup_page.complete_email_verification(user_data['email'])

    # Assert verification was successful
    assert_true(verification_success, "Email verification was not completed successfully", driver=browser)

    # Log successful test completion
    logger.info("Test completed successfully")


def test_complete_registration_flow_sla(browser):
    """Test the complete registration flow meets Service Level Agreements for timing"""
    # Initialize SignupPage with browser instance
    signup_page = SignupPage(browser)

    # Record start time
    start_time = time.time()

    # Generate random test user data
    user_data = signup_page.generate_test_data()

    # Complete full registration process including verification
    signup_page.complete_registration_with_verification(
        name=user_data['name'],
        email=user_data['email'],
        password=user_data['password']
    )

    # Record end time and calculate duration
    end_time = time.time()
    duration = end_time - start_time

    # Assert that registration process completed within SLA time limit (60 seconds)
    assert_true(duration <= 60, f"Registration process took {duration} seconds, exceeding SLA of 60 seconds", driver=browser)

    # Log performance metrics
    logger.info(f"Registration process completed in {duration} seconds")


@pytest.mark.registration
@pytest.mark.web
class TestValidRegistration:
    """Test class for validating successful user registration scenarios"""

    def __init__(self):
        """Default constructor"""
        pass

    def setup_method(self, browser):
        """Setup method that runs before each test"""
        # Store reference to browser instance
        self.browser = browser

        # Initialize SignupPage with browser
        self.signup_page = SignupPage(browser)

        # Initialize EmailHelper
        self.email_helper = EmailHelper()

        # Log test setup completed
        logger.info("Test setup completed")

    def teardown_method(self):
        """Teardown method that runs after each test"""
        # Log test teardown
        logger.info("Test teardown")

        # Perform any required cleanup
        pass

    def test_successful_user_registration(self):
        """Test basic successful user registration with verification"""
        # Generate random user data
        user_data = self.signup_page.generate_test_data()

        # Navigate to signup page
        self.signup_page.navigate_to()

        # Complete signup with generated data
        self.signup_page.complete_signup(user_data['name'], user_data['email'], user_data['password'])

        # Assert signup was successful
        assert_true(self.signup_page.is_signup_successful(), "Signup was not successful", driver=self.browser)

        # Verify registration email was received
        assert_true(self.signup_page.verify_registration_email(user_data['email']), "Verification email not received", driver=self.browser)

        # Complete email verification
        verification_success = self.signup_page.complete_email_verification(user_data['email'])

        # Assert registration process was successful end-to-end
        assert_true(verification_success, "Email verification was not completed successfully", driver=self.browser)

    def test_registration_email_verification_link(self):
        """Test that registration email contains a valid verification link"""
        # Generate random user data
        user_data = self.signup_page.generate_test_data()

        # Complete signup with generated data
        self.signup_page.complete_signup(user_data['name'], user_data['email'], user_data['password'])

        # Wait for verification email
        message = self.email_helper.wait_for_email(
            user_data['email'],
            "Welcome to Storydoc",
            timeout=EMAIL_DELIVERY_TIMEOUT
        )

        # Extract verification link from email
        verification_link = self.email_helper.extract_verification_link(message)

        # Assert that verification link is not empty
        assert_true(verification_link is not None, "Verification link is empty", driver=self.browser)

        # Assert that verification link contains expected URL patterns
        assert_true("verify" in verification_link or "confirm" in verification_link, "Verification link does not contain expected URL patterns", driver=self.browser)

        # Navigate to verification link
        self.browser.get(verification_link)

        # Assert verification completes successfully
        assert_element_visible(self.browser, (".success-message"), "Success Message", driver=self.browser)

    def test_registration_redirects_to_dashboard(self):
        """Test that after successful registration and verification user is redirected to dashboard"""
        # Generate random user data
        user_data = self.signup_page.generate_test_data()

        # Complete signup process
        self.signup_page.complete_signup(user_data['name'], user_data['email'], user_data['password'])

        # Verify and follow verification link
        message = self.email_helper.wait_for_email(
            user_data['email'],
            "Welcome to Storydoc",
            timeout=EMAIL_DELIVERY_TIMEOUT
        )

        # Extract verification link from email
        verification_link = self.email_helper.extract_verification_link(message)

        # Navigate to verification link
        self.browser.get(verification_link)

        # Assert URL contains 'dashboard'
        assert_url_contains(self.browser, "dashboard", driver=self.browser)

        # Assert dashboard elements are visible
        assert_element_visible(self.browser, (".dashboard-nav"), "Dashboard Navigation", driver=self.browser)