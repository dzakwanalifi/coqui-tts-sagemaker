# Gunakan base image Ubuntu yang lebih ringan untuk development
FROM ubuntu:22.04

# Set environment variables
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies sistem (versi ringan)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 sebagai default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Salin file requirements
COPY ./code/requirements.txt /opt/program/requirements.txt

# Install library Python
WORKDIR /opt/program
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi
COPY ./code /opt/program/

# Make serve script executable and add to PATH
RUN chmod +x /opt/program/serve && \
    ln -s /opt/program/serve /usr/local/bin/serve

# Set env var untuk SageMaker
ENV SAGEMAKER_PROGRAM inference.py
ENV PATH="/opt/program:${PATH}"
