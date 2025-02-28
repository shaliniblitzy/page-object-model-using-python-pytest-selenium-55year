#!/bin/bash
# setup_environment.sh
# Script to set up the testing environment for the Storydoc application test automation framework

# Global variables
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(dirname "$(dirname "$SCRIPT_DIR")")
TEST_DIR=$PROJECT_ROOT/src/test
DEFAULT_ENV="staging"
ENV_FILE=$TEST_DIR/.env
ENV_EXAMPLE_FILE=$TEST_DIR/.env.example
REPORTS_DIR=$TEST_DIR/reports
SCREENSHOTS_DIR=$REPORTS_DIR/screenshots
LOGS_DIR=$REPORTS_DIR/logs
PERFORMANCE_DIR=$REPORTS_DIR/performance
PYTHON_MIN_VERSION="3.9"
VENV_NAME="storydoc-venv"

# Function to print a formatted header
print_header() {
    echo "========================================================================"
    echo "            Storydoc Test Automation Framework Setup                    "
    echo "========================================================================"
}

# Function to print a section header
print_section() {
    echo "--------------------------------------------------------------------"
    echo "  $1"
    echo "--------------------------------------------------------------------"
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check for Python 3.9+
    python_cmd=""
    if command -v python3 &>/dev/null; then
        python_cmd="python3"
    elif command -v python &>/dev/null; then
        python_cmd="python"
    else
        echo "Error: Python is not installed."
        return 1
    fi
    
    # Check Python version
    python_version=$($python_cmd --version 2>&1 | cut -d " " -f 2)
    python_major=$(echo "$python_version" | cut -d. -f1)
    python_minor=$(echo "$python_version" | cut -d. -f2)
    
    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 9 ]); then
        echo "Error: Python version $python_version is not supported. Please install Python 3.9 or higher."
        return 1
    fi
    
    echo "Python $python_version is installed."
    
    # Check for pip
    pip_cmd=""
    if command -v pip3 &>/dev/null; then
        pip_cmd="pip3"
    elif command -v pip &>/dev/null; then
        pip_cmd="pip"
    else
        echo "Error: pip is not installed."
        return 1
    fi
    
    echo "pip is installed."
    
    return 0
}

# Function to set up virtual environment
setup_virtual_environment() {
    print_section "Setting Up Virtual Environment"
    
    # Check if virtual environment already exists
    if [ -d "$VENV_NAME" ]; then
        echo "Virtual environment already exists at $VENV_NAME"
    else
        echo "Creating virtual environment..."
        
        python_cmd=""
        if command -v python3 &>/dev/null; then
            python_cmd="python3"
        else
            python_cmd="python"
        fi
        
        $python_cmd -m venv $VENV_NAME
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment."
            return 1
        fi
        
        echo "Virtual environment created at $VENV_NAME"
    fi
    
    # Provide activation instructions
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source $VENV_NAME/bin/activate  # For bash/zsh"
    echo "  source $VENV_NAME/bin/activate.csh  # For csh/tcsh"
    echo "  $VENV_NAME\\Scripts\\activate.bat  # For Windows cmd"
    echo "  $VENV_NAME\\Scripts\\Activate.ps1  # For Windows PowerShell"
    echo ""
    
    # Upgrade pip
    echo "Upgrading pip..."
    if [ -f "$VENV_NAME/bin/pip" ]; then
        $VENV_NAME/bin/pip install --upgrade pip
    elif [ -f "$VENV_NAME/Scripts/pip.exe" ]; then
        $VENV_NAME/Scripts/pip.exe install --upgrade pip
    else
        echo "Warning: Could not find pip in the virtual environment."
        echo "You may need to activate the environment manually and upgrade pip."
    fi
    
    return 0
}

# Function to install dependencies
install_dependencies() {
    print_section "Installing Dependencies"
    
    # Check if install_dependencies.sh exists
    dependency_script="$SCRIPT_DIR/install_dependencies.sh"
    if [ ! -f "$dependency_script" ]; then
        echo "Error: install_dependencies.sh script not found at $dependency_script"
        return 1
    fi
    
    # Make sure the script is executable
    chmod +x "$dependency_script"
    
    # Execute the install_dependencies.sh script
    echo "Executing install_dependencies.sh..."
    source "$dependency_script"
    local result=$?
    
    if [ $result -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        return 1
    fi
    
    echo "Dependencies installed successfully."
    return 0
}

# Function to set up environment variables
setup_environment_variables() {
    local env_name=$1
    print_section "Setting Up Environment Variables"
    
    # Validate environment name
    case "$env_name" in
        development|staging|production|ci)
            # Valid environment name
            ;;
        *)
            echo "Error: Invalid environment name '$env_name'. Valid values are: development, staging, production, ci."
            return 1
            ;;
    esac
    
    # Create .env file from .env.example if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE_FILE" ]; then
            echo "Creating .env file from .env.example..."
            cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
        else
            echo "Error: .env.example file not found at $ENV_EXAMPLE_FILE"
            return 1
        fi
    fi
    
    # Set TEST_ENVIRONMENT in .env file - compatible with both GNU and BSD sed
    if grep -q "^TEST_ENVIRONMENT=" "$ENV_FILE"; then
        # Replace existing TEST_ENVIRONMENT
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS (BSD sed)
            sed -i '' "s/^TEST_ENVIRONMENT=.*/TEST_ENVIRONMENT=$env_name/" "$ENV_FILE"
        else
            # Linux (GNU sed)
            sed -i "s/^TEST_ENVIRONMENT=.*/TEST_ENVIRONMENT=$env_name/" "$ENV_FILE"
        fi
    else
        # Add TEST_ENVIRONMENT
        echo "TEST_ENVIRONMENT=$env_name" >> "$ENV_FILE"
    fi
    
    echo "Environment variables set up for '$env_name' environment."
    
    return 0
}

