FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for modem communication
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libasound2-dev \
    portaudio19-dev \
    libusb-1.0-0-dev \
    udev \
    usb-modeswitch \
    usb-modeswitch-data \
    minicom \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs audio_temp

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"]