#!/bin/bash
set -e

# Wait for MongoDB to be available - necessary in Azure App Service
echo "Waiting for MongoDB to be available..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if nc -z ai-mongo 27017; then
        echo "MongoDB is up, proceeding..."
        break
    fi
    attempt=$((attempt+1))
    echo "Waiting for MongoDB (attempt $attempt/$max_attempts)..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "MongoDB did not become available in time, but will continue anyway..."
fi

# Implement a small delay to ensure MongoDB is fully initialized
echo "Waiting for MongoDB to initialize (10s)..."
sleep 10

# Populate default memes if the script exists
if [ -f "/app/scripts/populate_memes.py" ]; then
    echo "Populating default memes..."
    python /app/scripts/populate_memes.py /app/documents/memes.json || echo "Meme population failed, but will continue..."
else
    echo "Populate memes script not found at /app/scripts/populate_memes.py, skipping."
fi

# Add a small delay after DB initialization
echo "Waiting 5s after DB initialization before starting Gunicorn..."
sleep 5

# Start Gunicorn
echo "Starting Gunicorn server..."

# Run Gunicorn with longer timeout for startup operations
exec gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 wsgi:app 