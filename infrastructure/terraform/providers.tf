# providers.tf
# Configuration for Terraform providers used in the Storydoc test automation infrastructure

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.1"
    }
  }
}

# AWS provider configuration
provider "aws" {
  region = var.region
}

# Random provider for generating unique values
provider "random" {}

# Null provider for resource placeholders and conditional logic
provider "null" {}

# Local provider for file operations
provider "local" {}