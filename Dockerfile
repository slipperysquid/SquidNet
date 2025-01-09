FROM python:3.12.8-slim-bookworm

# Install any needed system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    python3-xlib \
    python3-tk \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* 

RUN apt install netcat -y

WORKDIR /app

RUN mkdir payload

RUN mkdir output

COPY . /app

RUN pip install -r requirements.txt

# Expose all ports asdasd
EXPOSE 5000-5004

CMD ["python3", "server.py"]