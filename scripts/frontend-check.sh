#!/bin/sh
set -e

# Default backend service name and port
BACKEND_HOST=${BACKEND_HOST:-ai-backend}
BACKEND_PORT=${BACKEND_PORT:-5000}

echo "Checking if backend service is available at $BACKEND_HOST:$BACKEND_PORT..."

# Function to check if backend is reachable
check_backend() {
  if command -v nc > /dev/null; then
    nc -z -w2 $BACKEND_HOST $BACKEND_PORT
    return $?
  elif command -v wget > /dev/null; then
    wget --spider -q http://$BACKEND_HOST:$BACKEND_PORT/
    return $?
  else
    # If no tools available, just try to connect directly
    (echo > /dev/tcp/$BACKEND_HOST/$BACKEND_PORT) >/dev/null 2>&1
    return $?
  fi
}

# Wait for backend to become available
count=0
max_attempts=30
until check_backend || [ $count -ge $max_attempts ]; do
  echo "Backend service is not available yet. Waiting... ($count/$max_attempts)"
  count=$((count+1))
  sleep 5
done

if [ $count -ge $max_attempts ]; then
  echo "Warning: Backend service did not become available in time."
  echo "The frontend will still start, but some features may not work until the backend is ready."
else
  echo "Backend service is available! Starting the frontend server."
fi

# Execute the original command
exec "$@" 