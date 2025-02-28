import pytest  # pytest 7.3+
import time
from typing import Dict  # built-in

from src.test.fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from src.test.pages.signup_page import SignupPage  # src/test/pages/signup_page.py
from src.test.pages.signin_page import SigninPage  # src/test/pages/signin_page.py
from src.test.pages.dashboard_page import DashboardPage  # src/test/pages/dashboard_page.py
from src.test.pages.story_editor_page import StoryEditorPage  # src/test/pages/story_editor_page.py
from src.test.pages.share_dialog_page import ShareDialogPage  # src/test/pages/share_dialog_page.py
from src.test.utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from src.test.utilities.random_data_generator import generate_random_email  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_password  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_name  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_story_title  # src/test/utilities/random_data_generator.py
from src.test.utilities.random_data_generator import generate_random_story_content  # src/test/utilities/random_data_generator.py
from src.test.utilities.logger import logger  # src/test/utilities/logger.py
from src.test.config.sla_config import SLA_TIMES  # src/test/config/sla_config.py
from src.test.utilities.performance_monitor import PerformanceMonitor  # src/test/utilities/performance_monitor.py

TIMEOUT = 60  # Default timeout for waiting operations in seconds
TEMPLATE_NAME = "Basic"  # Default template name for story creation


class TestCompleteWorkflow:
    """Test class for validating the complete end-to-end workflow of the Storydoc application with performance monitoring"""

    def __init__(self):
        """Default constructor"""
        pass

    def setup_method(self, browser):
        """Set up test environment and initialize test data before each test method

        Args:
            browser: WebDriver fixture
        """
        # Assign browser instance to self.driver
        self.driver = browser

        # Initialize page objects with self.driver
        self.signup_page = SignupPage(self.driver)
        self.signin_page = SigninPage(self.driver)
        self.dashboard_page = DashboardPage(self.driver)
        self.story_editor_page = StoryEditorPage(self.driver)
        self.share_dialog_page = ShareDialogPage(self.driver)

        # Initialize EmailHelper
        self.email_helper = EmailHelper()

        # Initialize PerformanceMonitor
        self.performance_monitor = PerformanceMonitor()

        # Generate test user data (email, password, name)
        self.user_email = generate_random_email()
        self.user_password = generate_random_password()
        self.user_name = generate_random_name()

        # Generate test story data (title, content)
        self.story_title = generate_random_story_title()
        self.story_content = generate_random_story_content()

        # Generate recipient email for sharing
        self.recipient_email = generate_random_email()

        # Log test setup information
        logger.info("Test setup completed")

    def teardown_method(self):
        """Clean up resources after each test method

        Args:
            self: TestCompleteWorkflow
        """
        # Log test teardown
        logger.info("Test teardown started")

        # Any required cleanup operations
        # Note: WebDriver cleanup handled by browser fixture
        logger.info("Test teardown completed")

    @pytest.mark.registration
    def test_user_registration(self):
        """Test user registration process with mailinator email and performance tracking"""
        logger.info("Starting user registration test")

        # Start performance timer for registration
        start_time = time.time()

        # Initialize SignupPage with self.driver
        signup_page = SignupPage(self.driver)

        # Navigate to signup page
        signup_page.navigate_to()

        # Enter user name, email and password
        signup_page.enter_name(self.user_name)
        signup_page.enter_email(self.user_email)
        signup_page.enter_password(self.user_password)

        # Accept terms and conditions
        signup_page.accept_terms()

        # Click signup button
        signup_page.click_signup_button()

        # Assert signup is successful
        assert signup_page.is_signup_successful(), "Signup was not successful"

        # Verify registration email received
        assert signup_page.verify_registration_email(self.user_email), "Verification email not received"

        # Stop performance timer for registration
        registration_time = time.time() - start_time

        # Assert registration completed within SLA time
        assert registration_time <= SLA_TIMES["REGISTRATION"], f"Registration time {registration_time} exceeds SLA {SLA_TIMES['REGISTRATION']}"

        # Log registration performance metrics
        logger.info(f"Registration completed in {registration_time} seconds")

        # Return the registered user data for use in other tests
        return {
            "email": self.user_email,
            "password": self.user_password,
            "name": self.user_name
        }

    @pytest.mark.authentication
    def test_user_authentication(self):
        """Test user authentication process with registered user and performance tracking"""
        logger.info("Starting user authentication test")

        # Ensure user is registered (call test_user_registration if needed)
        if self.user_email is None:
            self.test_user_registration()

        # Start performance timer for authentication
        start_time = time.time()

        # Initialize SigninPage with self.driver
        signin_page = SigninPage(self.driver)

        # Navigate to signin page
        signin_page.navigate_to()

        # Enter registered email and password
        signin_page.enter_email(self.user_email)
        signin_page.enter_password(self.user_password)

        # Click signin button
        signin_page.click_signin_button()

        # Assert signin is successful
        assert signin_page.is_signin_successful(), "Signin was not successful"

        # Verify dashboard is loaded
        assert self.dashboard_page.is_loaded(), "Dashboard not loaded"

        # Stop performance timer for authentication
        authentication_time = time.time() - start_time

        # Assert authentication completed within SLA time
        assert authentication_time <= SLA_TIMES["AUTHENTICATION"], f"Authentication time {authentication_time} exceeds SLA {SLA_TIMES['AUTHENTICATION']}"

        # Log authentication performance metrics
        logger.info(f"Authentication completed in {authentication_time} seconds")

    @pytest.mark.story_creation
    def test_story_creation(self):
        """Test creating a new story with a specific template and performance tracking"""
        logger.info("Starting story creation test")

        # Ensure user is authenticated (call test_user_authentication if needed)
        if self.user_email is None:
            self.test_user_authentication()

        # Start performance timer for story creation
        start_time = time.time()

        # Click create story button on dashboard
        self.dashboard_page.click_create_story_button()

        # Verify story editor is loaded
        assert self.story_editor_page.is_loaded(), "Story editor not loaded"

        # Enter story title
        self.story_editor_page.enter_story_title(self.story_title)

        # Select a template
        self.story_editor_page.select_template(TEMPLATE_NAME)

        # Optionally enter story content
        # self.story_editor_page.input_content(self.story_content)

        # Save the story
        self.story_editor_page.save_story()

        # Assert story is saved successfully
        assert self.story_editor_page.is_story_saved(), "Story was not saved"

        # Verify story appears on dashboard
        assert self.dashboard_page.is_story_present(self.story_title), "Story not present on dashboard"

        # Stop performance timer for story creation
        story_creation_time = time.time() - start_time

        # Assert story creation completed within SLA time
        assert story_creation_time <= SLA_TIMES["STORY_CREATION"], f"Story creation time {story_creation_time} exceeds SLA {SLA_TIMES['STORY_CREATION']}"

        # Log story creation performance metrics
        logger.info(f"Story creation completed in {story_creation_time} seconds")

    @pytest.mark.story_sharing
    def test_story_sharing(self):
        """Test sharing a story with another user via email and performance tracking"""
        logger.info("Starting story sharing test")

        # Ensure story is created (call test_story_creation if needed)
        if self.user_email is None:
            self.test_story_creation()

        # Start performance timer for story sharing
        start_time = time.time()

        # Open the story for editing if not already open
        # self.dashboard_page.open_story(self.story_title)

        # Click share button in story editor
        share_dialog = self.story_editor_page.click_share_button()

        # Enter recipient email address
        share_dialog.enter_recipient_email(self.recipient_email)

        # Optionally enter personal message
        # share_dialog.enter_personal_message("Check out this awesome story!")

        # Click share button on dialog
        share_dialog.click_share_button()

        # Assert sharing is successful
        assert share_dialog.is_sharing_successful(), "Story sharing was not successful"

        # Verify sharing email received by recipient
        assert share_dialog.verify_sharing_email(self.recipient_email), "Sharing email not received"

        # Extract shared story link from email
        sharing_link = share_dialog.get_sharing_link(self.recipient_email)

        # Navigate to the shared story link
        self.driver.get(sharing_link)

        # Verify shared story is accessible
        assert "Storydoc" in self.driver.title, "Shared story not accessible"

        # Stop performance timer for story sharing
        story_sharing_time = time.time() - start_time

        # Assert story sharing completed within SLA time
        assert story_sharing_time <= SLA_TIMES["STORY_SHARING"], f"Story sharing time {story_sharing_time} exceeds SLA {SLA_TIMES['STORY_SHARING']}"

        # Log story sharing performance metrics
        logger.info(f"Story sharing completed in {story_sharing_time} seconds")

    @pytest.mark.e2e
    def test_complete_workflow(self):
        """Test the complete end-to-end workflow from registration to story sharing"""
        logger.info("Starting complete workflow test")

        # Start performance timer for complete workflow
        start_time = time.time()

        # 1. Register a new user (test_user_registration)
        registration_data = self.test_user_registration()

        # 2. Sign in with the registered user (test_user_authentication)
        self.test_user_authentication()

        # 3. Create a new story (test_story_creation)
        self.test_story_creation()

        # 4. Share the created story (test_story_sharing)
        self.test_story_sharing()

        # Stop performance timer for complete workflow
        complete_workflow_time = time.time() - start_time

        # Assert complete workflow completed within SLA time
        assert complete_workflow_time <= SLA_TIMES["FULL_WORKFLOW"], f"Complete workflow time {complete_workflow_time} exceeds SLA {SLA_TIMES['FULL_WORKFLOW']}"

        # Log complete workflow performance metrics
        logger.info(f"Complete workflow completed in {complete_workflow_time} seconds")

        # Assert that all steps in the workflow completed successfully
        assert registration_data is not None, "User registration failed"
        assert self.signin_page.is_signin_successful(), "User authentication failed"
        assert self.story_editor_page.is_story_saved(), "Story creation failed"
        assert self.share_dialog_page.is_sharing_successful(), "Story sharing failed"

    @pytest.mark.resilience
    @pytest.mark.flaky(reruns=2)
    def test_workflow_with_retry(self):
        """Test the complete workflow with automatic retry mechanism for resilience"""
        logger.info("Starting workflow with retry test")
        # Call test_complete_workflow with retry capability
        # If any step fails, retry the entire workflow up to specified number of times
        # Log number of attempts made
        # Assert that workflow eventually completed successfully
        pass

    @pytest.mark.sla
    @pytest.mark.parametrize("operation", ["registration", "authentication", "story_creation", "story_sharing", "complete_workflow"])
    def test_sla_compliance(self, operation):
        """Test that all operations meet the defined SLA requirements"""
        logger.info(f"Starting SLA compliance test for operation: {operation}")
        # Perform the specified operation (calling appropriate test method)
        # Record execution time
        # Retrieve SLA time limit for the operation
        # Assert that operation completed within SLA time limit
        # Log SLA compliance results
        pass