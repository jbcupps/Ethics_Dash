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
# Own the requirements file by the app user before installing
COPY --chown=app:app ethical_review_app/requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
# Run pip install as the app user
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and context directory into the container at /app
# Ensure the copied files are owned by the app user
COPY --chown=app:app ethical_review_app/ /app/ethical_review_app/
COPY --chown=app:app context/ /app/context/

# Switch to the non-root user
USER app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define the command to run the app using Gunicorn
# No longer need FLASK_APP/FLASK_RUN_HOST as gunicorn specifies the app directly
# Gunicorn runs as the 'app' user now
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "ethical_review_app.main:app"] 