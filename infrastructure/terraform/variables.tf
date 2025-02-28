# Infrastructure configuration variables for the Storydoc test automation framework
# These variables define all configurable inputs required for provisioning the infrastructure

# Project and environment information
variable "project_name" {
  type        = string
  default     = "storydoc-automation"
  description = "Used for naming and tagging resources"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment identifier for resource naming and tagging"
}

# AWS infrastructure settings
variable "region" {
  type        = string
  default     = "us-west-2"
  description = "AWS region where resources will be created"
}

variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "Instance type for the test runner EC2 instance"
}

variable "storage_size" {
  type        = number
  default     = 30
  description = "Size in GB for the test runner's EBS volume"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the Virtual Private Cloud"
}

variable "subnet_cidr" {
  type        = string
  default     = "10.0.1.0/24"
  description = "CIDR block for the subnet within the VPC"
}

# Test automation framework configuration
variable "chrome_driver_version" {
  type        = string
  default     = "latest"
  description = "Version of Chrome WebDriver to install, or 'latest' for auto-detection"
}

variable "firefox_driver_version" {
  type        = string
  default     = "latest"
  description = "Version of Firefox WebDriver to install, or 'latest' for auto-detection"
}

variable "python_version" {
  type        = string
  default     = "3.9"
  description = "Python version to install on the test runner environment"
}

# Test-specific configuration
variable "mailinator_domain" {
  type        = string
  default     = "mailinator.com"
  description = "Mailinator domain for email verification testing"
}

variable "mailinator_api_key" {
  type        = string
  default     = ""
  description = "Optional API key for accessing Mailinator premium features"
  sensitive   = true
}

variable "storydoc_app_url" {
  type        = string
  default     = "https://editor-staging.storydoc.com"
  description = "URL of the Storydoc application for test automation"
}

variable "test_timeout" {
  type        = number
  default     = 10
  description = "Default timeout in seconds for test operations"
}

variable "headless_mode" {
  type        = bool
  default     = true
  description = "Run browsers in headless mode when true"
}

variable "parallel_executions" {
  type        = number
  default     = 2
  description = "Number of tests that can run in parallel"
}