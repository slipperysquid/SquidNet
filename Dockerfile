FROM python:3.12.8-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expose all ports
EXPOSE 5000-5002

CMD ["python3", "server.py"]