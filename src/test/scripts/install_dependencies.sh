#!/bin/bash
# install_dependencies.sh
# Script to install all dependencies required for the Storydoc test automation framework
# This script installs Python packages and system dependencies needed for browser automation

# Global variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
MIN_PYTHON_VERSION="3.9"
VENV_DIR="$PROJECT_ROOT/.venv"

# Function to print a formatted section header
print_section() {
    echo "========================================================================"
    echo ">>> ${1^^} <<<"
    echo "========================================================================"
}

# Function to check if a command exists in the system PATH
check_command_exists() {
    command -v "$1" >/dev/null 2>&1
    return $?
}

# Function to check if Python version meets the minimum requirement
check_python_version() {
    local python_cmd=""
    
    if check_command_exists python3; then
        python_cmd="python3"
    elif check_command_exists python; then
        python_cmd="python"
    else
        echo "Error: Python is not installed."
        return 1
    fi
    
    # Get Python version
    local version=$($python_cmd --version 2>&1 | cut -d " " -f 2)
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    
    # Extract minimum version components
    local min_major=$(echo "$MIN_PYTHON_VERSION" | cut -d. -f1)
    local min_minor=$(echo "$MIN_PYTHON_VERSION" | cut -d. -f2)
    
    # Compare versions
    if [ "$major" -gt "$min_major" ] || ([ "$major" -eq "$min_major" ] && [ "$minor" -ge "$min_minor" ]); then
        echo "Python version $version meets the minimum requirement of $MIN_PYTHON_VERSION."
        return 0
    else
        echo "Error: Python version $version does not meet the minimum requirement of $MIN_PYTHON_VERSION."
        return 1
    fi
}

# Function to create and activate a Python virtual environment
setup_virtual_environment() {
    # Check if virtualenv is installed
    if ! check_command_exists virtualenv; then
        echo "Installing virtualenv..."
        pip install virtualenv || pip3 install virtualenv
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install virtualenv."
            return 1
        fi
    fi
    
    # Create a virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in $VENV_DIR..."
        virtualenv "$VENV_DIR" -p python3
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment."
            return 1
        fi
    else
        echo "Virtual environment already exists at $VENV_DIR"
    fi
    
    # Provide activation instructions
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source $VENV_DIR/bin/activate  # For bash/zsh"
    echo "  source $VENV_DIR/bin/activate.csh  # For csh/tcsh"
    echo "  $VENV_DIR\\Scripts\\activate  # For Windows"
    echo ""
    
    return 0
}

# Function to install Python dependencies from requirements.txt
install_python_dependencies() {
    # Check if pip is installed
    local pip_cmd=""
    
    if check_command_exists pip3; then
        pip_cmd="pip3"
    elif check_command_exists pip; then
        pip_cmd="pip"
    else
        echo "Error: pip is not installed."
        return 1
    fi
    
    # Upgrade pip
    echo "Upgrading pip..."
    $pip_cmd install --upgrade pip
    
    # Check if requirements file exists
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        echo "Error: Requirements file not found at $REQUIREMENTS_FILE"
        return 1
    fi
    
    # Install dependencies from requirements.txt
    echo "Installing Python dependencies from $REQUIREMENTS_FILE..."
    $pip_cmd install -r "$REQUIREMENTS_FILE"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install Python dependencies."
        return 1
    fi
    
    echo "Python dependencies installed successfully."
    return 0
}

