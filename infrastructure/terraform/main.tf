# Main Terraform configuration file for Storydoc test automation framework
# Provisions the infrastructure required to run browser automation tests

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC for test infrastructure
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

# Subnet for the test runner instance
resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-subnet"
  })
}

# Security group for the test runner instance
resource "aws_security_group" "test_runner_sg" {
  name   = "${var.project_name}-${var.environment}-sg"
  vpc_id = aws_vpc.main.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-sg"
  })
}

# IAM role for the test runner instance
resource "aws_iam_role" "test_runner_role" {
  name = "${var.project_name}-${var.environment}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# Instance profile for attaching the IAM role to the EC2 instance
resource "aws_iam_instance_profile" "test_runner_profile" {
  name = "${var.project_name}-${var.environment}-profile"
  role = aws_iam_role.test_runner_role.name
}

# Attach S3 access policy to the IAM role
resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.test_runner_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# S3 bucket for storing test artifacts
resource "aws_s3_bucket" "test_artifacts" {
  bucket = "${var.project_name}-${var.environment}-artifacts"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-artifacts"
  })
}

# EC2 instance for the test runner
resource "aws_instance" "test_runner" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.test_runner_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.test_runner_profile.name

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3 python3-pip
    pip3 install selenium pytest pytest-html webdriver-manager requests python-dotenv
  EOF

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-test-runner"
  })
}

# Internet Gateway for the VPC to allow internet access
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-igw"
  })
}

# Route table for internet access
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-rt"
  })
}

# Associate the route table with the subnet
resource "aws_route_table_association" "main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

# Elastic IP for the test runner to ensure it has a static public IP
resource "aws_eip" "test_runner" {
  instance = aws_instance.test_runner.id
  vpc      = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-eip"
  })
}