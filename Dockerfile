# Optimized lightweight Python image for fast Cloud Run cold starts
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if required by python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Run the pipeline script
CMD ["python", "src/main.py"]