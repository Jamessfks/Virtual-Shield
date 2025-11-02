# ==================================
# Multi-stage Dockerfile for AI Screenshot Detector
# ==================================

# Stage 1: Python Backend
FROM python:3.11-slim as python-backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY config.py .
COPY api_server_v2.py .
COPY services/ services/

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5001

# Run backend server
CMD ["python", "api_server_v2.py"]
