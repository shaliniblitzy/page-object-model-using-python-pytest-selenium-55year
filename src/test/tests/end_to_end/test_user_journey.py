import pytest  # pytest 7.3+
import time
import random

# Internal imports
from src.test.pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.driver_factory import DriverFactory  # src/test/utilities/driver_factory.py
from src.test.utilities.logger import logger  # src/test/utilities.logger.py

TIMEOUT = 60  # Default timeout for waiting operations


class TestUserJourney:
    """
    Test class that implements end-to-end tests for the complete user journey through the Storydoc application
    """

    @pytest.fixture(scope='function')
    def setup(self):
        """
        Test fixture to set up the test environment before each test
        """
        # Initialize WebDriver instance using DriverFactory
        self.driver = DriverFactory.get_driver()
        logger.info("WebDriver instance initialized")

        # Initialize page objects (SignupPage, SigninPage, DashboardPage, StoryEditorPage, ShareDialogPage)
        self.signup_page = SignupPage(self.driver)
        self.signin_page = SigninPage(self.driver)
        self.dashboard_page = DashboardPage(self.driver)
        self.story_editor_page = StoryEditorPage(self.driver)
        self.share_dialog_page = ShareDialogPage(self.driver)
        logger.info("Page objects initialized")

        # Initialize EmailHelper for email verification
        self.email_helper = EmailHelper()
        logger.info("EmailHelper initialized")

        # Generate test data (user_email, user_password, user_name, story_title, recipient_email)
        self.user_email = self.email_helper.generate_email_address()
        self.user_password = "Test@123"
        self.user_name = f"Test User {random.randint(1000, 9999)}"
        self.story_title = f"Test Story {random.randint(1000, 9999)}"
        self.recipient_email = self.email_helper.generate_email_address()
        logger.info(
            f"Test data generated: user_email={self.user_email}, user_name={self.user_name}, story_title={self.story_title}, recipient_email={self.recipient_email}"
        )

        # Yield to test execution
        yield

        # After test execution, quit the WebDriver instance
        self.driver.quit()
        logger.info("WebDriver instance quit")

    @pytest.mark.registration
    def test_user_registration(self, setup):
        """
        Test user registration process with mailinator email
        """
        # Navigate to signup page
        self.signup_page.navigate_to()
        logger.info("Navigated to signup page")

        # Enter user name, email and password
        self.signup_page.enter_name(self.user_name)
        self.signup_page.enter_email(self.user_email)
        self.signup_page.enter_password(self.user_password)
        logger.info("Entered user details")

        # Accept terms and conditions
        self.signup_page.accept_terms()
        logger.info("Accepted terms and conditions")

        # Click signup button
        self.signup_page.click_signup_button()
        logger.info("Clicked signup button")

        # Verify successful registration
        assert self.signup_page.is_signup_successful(), "Registration failed"
        logger.info("Registration successful")

        # Check Mailinator for verification email
        assert self.email_helper.verify_email_received(self.user_email, "Welcome to Storydoc"), "Verification email not received"
        logger.info("Verification email received")

        # Assert that registration was successful
        assert True, "User registration test completed"

    @pytest.mark.authentication
    def test_user_authentication(self, setup):
        """
        Test user authentication process with registered user
        """
        # Navigate to signin page
        self.signin_page.navigate_to()
        logger.info("Navigated to signin page")

        # Enter registered email and password
        self.signin_page.enter_email(self.user_email)
        self.signin_page.enter_password(self.user_password)
        logger.info("Entered user credentials")

        # Click signin button
        self.signin_page.click_signin_button()
        logger.info("Clicked signin button")

        # Verify successful authentication
        assert self.signin_page.is_signin_successful(), "Authentication failed"
        logger.info("Authentication successful")

        # Verify dashboard is loaded
        assert self.dashboard_page.is_loaded(), "Dashboard not loaded"
        logger.info("Dashboard loaded")

        # Assert that authentication was successful
        assert True, "User authentication test completed"

    @pytest.mark.story_creation
    def test_story_creation(self, setup):
        """
        Test creating a new story with a specific template
        """
        # Ensure user is authenticated (call test_user_authentication if needed)
        self.test_user_authentication(setup)
        logger.info("User authenticated")

        # Navigate to dashboard
        assert self.dashboard_page.is_loaded(), "Dashboard not loaded"
        logger.info("Navigated to dashboard")

        # Click create story button
        self.dashboard_page.click_create_story_button()
        logger.info("Clicked create story button")

        # Verify story editor is loaded
        assert self.story_editor_page.is_loaded(), "Story editor not loaded"
        logger.info("Story editor loaded")

        # Enter story title
        self.story_editor_page.enter_story_title(self.story_title)
        logger.info("Entered story title")

        # Select a template
        self.story_editor_page.select_template("Basic")
        logger.info("Selected a template")

        # Save the story
        self.story_editor_page.save_story()
        logger.info("Saved the story")

        # Verify story is saved successfully
        assert self.story_editor_page.is_story_saved(), "Story not saved"
        logger.info("Story saved successfully")

        # Assert that story creation was successful
        assert True, "Story creation test completed"

    @pytest.mark.story_sharing
    def test_story_sharing(self, setup):
        """
        Test sharing a story with another user via email
        """
        # Ensure story is created (call test_story_creation if needed)
        self.test_story_creation(setup)
        logger.info("Story created")

        # Click share button on story editor
        self.story_editor_page.click_share_button()
        logger.info("Clicked share button")

        # Enter recipient email address
        self.share_dialog_page.enter_recipient_email(self.recipient_email)
        logger.info(f"Entered recipient email: {self.recipient_email}")

        # Click share button on dialog
        self.share_dialog_page.click_share_button()
        logger.info("Clicked share button on dialog")

        # Verify sharing is successful
        assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"
        logger.info("Story sharing successful")

        # Check Mailinator for sharing email
        assert self.email_helper.verify_email_received(self.recipient_email, "Story shared with you"), "Sharing email not received"
        logger.info("Sharing email received")

        # Extract shared story link from email
        message = self.email_helper.wait_for_email(self.recipient_email, "Story shared with you")
        sharing_link = self.email_helper.extract_verification_link(message)

        # Navigate to the shared story link
        self.driver.get(sharing_link)
        logger.info("Navigated to shared story link")

        # Verify shared story is accessible
        assert "Storydoc" in self.driver.title, "Shared story not accessible"
        logger.info("Shared story accessible")

        # Assert that story sharing was successful
        assert True, "Story sharing test completed"

    @pytest.mark.e2e
    def test_end_to_end_user_journey(self, setup):
        """
        Test the complete end-to-end user journey from registration to story sharing
        """
        # Register a new user (using steps from test_user_registration)
        self.signup_page.navigate_to()
        self.signup_page.enter_name(self.user_name)
        self.signup_page.enter_email(self.user_email)
        self.signup_page.enter_password(self.user_password)
        self.signup_page.accept_terms()
        self.signup_page.click_signup_button()
        assert self.signup_page.is_signup_successful(), "Registration failed"
        assert self.email_helper.verify_email_received(self.user_email, "Welcome to Storydoc"), "Verification email not received"
        logger.info("User registered successfully")

        # Sign in with the newly registered user (using steps from test_user_authentication)
        self.signin_page.navigate_to()
        self.signin_page.enter_email(self.user_email)
        self.signin_page.enter_password(self.user_password)
        self.signin_page.click_signin_button()
        assert self.signin_page.is_signin_successful(), "Authentication failed"
        assert self.dashboard_page.is_loaded(), "Dashboard not loaded"
        logger.info("User signed in successfully")

        # Create a new story (using steps from test_story_creation)
        self.dashboard_page.click_create_story_button()
        assert self.story_editor_page.is_loaded(), "Story editor not loaded"
        self.story_editor_page.enter_story_title(self.story_title)
        self.story_editor_page.select_template("Basic")
        self.story_editor_page.save_story()
        assert self.story_editor_page.is_story_saved(), "Story not saved"
        logger.info("Story created successfully")

        # Share the created story (using steps from test_story_sharing)
        self.story_editor_page.click_share_button()
        self.share_dialog_page.enter_recipient_email(self.recipient_email)
        self.share_dialog_page.click_share_button()
        assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"
        assert self.email_helper.verify_email_received(self.recipient_email, "Story shared with you"), "Sharing email not received"
        message = self.email_helper.wait_for_email(self.recipient_email, "Story shared with you")
        sharing_link = self.email_helper.extract_verification_link(message)
        self.driver.get(sharing_link)
        assert "Storydoc" in self.driver.title, "Shared story not accessible"
        logger.info("Story shared successfully")

        # Verify the entire workflow completes successfully
        assert True, "End-to-end user journey test completed"