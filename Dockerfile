FROM python:3.12.8-slim-bookworm

# Install any needed system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    python3-xlib \
    python3-tk \
    netcat-traditional \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/* 

# Install Docker's official GPG key and repo
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list

# Install Docker CLI from Docker's repo
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Buildx
RUN mkdir -p /usr/lib/docker/cli-plugins/ \
    && curl -SL https://github.com/docker/buildx/releases/download/v0.10.3/buildx-v0.10.3.linux-amd64 -o /usr/lib/docker/cli-plugins/docker-buildx \
    && chmod +x /usr/lib/docker/cli-plugins/docker-buildx

WORKDIR /app

RUN mkdir payload

RUN mkdir output

COPY . /app

RUN pip install -r requirements.txt

# Expose all ports asdasd
EXPOSE 5000-5004

CMD ["python3", "server.py"]