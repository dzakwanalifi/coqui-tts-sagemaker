# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /opt/program

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ./code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./code/ .

# Make serve script executable
RUN chmod +x serve

# Create serve symlink in PATH
RUN ln -s /opt/program/serve /usr/local/bin/serve

# SageMaker expects the serve script to be in PATH
ENV PATH="/opt/program:${PATH}"

# Default command (SageMaker will override this)
CMD ["serve"]
