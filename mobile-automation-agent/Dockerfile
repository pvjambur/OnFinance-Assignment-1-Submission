FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # For Appium
    openjdk-17-jdk \
    # For OCR
    tesseract-ocr \
    tesseract-ocr-eng \
    # For audio (optional)
    portaudio19-dev \
    python3-pyaudio \
    # For image processing
    libgl1-mesa-glx \
    libglib2.0-0 \
    # For Redis
    redis-server \
    # Utilities
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Appium
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g appium@2.4.1 \
    && appium driver install uiautomator2

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PaddleOCR
RUN pip install --no-cache-dir paddleocr paddlepaddle

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000
EXPOSE 6379

# Health check (assuming FastAPI)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "main.py"]
