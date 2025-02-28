# Storydoc Test Automation - Terraform Infrastructure

Terraform configurations for provisioning and managing infrastructure for the Storydoc test automation framework.

## Overview

This directory contains Terraform configurations to provision the required infrastructure for running the Storydoc test automation framework. These resources include compute instances, networking, storage, and security configurations optimized for browser automation testing.

## Prerequisites

- Terraform CLI (v1.0.0 or newer)
- AWS CLI configured with appropriate credentials
- IAM permissions to create required resources
- Basic knowledge of Terraform and AWS

## Directory Structure

- `main.tf` - Main infrastructure configuration
- `variables.tf` - Input variable declarations
- `outputs.tf` - Output definitions
- `providers.tf` - Provider configuration
- `backend.tf` - State backend configuration

## Provisioned Resources

This Terraform configuration provisions the following AWS resources:

- VPC with public subnet
- Security Groups for test runner access
- EC2 instance for test execution
- EBS volume for test artifacts and logs
- IAM role and policies for resource access
- S3 bucket for test reports (optional)

## Configuration

The infrastructure can be customized through variables defined in `variables.tf`. Key configurations include:

| Variable | Description | Default |
|----------|-------------|---------|
| project_name | Name of the project | storydoc-automation |
| environment | Deployment environment | dev |
| region | AWS region | us-west-2 |
| instance_type | EC2 instance type | t3.medium |
| storage_size | EBS volume size (GB) | 30 |
| python_version | Python version | 3.9 |
| chrome_driver_version | Chrome WebDriver version | latest |
| firefox_driver_version | Firefox WebDriver version | latest |

## Getting Started

### Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### Plan the Deployment

```bash
terraform plan -out=tfplan
```

### Apply the Configuration

```bash
terraform apply tfplan
```

### Destroy Resources When Done

```bash
terraform destroy
```

## Customization

To customize the deployment, create a `terraform.tfvars` file with your variable overrides:

```hcl
project_name = "my-storydoc-tests"
environment = "staging"
instance_type = "t3.large"
storage_size = 50
```

Alternatively, set variables via environment variables prefixed with `TF_VAR_`:

```bash
export TF_VAR_environment="staging"
export TF_VAR_instance_type="t3.large"
terraform apply
```

## Remote State

For team environments, it's recommended to use remote state storage:

1. Uncomment the backend configuration in `backend.tf`
2. Update the bucket name and key path
3. Run `terraform init` again to migrate state

## Post-Provisioning Setup

After the infrastructure is provisioned:

1. Connect to the EC2 instance via SSH:
   ```bash
   ssh -i your-key.pem ec2-user@$(terraform output -raw instance_public_ip)
   ```

2. Clone the test repository:
   ```bash
   git clone https://github.com/your-org/storydoc-automation.git
   ```

3. Install dependencies:
   ```bash
   cd storydoc-automation
   pip install -r requirements.txt
   ```

4. Configure the test environment:
   ```bash
   cp src/test/.env.example src/test/.env
   # Edit .env with appropriate values
   ```

## CI/CD Integration

To integrate with CI/CD pipelines:

### GitHub Actions

```yaml
name: Infrastructure Deployment

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: hashicorp/setup-terraform@v1
        with:
          terraform_version: 1.0.0
      - name: Terraform Init
        run: terraform -chdir=infrastructure/terraform init
      - name: Terraform Validate
        run: terraform -chdir=infrastructure/terraform validate
      - name: Terraform Plan
        run: terraform -chdir=infrastructure/terraform plan
```

## Best Practices

1. Use workspaces for managing multiple environments:
   ```bash
   terraform workspace new staging
   terraform workspace select staging
   terraform apply
   ```

2. Lock the Terraform provider versions for stability

3. Use variables for all configurable parameters

4. Tag all resources for better organization and cost tracking

5. Regularly update provider versions for security patches

## Performance Optimization

For optimal test execution performance:

1. Choose compute-optimized instance types (e.g., c5.large) for better browser automation performance

2. Ensure the instance is in the same region as the application being tested to reduce latency

3. For parallel test execution, increase the instance size or provision multiple instances

## Security Considerations

1. Restrict SSH access to specific IP ranges

2. Use IAM roles with least privilege principle

3. Enable VPC flow logs for network monitoring

4. Store sensitive data (like API keys) using AWS Secrets Manager

5. Encrypt EBS volumes and S3 buckets

## Troubleshooting

### Common Issues

- **Permission Errors**: Ensure IAM credentials have sufficient permissions

- **Resource Limits**: Check AWS service quotas if resource creation fails

- **State Lock**: If state is locked, use `terraform force-unlock` with caution

- **Network Connectivity**: Ensure security groups allow necessary traffic

### Debugging

Enable verbose logging with:

```bash
export TF_LOG=DEBUG
terraform apply
```

## Cost Management

To manage infrastructure costs:

1. Destroy resources when not in use

2. Use Spot Instances for non-critical testing

3. Schedule test runs during off-peak hours

4. Set up AWS Budget alerts

5. Right-size the EC2 instances based on actual resource usage