# Node.js base image for building the React app
FROM node:18-alpine as build

# Update build stage packages first (less critical but good practice)
RUN apk update && apk upgrade --no-cache

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./

# Install dependencies (ignoring peer deps)
RUN npm install --legacy-peer-deps

# Copy the rest of the app's source code
COPY . ./

# Build the app for production
RUN npm run build

# Nginx base image for serving the built React app
FROM nginx:stable-alpine

# Update packages in the final Nginx stage to patch vulnerabilities
# This is the critical step for fixing the reported CVEs
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache netcat-openbsd wget bind-tools bash

# Create scripts directory
RUN mkdir -p /docker-entrypoint.d

# Create the health check script using Heredoc for reliability
RUN <<EOF > /docker-entrypoint.d/30-check-backend.sh
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
EOF

RUN chmod +x /docker-entrypoint.d/30-check-backend.sh

# Copy the build output from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 