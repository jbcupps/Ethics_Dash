# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr (good for logging)
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

# Install system dependencies like curl and CA certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY --chown=app:app requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir dash-cytoscape && \
    pip install --no-cache-dir google-generativeai && \
    pip install --no-cache-dir anthropic && \
    pip install --no-cache-dir openai

# Copy the application code into the container
COPY --chown=app:app . /app/backend/

# Copy external documents (memes JSON and ontology)
COPY --chown=app:app documents/ /app/documents/

# Copy scripts
RUN mkdir -p /app/scripts
COPY --chown=app:app scripts/ /app/scripts/

# Switch to the non-root user
USER app

# Make port 5000 available
EXPOSE 5000

# Copy and setup entrypoint script
COPY --chown=app:app backend/backend/entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

# Use custom entrypoint to populate DB and start server
ENTRYPOINT ["/app/backend/entrypoint.sh"] 