# Function to install system dependencies based on the detected operating system
install_system_dependencies() {
    print_section "Installing System Dependencies"
    
    # Detect OS
    local os=""
    case "$(uname -s)" in
        Linux*)
            os="Linux"
            
            # Check for specific Linux distribution
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]] || [[ "$ID_LIKE" == *"debian"* ]]; then
                    echo "Detected Debian/Ubuntu-based system."
                    
                    # Update package lists
                    echo "Updating package lists..."
                    sudo apt-get update
                    
                    # Install required packages
                    echo "Installing required packages..."
                    sudo apt-get install -y \
                        wget \
                        curl \
                        unzip \
                        xvfb \
                        libxi6 \
                        libgconf-2-4 \
                        default-jdk \
                        firefox
                    
                    # Install Chrome
                    if ! check_command_exists google-chrome; then
                        echo "Installing Google Chrome..."
                        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
                        sudo apt-get update
                        sudo apt-get install -y google-chrome-stable
                    else
                        echo "Google Chrome is already installed."
                    fi
                    
                    # Check if all installations were successful
                    if check_command_exists google-chrome && check_command_exists firefox; then
                        echo "System dependencies installed successfully."
                        return 0
                    else
                        echo "Error: Some system dependencies failed to install."
                        return 1
                    fi
                elif [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]] || [[ "$ID" == "fedora" ]] || [[ "$ID_LIKE" == *"rhel"* ]]; then
                    echo "Detected RHEL/CentOS/Fedora-based system."
                    
                    # Update package lists
                    echo "Updating package lists..."
                    sudo yum update -y
                    
                    # Install required packages
                    echo "Installing required packages..."
                    sudo yum install -y \
                        wget \
                        curl \
                        unzip \
                        xorg-x11-server-Xvfb \
                        libXi \
                        GConf2 \
                        java-11-openjdk \
                        firefox
                    
                    # Install Chrome
                    if ! check_command_exists google-chrome; then
                        echo "Installing Google Chrome..."
                        wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
                        sudo yum install -y ./google-chrome-stable_current_x86_64.rpm
                        rm google-chrome-stable_current_x86_64.rpm
                    else
                        echo "Google Chrome is already installed."
                    fi
                    
                    # Check if all installations were successful
                    if check_command_exists google-chrome && check_command_exists firefox; then
                        echo "System dependencies installed successfully."
                        return 0
                    else
                        echo "Error: Some system dependencies failed to install."
                        return 1
                    fi
                else
                    echo "Unsupported Linux distribution. Please install the following packages manually:"
                    echo "- Google Chrome"
                    echo "- Firefox"
                    echo "- Xvfb (for headless browser testing)"
                    return 1
                fi
            else
                echo "Unable to determine Linux distribution. Please install the following packages manually:"
                echo "- Google Chrome"
                echo "- Firefox"
                echo "- Xvfb (for headless browser testing)"
                return 1
            fi
            ;;
            
        Darwin*)
            os="macOS"
            echo "Detected macOS system."
            
            # Check if Homebrew is installed
            if ! check_command_exists brew; then
                echo "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                if [ $? -ne 0 ]; then
                    echo "Error: Failed to install Homebrew."
                    echo "Please install Homebrew manually: https://brew.sh/"
                    return 1
                fi
            fi
            
            # Install required packages
            echo "Installing required packages..."
            brew update
            brew install --cask google-chrome firefox
            
            # Check if all installations were successful
            if [ -d "/Applications/Google Chrome.app" ] && [ -d "/Applications/Firefox.app" ]; then
                echo "System dependencies installed successfully."
                return 0
            else
                echo "Error: Some system dependencies failed to install."
                return 1
            fi
            ;;
            
        MINGW*|MSYS*|CYGWIN*)
            os="Windows"
            echo "Detected Windows system."
            echo "Please install the following software manually:"
            echo "1. Google Chrome: https://www.google.com/chrome/"
            echo "2. Firefox: https://www.mozilla.org/firefox/"
            echo "3. Make sure Python is in your PATH"
            return 0  # Return success as we're just providing instructions
            ;;
            
        *)
            echo "Unknown operating system. Please install the following software manually:"
            echo "1. Google Chrome"
            echo "2. Firefox"
            echo "3. Python 3.9 or higher"
            return 1
            ;;
    esac
}

# Main execution

# Print welcome message
print_section "Storydoc Test Automation Framework Setup"
echo "This script will install all dependencies required for the Storydoc test automation framework."
echo ""

# Check Python version
print_section "Checking Python Version"
if ! check_python_version; then
    echo "Please install Python $MIN_PYTHON_VERSION or higher before continuing."
    exit 1
fi

# Install system dependencies
if ! install_system_dependencies; then
    echo "Warning: Some system dependencies could not be installed automatically."
    echo "You may need to install them manually to run the tests."
fi

# Set up virtual environment
print_section "Setting Up Python Virtual Environment"
if ! setup_virtual_environment; then
    echo "Error: Failed to set up virtual environment."
    exit 1
fi

# Install Python dependencies
print_section "Installing Python Dependencies"
if ! install_python_dependencies; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# Print success message
print_section "Installation Complete"
echo "All dependencies have been installed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source $VENV_DIR/bin/activate  # For bash/zsh"
echo "   $VENV_DIR\\Scripts\\activate  # For Windows"
echo ""
echo "2. Run the tests:"
echo "   cd $PROJECT_ROOT"
echo "   pytest"
echo ""
echo "For more information, refer to the project documentation."
echo ""

exit 0