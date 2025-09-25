
FROM python:3.10-slim


WORKDIR /opt/program


RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*


# Install uv for blazing fast package installation
RUN pip install --no-cache-dir uv

# Copy requirements first for better caching
COPY ./code/requirements.txt .

# Use uv pip install with --index-url support
RUN uv pip install --system --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 && \
    uv pip install --system TTS==0.22.0 Flask==3.0.0 gunicorn==21.2.0


COPY ./code/ .


RUN chmod +x serve


RUN ln -s /opt/program/serve /usr/local/bin/serve


ENV PATH="/opt/program:${PATH}"


CMD ["serve"]
