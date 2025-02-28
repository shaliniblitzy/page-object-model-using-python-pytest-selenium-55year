# Terraform outputs for the Storydoc test automation framework

output "storydoc_test_url" {
  description = "The URL of the Storydoc staging environment for testing"
  value       = "https://editor-staging.storydoc.com"
}

output "environment_variables" {
  description = "Environment variables needed for test execution, to be used in .env files or CI/CD configuration"
  value = {
    BASE_URL                = "https://editor-staging.storydoc.com"
    DEFAULT_TIMEOUT         = "10"
    HEADLESS_MODE           = "false"
    TEST_EMAIL_DOMAIN       = "mailinator.com"
    TEST_PASSWORD           = "Test@123"
    TEST_USER_NAME          = "Test User"
    SCREENSHOT_DIR          = "reports/screenshots"
    REPORT_DIR              = "reports/html"
    RETRY_ATTEMPTS          = "3"
    LOG_LEVEL               = "INFO"
    EXECUTION_ENVIRONMENT   = "staging"
  }
}

output "webdriver_config" {
  description = "Configuration for WebDriver setup to ensure consistent browser automation"
  value = {
    chrome_driver_version  = "114.0.5735.90"
    firefox_driver_version = "0.33.0"
    default_browser        = "chrome"
    implicit_wait_time     = 5
    page_load_timeout      = 30
    script_timeout         = 30
    headless_mode_ci       = true
  }
}

output "docker_image" {
  description = "Docker image reference for containerized test execution"
  value       = "python:3.9-slim"
}

output "test_reports_path" {
  description = "Path for storing test reports and artifacts"
  value       = "./reports"
}

output "mailinator_config" {
  description = "Configuration for Mailinator email testing service"
  value = {
    api_endpoint = "https://api.mailinator.com/api/v2"
    test_domain  = "mailinator.com"
    inbox_check_interval = 5
    email_wait_timeout   = 60
    token_name           = "MAILINATOR_API_KEY"
  }
}