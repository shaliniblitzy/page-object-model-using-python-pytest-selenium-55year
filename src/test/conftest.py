import pytest  # pytest 7.3+
import os  # built-in
import sys  # built-in
import logging  # built-in
from datetime import datetime  # built-in
import pathlib  # built-in
import random  # built-in
from typing import Dict  # built-in
from typing import Any  # built-in

# Import internal utilities and configurations
from .utilities.driver_factory import DriverFactory  # src/test/utilities/driver_factory.py
from .utilities.config_manager import get_config  # src/test/utilities/config_manager.py
from .utilities.config_manager import initialize  # src/test/utilities/config_manager.py
from .utilities.config_manager import create_directories  # src/test/utilities/config_manager.py
from .utilities.email_helper import EmailHelper  # src/test/utilities/email_helper.py
from .utilities.screenshot_manager import ScreenshotManager  # src/test/utilities/screenshot_manager.py
from .utilities.logger import initialize_logger  # src/test/utilities/logger.py
from .utilities.logger import log_info  # src/test/utilities/logger.py
from .utilities.logger import log_error  # src/test/utilities/logger.py
from .fixtures.browser_fixtures import browser  # src/test/fixtures/browser_fixtures.py
from .fixtures.browser_fixtures import browser_session  # src/test/fixtures/browser_fixtures.py
from .fixtures.browser_fixtures import chrome_browser  # src/test/fixtures/browser_fixtures.py
from .fixtures.browser_fixtures import firefox_browser  # src/test/fixtures/browser_fixtures.py
from .fixtures.browser_fixtures import edge_browser  # src/test/fixtures/browser_fixtures.py
from .fixtures.user_fixtures import test_user  # src/test/fixtures/user_fixtures.py
from .fixtures.user_fixtures import authenticated_user  # src/test/fixtures/user_fixtures.py
from pytest import FixtureRequest
from pytest import TestReport
from pytest import Session
from pytest import Item
from pytest import Collector

# Define global constants
PYTEST_REPORT_HEADER = "Storydoc Automation Framework"
ENV_FILE = os.getenv('ENV_FILE', '.env')
ENVIRONMENT = os.getenv('TEST_ENVIRONMENT', 'staging')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize screenshot_manager (will be properly initialized in pytest_configure)
screenshot_manager = None  # Initialized in pytest_configure


def pytest_configure(config: pytest.Config) -> None:
    """Initial configuration hook for pytest that sets up the test environment"""
    # Initialize configuration
    initialize(ENV_FILE, ENVIRONMENT)

    # Create necessary directories
    create_directories()

    # Configure logger
    initialize_logger()

    # Initialize screenshot_manager global variable
    global screenshot_manager
    screenshot_manager = ScreenshotManager()

    # Set pytest terminal reporter header
    config.option.reportheader = PYTEST_REPORT_HEADER

    # Log test session start information
    log_info("Test session started")


def pytest_unconfigure(config: pytest.Config) -> None:
    """Cleanup hook that runs after all tests have completed"""
    # Quit all WebDriver instances
    DriverFactory.quit_all_drivers()

    # Log test session end information
    log_info("Test session ended")


def pytest_sessionstart(session: pytest.Session) -> None:
    """Hook that runs at the start of the test session"""
    # Log test session start with timestamp
    log_info(f"Test session started at: {datetime.now()}")

    # Set session start time in session.config
    session.config._session_start_time = time.time()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Hook that runs at the end of the test session"""
    # Calculate test session duration
    duration = time.time() - session.config._session_start_time

    # Log test session end with duration and exit status
    log_info(f"Test session finished in {duration:.2f} seconds with exit status: {exitstatus}")


def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Collector) -> bool:
    """Hook that runs the test protocol for a single test"""
    # Store test start time
    item._start_time = time.time()
    return False  # Return False to let pytest handle the test protocol


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Hook that runs before each test setup"""
    # Log test setup start with test name
    log_info(f"Setting up test: {item.name}")

    # Store test start time
    item._start_time = time.time()


def pytest_runtest_teardown(item: pytest.Item) -> None:
    """Hook that runs after each test teardown"""
    # Calculate test duration if _start_time exists
    if hasattr(item, '_start_time'):
        duration = time.time() - item._start_time

        # Log test teardown completion with duration
        log_info(f"Tearing down test: {item.name} (Duration: {duration:.2f} seconds)")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Hook that processes test reports"""
    if report.when == 'call':
        if report.failed:
            # Capture screenshot if driver available
            try:
                driver = report.node.funcargs['browser']
                global screenshot_manager
                screenshot_manager.capture_failure_screenshot(driver, report.node.name, report.longreprtext)
            except Exception as e:
                log_error(f"Failed to capture screenshot: {str(e)}")

            # Log test failure with detailed error information
            log_error(f"Test failed: {report.node.name}\n{report.longreprtext}")
        elif report.passed:
            # Log test success
            log_info(f"Test passed: {report.node.name}")
        elif report.skipped:
            # Log test skip with reason
            log_info(f"Test skipped: {report.node.name}\nReason: {report.longreprtext}")


@pytest.fixture(scope='session')
def email_helper() -> EmailHelper:
    """Fixture that provides an EmailHelper instance for email verification"""
    # Create an instance of EmailHelper
    email_helper = EmailHelper()

    # Log email helper initialization
    log_info("EmailHelper fixture initialized")

    # Yield EmailHelper instance to tests
    yield email_helper

    # No cleanup needed


@pytest.fixture(scope='session')
def screenshot_helper() -> ScreenshotManager:
    """Fixture that provides a ScreenshotManager instance for capturing screenshots"""
    global screenshot_manager
    if screenshot_manager is None:
        screenshot_manager = ScreenshotManager()
    log_info("ScreenshotManager fixture initialized")
    yield screenshot_manager


@pytest.fixture
def generate_random_email(email_helper: EmailHelper) -> str:
    """Fixture that provides a random email address for testing"""
    def _generate_random_email(prefix: str = None) -> str:
        # Generate random email using EmailHelper.generate_email_address(prefix)
        email = email_helper.generate_email_address(prefix)

        # Log generated email address
        log_info(f"Generated random email: {email}")

        # Return email address to test
        return email
    yield _generate_random_email


@pytest.fixture
def test_name(request: FixtureRequest) -> str:
    """Fixture that provides the current test name"""
    # Extract test name from request.node.name
    test_name = request.node.name

    # Clean up test name by removing special characters
    test_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in test_name)

    # Log test name
    log_info(f"Current test name: {test_name}")

    # Return test name to test
    yield test_name


@pytest.fixture(scope='session')
def base_url() -> str:
    """Fixture that provides the base URL for the application under test"""
    # Get base URL from configuration
    base_url = get_config('base_url')

    # Log base URL value
    log_info(f"Base URL: {base_url}")

    # Return base URL to tests
    yield base_url

# Re-export browser fixtures from browser_fixtures.py
@pytest.fixture(scope='function')
def browser(request):
    return browser(request)

@pytest.fixture(scope='session')
def browser_session(request):
    return browser_session(request)

@pytest.fixture(scope='function')
def chrome_browser(request):
    return chrome_browser(request)

@pytest.fixture(scope='function')
def firefox_browser(request):
    return firefox_browser(request)

@pytest.fixture(scope='function')
def edge_browser(request):
    return edge_browser(request)

# Re-export test user data fixture
@pytest.fixture(scope='function')
def test_user(request):
    return test_user(request)

# Re-export authenticated user fixture
@pytest.fixture(scope='function')
def authenticated_user(browser, test_user):
    return authenticated_user(browser, test_user)