# Function to create necessary directories
create_directories() {
    print_section "Creating Directories"
    
    # Create reports directory
    if [ ! -d "$REPORTS_DIR" ]; then
        echo "Creating reports directory at $REPORTS_DIR..."
        mkdir -p "$REPORTS_DIR"
    else
        echo "Reports directory already exists at $REPORTS_DIR"
    fi
    
    # Create screenshots directory
    if [ ! -d "$SCREENSHOTS_DIR" ]; then
        echo "Creating screenshots directory at $SCREENSHOTS_DIR..."
        mkdir -p "$SCREENSHOTS_DIR"
    else
        echo "Screenshots directory already exists at $SCREENSHOTS_DIR"
    fi
    
    # Create logs directory
    if [ ! -d "$LOGS_DIR" ]; then
        echo "Creating logs directory at $LOGS_DIR..."
        mkdir -p "$LOGS_DIR"
    else
        echo "Logs directory already exists at $LOGS_DIR"
    fi
    
    # Create performance directory
    if [ ! -d "$PERFORMANCE_DIR" ]; then
        echo "Creating performance directory at $PERFORMANCE_DIR..."
        mkdir -p "$PERFORMANCE_DIR"
    else
        echo "Performance directory already exists at $PERFORMANCE_DIR"
    fi
    
    echo "Directories created successfully."
    
    return 0
}

# Function to set up WebDriver executables
setup_browser_drivers() {
    print_section "Setting Up Browser Drivers"
    
    # Check if webdriver-manager is installed
    pip_cmd=""
    if command -v pip3 &>/dev/null; then
        pip_cmd="pip3"
    else
        pip_cmd="pip"
    fi
    
    # Install webdriver-manager if not already installed
    if ! $pip_cmd show webdriver-manager &>/dev/null; then
        echo "Installing webdriver-manager..."
        $pip_cmd install webdriver-manager
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install webdriver-manager."
            return 1
        fi
    else
        echo "webdriver-manager is already installed."
    fi
    
    # Run a Python script to trigger driver downloads
    echo "Downloading browser drivers..."
    python_cmd=""
    if command -v python3 &>/dev/null; then
        python_cmd="python3"
    else
        python_cmd="python"
    fi
    
    $python_cmd -c "
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

try:
    # Trigger download of ChromeDriver
    ChromeDriverManager().install()
    print('ChromeDriver downloaded successfully.')
except Exception as e:
    print(f'Error downloading ChromeDriver: {e}')
    exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download browser drivers."
        return 1
    fi
    
    echo "Browser drivers set up successfully."
    
    return 0
}

# Function to validate the setup
validate_setup() {
    print_section "Validating Setup"
    
    # Check if directories exist
    local all_valid=true
    
    if [ ! -d "$REPORTS_DIR" ]; then
        echo "Warning: Reports directory does not exist at $REPORTS_DIR"
        all_valid=false
    fi
    
    if [ ! -d "$SCREENSHOTS_DIR" ]; then
        echo "Warning: Screenshots directory does not exist at $SCREENSHOTS_DIR"
        all_valid=false
    fi
    
    if [ ! -d "$LOGS_DIR" ]; then
        echo "Warning: Logs directory does not exist at $LOGS_DIR"
        all_valid=false
    fi
    
    if [ ! -d "$PERFORMANCE_DIR" ]; then
        echo "Warning: Performance directory does not exist at $PERFORMANCE_DIR"
        all_valid=false
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        echo "Warning: .env file does not exist at $ENV_FILE"
        all_valid=false
    fi
    
    if [ "$all_valid" = true ]; then
        echo "Validation successful! All required directories and files are set up."
        return 0
    else
        echo "Validation failed! Some required directories or files are missing."
        return 1
    fi
}

# Main function
main() {
    local env_name=$1
    
    # Set default environment if not provided
    if [ -z "$env_name" ]; then
        env_name=$DEFAULT_ENV
    fi
    
    # Print header
    print_header
    
    # Check prerequisites
    check_prerequisites
    if [ $? -ne 0 ]; then
        echo "Error: Prerequisites check failed. Please install the required software and try again."
        exit 1
    fi
    
    # Set up virtual environment
    setup_virtual_environment
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set up virtual environment."
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        exit 1
    fi
    
    # Set up environment variables
    setup_environment_variables "$env_name"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set up environment variables."
        exit 1
    fi
    
    # Create directories
    create_directories
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create directories."
        exit 1
    fi
    
    # Set up browser drivers
    setup_browser_drivers
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set up browser drivers."
        exit 1
    fi
    
    # Validate setup
    validate_setup
    local validation_result=$?
    
    # Print final message
    if [ $validation_result -eq 0 ]; then
        echo ""
        echo "========================================================================"
        echo "  Setup completed successfully!"
        echo "  You can now run the tests using: "
        echo "  1. Activate the virtual environment:"
        echo "     source $VENV_NAME/bin/activate  # For bash/zsh"
        echo "     source $VENV_NAME/bin/activate.csh  # For csh/tcsh"
        echo "     $VENV_NAME\\Scripts\\activate.bat  # For Windows cmd"
        echo "     $VENV_NAME\\Scripts\\Activate.ps1  # For Windows PowerShell"
        echo "  2. Run the tests:"
        echo "     cd $PROJECT_ROOT"
        echo "     pytest"
        echo "========================================================================"
        return 0
    else
        echo ""
        echo "========================================================================"
        echo "  Setup completed with warnings. Please check the output above."
        echo "========================================================================"
        return 1
    fi
}

# Execute main function with command line arguments
main "$@"
exit $?