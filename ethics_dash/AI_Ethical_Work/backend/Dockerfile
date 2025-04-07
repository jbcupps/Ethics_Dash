# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr (good for logging)
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY --chown=app:app backend/requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and context directory into the container
COPY --chown=app:app backend/ /app/backend/
COPY --chown=app:app Context/ /app/context/

# Switch to the non-root user
USER app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define the command to run the app using Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "backend.wsgi:app"] 