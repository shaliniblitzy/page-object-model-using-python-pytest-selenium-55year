#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
from setuptools import setup, find_packages

# Current directory path
HERE = os.path.abspath(os.path.dirname(__file__))

# Package version
VERSION = '1.0.0'

# Package name
PACKAGE_NAME = 'storydoc-automation'

# Package description
DESCRIPTION = 'Page Object Model based automation framework for testing Storydoc application'

# Author information
AUTHOR = 'Storydoc QA Team'
AUTHOR_EMAIL = 'qa@storydoc.com'

# Repository URL
URL = 'https://github.com/storydoc/storydoc-automation'

def read_requirements(requirements_file='requirements.txt'):
    """
    Reads dependencies from requirements.txt file
    
    Args:
        requirements_file (str): Path to requirements file
        
    Returns:
        List[str]: List of package dependencies
    """
    requirements_path = os.path.join(HERE, requirements_file)
    if os.path.exists(requirements_path):
        with io.open(requirements_path, encoding='utf-8') as f:
            return [
                line.strip() for line in f
                if line.strip() and not line.startswith('#')
            ]
    return []

def read_long_description():
    """
    Reads long description from README.md file
    
    Returns:
        str: Content of README.md file
    """
    readme_path = os.path.join(HERE, 'README.md')
    if os.path.exists(readme_path):
        with io.open(readme_path, encoding='utf-8') as f:
            return f.read()
    return DESCRIPTION

# Read requirements and long description
REQUIREMENTS = read_requirements()
LONG_DESCRIPTION = read_long_description()

# Package classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    python_requires='>=3.9',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest>=7.3.0',             # pytest 7.3+ - Test framework
        'pytest-html>=3.2.0',        # pytest-html 3.2+ - Reporting
        'pytest-xdist>=3.3.0',       # pytest-xdist 3.3+ - Parallel execution
        'pytest-cov>=4.1.0',         # pytest-cov 4.1+ - Code coverage
        'selenium>=4.10.0',          # Selenium WebDriver 4.10+ - Browser automation
        'webdriver-manager>=4.0.0',  # webdriver-manager 4.0+ - Driver management
        'requests>=2.31.0',          # requests 2.31+ - HTTP client
        'python-dotenv>=1.0.0'       # python-dotenv 1.0+ - Configuration management
    ],
    entry_points={
        'console_scripts': [
            'storydoc-test=storydoc_automation.cli:main',
        ],
    },
    zip_safe=False,
)