FROM python:3.12.8-slim-bookworm

WORKDIR /app

RUN mkdir payload

RUN mkdir output

COPY . /app

RUN pip install -r requirements.txt

# Expose all ports asdasd
EXPOSE 5000-5002

CMD ["python3", "server.py"]