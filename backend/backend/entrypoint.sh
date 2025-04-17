#!/usr/bin/env bash
set -e

# Wait for MongoDB
echo "Waiting for MongoDB to be available..."
while ! nc -z ai-mongo 27017; do
  sleep 1
  echo "Still waiting for MongoDB..."
done

echo "MongoDB is up. Populating default memes..."

# Run the memes population script
python3 /app/scripts/populate_memes.py

echo "Starting Gunicorn server..."
exec gunicorn --workers 4 --bind 0.0.0.0:5000 backend.wsgi:app 