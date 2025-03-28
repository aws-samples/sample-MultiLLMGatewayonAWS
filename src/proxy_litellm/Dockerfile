# Use Python 3.12 slim as base image for smaller size
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -d /app appuser  && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p logs

# Copy application code and config files
COPY proxy_litellm/ ./proxy_litellm/
COPY log_conf.yaml .

# Set Python path
ENV PYTHONPATH=/app
ENV PATH="/app/.local/bin:${PATH}"

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "proxy_litellm.core.app:app", "--host", "0.0.0.0", "--port", "8000"]
