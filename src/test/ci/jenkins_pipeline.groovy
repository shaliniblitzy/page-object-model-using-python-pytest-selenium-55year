pipeline {
    agent any
    
    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        ansiColor('xterm')
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_NAME = 'storydoc-venv'
        TEST_REPORTS_DIR = 'reports'
        SCREENSHOTS_DIR = 'screenshots'
        MAILINATOR_API_KEY = credentials('mailinator-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Checked out repository"
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh """
                    # Create and activate virtual environment
                    python${PYTHON_VERSION} -m venv ${VENV_NAME}
                    . ${VENV_NAME}/bin/activate
                    
                    # Upgrade pip and install dependencies
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Verify installation
                    pip list
                """
                
                echo "Environment setup completed"
            }
        }
        
        stage('Lint & Static Analysis') {
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Run code quality checks
                    flake8 .
                    black --check .
                    mypy .
                """
                
                echo "Linting and static analysis completed"
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Create directories for reports and screenshots if they don't exist
                    mkdir -p ${TEST_REPORTS_DIR}
                    mkdir -p ${SCREENSHOTS_DIR}
                    
                    # Run unit tests with pytest
                    python -m pytest tests/unit --html=${TEST_REPORTS_DIR}/unit-tests-report.html --self-contained-html --junitxml=${TEST_REPORTS_DIR}/unit-tests-results.xml -v
                """
                
                echo "Unit tests completed"
            }
            post {
                always {
                    junit "${TEST_REPORTS_DIR}/unit-tests-results.xml"
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Run integration tests with pytest
                    python -m pytest tests/integration --html=${TEST_REPORTS_DIR}/integration-tests-report.html --self-contained-html --junitxml=${TEST_REPORTS_DIR}/integration-tests-results.xml -v
                """
                
                echo "Integration tests completed"
            }
            post {
                always {
                    junit "${TEST_REPORTS_DIR}/integration-tests-results.xml"
                }
                failure {
                    archiveArtifacts artifacts: "${SCREENSHOTS_DIR}/**/*", allowEmptyArchive: true
                }
            }
        }
        
        stage('End-to-End Tests') {
            environment {
                // Set environment variables for the tests
                TEST_BASE_URL = 'https://editor-staging.storydoc.com'
                TEST_EMAIL_DOMAIN = 'mailinator.com'
                TEST_HEADLESS_MODE = 'true'
                TEST_DEFAULT_TIMEOUT = '10'
            }
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Run E2E tests with pytest, parallel execution with 4 processes
                    python -m pytest tests/e2e -n 4 --html=${TEST_REPORTS_DIR}/e2e-tests-report.html --self-contained-html --junitxml=${TEST_REPORTS_DIR}/e2e-tests-results.xml -v
                """
                
                echo "End-to-End tests completed"
            }
            post {
                always {
                    junit "${TEST_REPORTS_DIR}/e2e-tests-results.xml"
                }
                failure {
                    archiveArtifacts artifacts: "${SCREENSHOTS_DIR}/**/*", allowEmptyArchive: true
                }
            }
        }
        
        stage('SLA Verification') {
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Run SLA verification script to check against defined performance requirements
                    # - User Registration: < 30 seconds
                    # - User Authentication: < 20 seconds
                    # - Story Creation: < 45 seconds
                    # - Story Sharing: < 60 seconds
                    # - Full Workflow: < 3 minutes
                    python -m scripts.verify_sla ${TEST_REPORTS_DIR}/e2e-tests-results.xml
                """
                
                echo "SLA verification completed"
            }
        }
        
        stage('Performance Analysis') {
            steps {
                sh """
                    . ${VENV_NAME}/bin/activate
                    
                    # Generate performance analysis report
                    python -m scripts.generate_performance_report ${TEST_REPORTS_DIR}
                """
                
                echo "Performance analysis completed"
            }
        }
    }
    
    post {
        always {
            // Archive test reports
            archiveArtifacts artifacts: "${TEST_REPORTS_DIR}/**/*", allowEmptyArchive: true
            
            // Clean up environment
            sh """
                # Clean up virtual environment if needed
                if [ -d "${VENV_NAME}" ]; then
                    rm -rf ${VENV_NAME}
                fi
            """
            
            echo "Pipeline execution completed"
        }
        
        success {
            sendNotification('SUCCESS')
        }
        
        failure {
            sendNotification('FAILURE')
        }
        
        unstable {
            sendNotification('UNSTABLE')
        }
    }
}

/**
 * Send notification about build status
 *
 * @param status The build status (SUCCESS, FAILURE, UNSTABLE)
 */
def sendNotification(String status) {
    def subject = "Build ${env.BUILD_NUMBER} - ${status}: ${env.JOB_NAME}"
    def body = """
        <p>Build: <b>${env.BUILD_NUMBER}</b></p>
        <p>Status: <b>${status}</b></p>
        <p>Job: ${env.JOB_NAME}</p>
        <p>Build URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
        <p>Console Output: <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></p>
        <p>Test Reports: <a href="${env.BUILD_URL}artifact/${TEST_REPORTS_DIR}">${env.BUILD_URL}artifact/${TEST_REPORTS_DIR}</a></p>
    """
    
    emailext (
        subject: subject,
        body: body,
        recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
        mimeType: 'text/html'
    )
    
    echo "Notification sent with status: ${status}"
}