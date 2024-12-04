FROM python:3.10-slim

# Install chromium dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver=130.0.6723.91-1~deb12u1 \
    chromium-common=130.0.6723.91-1~deb12u1 \
    chromium=130.0.6723.91-1~deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the working directory
WORKDIR /app

# Set the environment variable for the Chrome binary location
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run the main application
CMD ["python3", "-u", "main.py"]
