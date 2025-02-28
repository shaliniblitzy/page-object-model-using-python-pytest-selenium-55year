FROM python:3.9-slim

LABEL maintainer="Storydoc Test Automation Team"

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install basic utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox
RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY src/test/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download WebDriver binaries
RUN python -c "from webdriver_manager.chrome import ChromeDriverManager; from webdriver_manager.firefox import GeckoDriverManager; ChromeDriverManager().install(); GeckoDriverManager().install()"

# Copy environment example file
COPY src/test/.env.example /app/src/test/.env.example

# Create directories for test artifacts
RUN mkdir -p /app/reports/screenshots /app/reports/logs /app/reports/html /app/reports/performance

# Copy the test framework code
COPY src/test /app/src/test

# Set the default command
CMD ["pytest", "src/test/tests", "-v", "--html=reports/html/report.html"]