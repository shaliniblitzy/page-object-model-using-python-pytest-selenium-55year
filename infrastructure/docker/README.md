# Docker Configuration for Storydoc Test Automation

This documentation provides detailed instructions for containerizing and running the Storydoc test automation framework using Docker. Containerization offers consistent test environments, simplified dependency management, and easy integration with CI/CD pipelines.

## Prerequisites

Before using Docker with the Storydoc test automation framework, ensure you have:

- [Docker](https://docs.docker.com/get-docker/) (version 20.10.0+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0.0+)
- Basic understanding of Docker and containerization concepts
- Access to the Storydoc test automation repository

## Docker Image

The Storydoc test automation Docker image contains:

- Python 3.9 (slim base image)
- Google Chrome browser
- Firefox ESR browser
- WebDriver binaries for Chrome and Firefox
- All Python dependencies from `requirements.txt`
- Pre-configured test directories and environment

The image is designed to run Selenium tests in both headless and non-headless modes, with support for parallel test execution and comprehensive reporting.

## Building the Docker Image

To build the Docker image locally:

```bash
# From the repository root
docker build -t storydoc-test-automation -f infrastructure/docker/Dockerfile .

# To build with no cache (for fresh builds)
docker build --no-cache -t storydoc-test-automation -f infrastructure/docker/Dockerfile .
```

The build process uses `.dockerignore` to optimize the build context by excluding unnecessary files such as:
- Git repositories
- Virtual environments
- Test reports and artifacts
- Documentation and system files

## Running Tests with Docker

You can run tests directly using the Docker image:

```bash
# Run all tests
docker run --rm -v "$(pwd)/reports:/app/reports" storydoc-test-automation

# Run specific test modules
docker run --rm -v "$(pwd)/reports:/app/reports" storydoc-test-automation \
  pytest src/test/tests/user_registration -v

# Run with environment variables
docker run --rm -v "$(pwd)/reports:/app/reports" \
  -e BASE_URL=https://editor-staging.storydoc.com \
  -e BROWSER_TYPE=chrome \
  -e HEADLESS_MODE=true \
  storydoc-test-automation
```

The `-v "$(pwd)/reports:/app/reports"` option mounts the local `reports` directory to the container, ensuring test reports are available after the container stops.

## Environment Configuration

The test framework can be configured with the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| BASE_URL | Target application URL | https://editor-staging.storydoc.com |
| BROWSER_TYPE | Browser to use (chrome/firefox) | chrome |
| HEADLESS_MODE | Run browser in headless mode | true |
| DEFAULT_TIMEOUT | Default wait timeout in seconds | 10 |
| MAILINATOR_DOMAIN | Domain for test email accounts | mailinator.com |
| TEST_USER_PASSWORD | Password for test users | Test@123 |
| TEST_USER_NAME | Name for test users | Test User |
| LOG_LEVEL | Logging verbosity | INFO |
| RETRY_COUNT | Number of retries for failed tests | 3 |
| PARALLEL_WORKERS | Number of parallel test processes | 2 |

A complete list of environment variables is available in the `.env.example` file.

## Using Docker Compose

Docker Compose allows running predefined test configurations:

```bash
# Run all tests
docker-compose -f infrastructure/docker/docker-compose.yml up storydoc-tests

# Run specific test type
docker-compose -f infrastructure/docker/docker-compose.yml up registration-tests

# Run tests in Firefox
docker-compose -f infrastructure/docker/docker-compose.yml up firefox-tests

# Run tests in parallel
docker-compose -f infrastructure/docker/docker-compose.yml up parallel-tests

# Run with custom parameters
docker-compose -f infrastructure/docker/docker-compose.yml run custom-tests 'pytest src/test/tests -k "signup and not error" -v'
```

The Docker Compose file provides several predefined services:
- `storydoc-tests`: Runs all tests
- `registration-tests`: Runs only user registration tests
- `authentication-tests`: Runs only authentication tests
- `story-creation-tests`: Runs only story creation tests
- `story-sharing-tests`: Runs only story sharing tests
- `e2e-tests`: Runs end-to-end workflow tests
- `firefox-tests`: Runs tests using Firefox browser
- `parallel-tests`: Runs tests in parallel mode
- `custom-tests`: Allows running custom test configurations

## Test Reports

Test reports are generated in the `reports` directory, which is mounted as a volume:

```
reports/
├── html/             # HTML test reports
├── logs/             # Test execution logs
├── performance/      # Performance metrics
└── screenshots/      # Failure screenshots
```

To view HTML reports, open `reports/html/report.html` in your browser after running the tests.

## CI/CD Integration

### GitHub Actions Integration

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t storydoc-test-automation -f infrastructure/docker/Dockerfile .
      
      - name: Run tests
        run: |
          docker run --rm \
            -e HEADLESS_MODE=true \
            -e RUN_HEADLESS_IN_CI=true \
            -v ${{ github.workspace }}/reports:/app/reports \
            storydoc-test-automation
      
      - name: Archive test results
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

### Jenkins Integration

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t storydoc-test-automation -f infrastructure/docker/Dockerfile .'
            }
        }
        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                      -e HEADLESS_MODE=true \
                      -v "${WORKSPACE}/reports:/app/reports" \
                      storydoc-test-automation
                '''
            }
        }
        stage('Publish Reports') {
            steps {
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/html',
                    reportFiles: 'report.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
}
```

## Resource Requirements

The following resources are recommended for optimal container performance:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| Memory | 2GB | 4GB+ |
| Storage | 1GB | 5GB |

For parallel test execution, increase resources proportionally to the number of parallel workers:
- Memory: Add ~512MB per additional worker
- CPU: Add 1 core per 2 additional workers

## Browser Support

The Docker image supports the following browsers:

| Browser | Support Level | Notes |
|---------|--------------|-------|
| Chrome | Primary | Fully supported, used by default |
| Firefox | Secondary | Supported, select with BROWSER_TYPE=firefox |

To run tests with a specific browser:

```bash
# Run with Chrome (default)
docker run --rm -v "$(pwd)/reports:/app/reports" \
  -e BROWSER_TYPE=chrome \
  storydoc-test-automation

# Run with Firefox
docker run --rm -v "$(pwd)/reports:/app/reports" \
  -e BROWSER_TYPE=firefox \
  storydoc-test-automation
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Container exits immediately | Check for syntax errors in test files or missing dependencies |
| Browser fails to start | Ensure `--no-sandbox` flag is set for headless mode |
| Permission issues with reports | Check the ownership of the mounted volume directory |
| Out of memory | Increase container memory limit or reduce parallel workers |
| Tests time out | Adjust timeout settings via environment variables |

### Viewing Container Logs

```bash
# View logs from a running container
docker logs <container_id>

# With Docker Compose
docker-compose -f infrastructure/docker/docker-compose.yml logs storydoc-tests
```

### Debugging Inside Container

```bash
# Start a shell in a new container
docker run -it --rm storydoc-test-automation /bin/bash

# Connect to a running container
docker exec -it <container_id> /bin/bash
```

## Extending the Docker Image

To extend the Docker image with additional tools or configurations:

1. Create a new Dockerfile that uses the base image:

```dockerfile
FROM storydoc-test-automation

# Add additional tools or configurations
RUN apt-get update && apt-get install -y --no-install-recommends \
    your-additional-package

# Set custom default command
CMD ["pytest", "src/test/tests/your_custom_tests", "-v"]
```

2. Build and use the extended image:

```bash
docker build -t storydoc-extended -f YourDockerfile .
docker run --rm -v "$(pwd)/reports:/app/reports" storydoc-extended
```