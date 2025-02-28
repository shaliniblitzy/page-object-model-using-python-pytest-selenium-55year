# Use Python 3.9 slim image as the base
FROM python:3.9-slim

# Add metadata to the image
LABEL maintainer="Storydoc QA Team" description="Docker image for Storydoc POM-based test automation framework"

# Set environment variables for Python and test configuration
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HEADLESS_MODE=true BASE_URL=https://editor-staging.storydoc.com

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for Chrome and Selenium
RUN apt-get update && \
apt-get install -y \
wget \
gnupg \
curl \
unzip \
xvfb \
libxi6 \
libxtst6 \
libxrandr2 \
libasound2 \
libatk1.0-0 \
libatk-bridge2.0-0 \
libcups2 \
libdbus-1-3 \
libxcomposite1 \
libxdamage1 \
libxfixes3 \
libpango-1.0-0 \
libcairo2 \
libnspr4 \
libnss3 \
fontconfig \
font-liberation \
&& apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Install Google Chrome browser with proper key handling
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg && \
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
apt-get update && \
apt-get install -y google-chrome-stable && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Install ChromeDriver matching the Chrome browser version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1-3) && \
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
unzip chromedriver_linux64.zip && \
mv chromedriver /usr/local/bin/chromedriver && \
chmod +x /usr/local/bin/chromedriver && \
rm chromedriver_linux64.zip

# Copy requirements.txt file into the container
COPY src/test/requirements.txt /app/

# Install Python dependencies with minimum version requirements
RUN pip install --no-cache-dir --upgrade pip && \
pip install --no-cache-dir -r requirements.txt && \
pip install --no-cache-dir \
selenium>=4.10.0 \
pytest>=7.3.1 \
pytest-html>=3.2.0 \
pytest-xdist>=3.3.0 \
requests>=2.31.0 \
webdriver-manager>=4.0.0 \
python-dotenv>=1.0.0

# Copy all test files into the container
COPY src/test /app/

# Create directories for test artifacts
RUN mkdir -p /app/reports/screenshots /app/reports/html /app/reports/logs /app/reports/performance

# Make the test runner script executable
RUN chmod +x /app/scripts/run_tests.sh

# Create a volume for persisting test reports
VOLUME ["/app/reports"]

# Set the default command to run tests using the shell script
ENTRYPOINT ["/app/scripts/run_tests.sh"]

# Default arguments to generate HTML reports
CMD ["--html=/app/reports/html/report.html", "--self-contained-html"]