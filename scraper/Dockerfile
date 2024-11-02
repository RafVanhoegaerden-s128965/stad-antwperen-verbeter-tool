FROM python:3.10-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install selenium bs4

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Set the environment variable for the Chrome binary location
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run the main application
CMD ["python3", "main.py"]
