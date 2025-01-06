# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /project

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /project/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /project/

# Ensure the entrypoint script is executable
RUN chmod +x /project/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/project/entrypoint.sh"]
