# Dockerfile for caddy-helper CLI tool
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run helper
ENTRYPOINT ["python", "helper.py"]
