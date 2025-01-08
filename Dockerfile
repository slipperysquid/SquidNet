FROM python:3.12.8-slim-bookworm

# Install any needed system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    python3-xlib \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir payload

RUN mkdir output

COPY . /app

RUN pip install -r requirements.txt

# Expose all ports asdasd
EXPOSE 5000-5002

CMD ["python3", "server.py"]