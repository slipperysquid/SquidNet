# Use a specific Debian version for better reproducibility
FROM python:3.12.8-slim-bookworm

# Install Wine and other dependencies for cross-compilation
RUN dpkg --add-architecture amd64 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wine64 \
    python3-dev \
    build-essential \
    python3-xlib \
    python3-tk \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN apt install netcat -y

WORKDIR /app

# Create necessary directories
RUN mkdir payload
RUN mkdir output

# Copy the application code
COPY . /app

# Install Python dependencies, including PyInstaller
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports
EXPOSE 5000-5004

# Set up Wine environment for PyInstaller
# This creates a default Wine prefix. PyInstaller will use this environment.
RUN wine64 wineboot --init

# Default command to run the server
CMD ["python3", "server.py"]