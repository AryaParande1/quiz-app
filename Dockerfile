# Use lightweight official Python runtime base image
FROM python:3.11-slim

# Set environment variables for optimized container execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_ENV=Production

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and test files
COPY . /app/

# Create a non-root system user for security compliance
RUN useradd -u 1001 devopsuser && \
    chown -R devopsuser:devopsuser /app

# Switch to non-root user
USER devopsuser

# Expose application port
EXPOSE 5000

# Container liveness health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Start the Flask web application
CMD ["python", "app.py"]
