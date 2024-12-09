# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git and required system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .
COPY setup.py .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Copy the rest of the application
COPY treeline/ treeline/
COPY tests/ tests/

# Create directory for outputs
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create a non-root user
RUN useradd -m treeline
RUN chown -R treeline:treeline /app
USER treeline

# Command to run the application
CMD ["python", "-m", "treeline"]
