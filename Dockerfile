# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

# Install system dependencies (if any - add as needed)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt
RUN if [ ! -f requirements.txt ]; then echo 'requirements.txt not found, installing defaults' && pip install dash gunicorn; else pip install --no-cache-dir -r requirements.txt; fi

# Copy project code
# Ensure permissions are set for the non-root user
COPY --chown=app:app . /app

# Switch to the non-root user
USER app

# Expose the port the app runs on (matching docker-compose.yml)
EXPOSE 8050

# Define the command to run the application
# Using gunicorn for a more production-ready server
# Assumes your Dash app instance is named 'server' in 'app.py'
# Adjust 'app:server' if your entrypoint file or app variable is different
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"] 