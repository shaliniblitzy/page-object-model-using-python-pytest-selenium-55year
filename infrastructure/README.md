# Storydoc Test Automation - Infrastructure

Infrastructure components and configurations for the Storydoc test automation framework. This directory contains configurations for various deployment options including Docker, Kubernetes, and Terraform-based cloud deployments.

## Overview

The Storydoc test automation framework can be deployed in various environments depending on your testing needs. This infrastructure directory provides configurations for:

- Docker containers for local development and CI/CD pipelines
- Kubernetes deployments for scalable test execution
- Terraform configurations for AWS-based infrastructure

Choose the appropriate option based on your specific requirements for test execution, scalability, and integration needs.

## Infrastructure Options

### Docker

The Docker-based setup provides a lightweight, portable environment for running tests locally or in CI/CD pipelines. It includes all necessary dependencies including browsers, WebDrivers, and the Python environment.

### Kubernetes

The Kubernetes configuration enables scalable test execution in a containerized environment, allowing for parallel test execution and resource optimization. Suitable for teams requiring consistent, scalable test infrastructure.

### Terraform

The Terraform configuration provisions cloud-based infrastructure (AWS) for running tests, including compute instances, networking, and storage resources. Ideal for teams with complex testing requirements or those already utilizing cloud infrastructure.

## Getting Started

Choose the appropriate infrastructure option based on your needs:

### Local Development (Docker)

```bash
# Navigate to Docker directory
cd infrastructure/docker

# Build the Docker image
docker build -t storydoc-automation .

# Run tests using Docker Compose
docker-compose up
```

### CI/CD Pipeline Integration

Refer to the .github/workflows directory for GitHub Actions configurations that can be adapted for your CI/CD platform.

### Kubernetes Deployment

```bash
# Navigate to Kubernetes directory
cd infrastructure/kubernetes

# Apply Kubernetes configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### AWS Infrastructure (Terraform)

```bash
# Navigate to Terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

## Resource Requirements

### Docker/Local Environment

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| Memory | 4GB | 8GB |
| Storage | 1GB | 5GB |
| Network | Internet connection | Stable broadband |

### Kubernetes Cluster

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Nodes | 1 | 3+ |
| CPU per node | 2 cores | 4+ cores |
| Memory per node | 4GB | 8GB+ |
| Storage | 10GB | 20GB+ |

### AWS (Terraform)

| Resource | Specification | Purpose |
|----------|--------------|----------|
| EC2 Instance | t3.medium (2 vCPU, 4GB RAM) | Test execution |
| EBS Volume | 30GB | Test artifacts and logs |
| S3 Bucket | Standard | Test reports storage |

## Configuration

Each infrastructure option has its own configuration files and parameters. Refer to the README.md file in each subdirectory for detailed configuration instructions:

- [Docker Configuration](./docker/README.md)
- [Kubernetes Configuration](./kubernetes/README.md)
- [Terraform Configuration](./terraform/README.md)

## CI/CD Integration

The test automation framework is designed to integrate with CI/CD pipelines. Sample configurations are provided for GitHub Actions, but can be adapted for other CI/CD platforms like Jenkins, GitLab CI, or Azure DevOps.

Key integration points:

1. Environment setup (Python, browsers, WebDrivers)
2. Dependency installation
3. Test execution with appropriate parameters
4. Test report generation and artifact storage
5. Notification of test results

Refer to the [.github/workflows/test.yml](../.github/workflows/test.yml) file for a complete example of CI/CD integration.

## Performance Considerations

To optimize test execution performance:

1. Use appropriate resource allocations based on test suite size
2. Enable parallel test execution where possible
3. Use headless browser mode for CI/CD environments
4. Implement appropriate timeouts and wait strategies
5. Consider test data management to minimize setup time

For large test suites, consider using Kubernetes with multiple nodes or larger AWS instances to distribute test execution load.

## Security Considerations

When deploying test infrastructure, consider these security best practices:

1. Use secure credential management (environment variables, secrets)
2. Implement network security (firewalls, security groups)
3. Apply principle of least privilege for service accounts
4. Regularly update dependencies and base images
5. Encrypt sensitive data and communications
6. Implement appropriate access controls for test reports

## Troubleshooting

Common infrastructure issues and solutions:

### Docker Issues

- **WebDriver connection failures**: Ensure host network mode or correct port mapping
- **Browser crashes**: Increase container memory allocation
- **Permission issues**: Check volume mount permissions

### Kubernetes Issues

- **Pod failures**: Check pod logs and events
- **Resource limitations**: Adjust resource requests/limits
- **Networking issues**: Verify service and network policies

### Terraform/AWS Issues

- **Provisioning failures**: Check IAM permissions
- **Instance connectivity**: Verify security group rules
- **Performance issues**: Consider instance type upgrades

## Maintenance

Regular maintenance tasks for test infrastructure:

1. Update base images and dependencies
2. Review and optimize resource allocations
3. Clean up test artifacts and reports
4. Monitor usage patterns and costs
5. Apply security patches
6. Update configurations for new test requirements