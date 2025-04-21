#!/bin/bash
set -e

# Optional: Wait for MongoDB to be available (Compose depends_on is preferred)
# echo "Waiting for MongoDB to be available..."
# until nc -z ai-mongo 27017; do
#     sleep 1
# done
# echo "MongoDB is up."

# Populate default memes if the script exists
if [ -f "/app/scripts/populate_memes.py" ]; then
    echo "Populating default memes..."
    python /app/scripts/populate_memes.py /app/documents/memes.json
else
    echo "Populate memes script not found at /app/scripts/populate_memes.py, skipping."
fi

# Start Gunicorn
echo "Starting Gunicorn server..."

# Run Gunicorn assuming wsgi.py is in /app and contains 'app'
# Assumes WORKDIR /app is set in Dockerfile
exec gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app 