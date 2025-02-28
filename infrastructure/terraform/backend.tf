# Terraform Backend Configuration
# 
# This file configures how and where Terraform state is stored for the test automation
# infrastructure. The Terraform state file tracks all resources managed by Terraform
# and their current configuration.
#
# For development environments, the local backend is enabled by default.
# For team environments and CI/CD integration, consider using one of the
# remote backend options (uncomment and configure as needed).
#
# Benefits of remote backends:
# - Team collaboration: Multiple team members can access the same state
# - State locking: Prevents concurrent modifications
# - CI/CD integration: Allows automation pipelines to access the state
# - Backup and versioning: Provides better data protection

terraform {
  # Local backend (default for development environments)
  # Stores state file locally on disk
  # 
  # Advantages:
  # - Simple setup, no external dependencies
  # - Good for local development and testing
  #
  # Limitations:
  # - Not suitable for team collaboration
  # - No built-in backup or versioning
  # - No state locking (risk of corruption with concurrent runs)
  backend "local" {
    path = "terraform.tfstate"
  }

  # AWS S3 Backend (recommended for AWS-based infrastructures)
  #
  # Uncomment and configure to use S3 for remote state storage.
  # This backend stores the Terraform state in an S3 bucket with
  # optional DynamoDB table for state locking.
  #
  # Required AWS permissions:
  # - S3: s3:ListBucket, s3:GetObject, s3:PutObject
  # - DynamoDB: dynamodb:GetItem, dynamodb:PutItem, dynamodb:DeleteItem
  #
  # backend "s3" {
  #   bucket         = "storydoc-terraform-state"        # S3 bucket name
  #   key            = "test-automation/terraform.tfstate" # Path in bucket
  #   region         = "us-west-2"                       # AWS region
  #   encrypt        = true                              # Encrypt state file
  #   dynamodb_table = "terraform-lock"                  # For state locking
  # }

  # Azure Storage Backend (recommended for Azure-based infrastructures)
  #
  # Uncomment and configure to use Azure Storage for remote state storage.
  # This backend stores the Terraform state in an Azure Storage container.
  #
  # Authentication methods:
  # - Environment variables (ARM_ACCESS_KEY or ARM_SAS_TOKEN)
  # - Azure CLI authentication
  # - Managed Service Identity
  #
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"         # Resource group name
  #   storage_account_name = "storydocterraformstate"     # Storage account name
  #   container_name       = "tfstate"                    # Container name
  #   key                  = "test-automation.tfstate"    # State file name
  #   use_azuread_auth     = true                         # Use Azure AD authentication
  # }

  # Google Cloud Storage Backend (recommended for GCP-based infrastructures)
  #
  # Uncomment and configure to use Google Cloud Storage for remote state storage.
  # This backend stores the Terraform state in a GCS bucket.
  #
  # Authentication methods:
  # - GOOGLE_CREDENTIALS environment variable
  # - Google Cloud SDK authentication
  #
  # backend "gcs" {
  #   bucket = "storydoc-terraform-state"              # GCS bucket name
  #   prefix = "test-automation"                       # Path prefix in bucket
  # }
}