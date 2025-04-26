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

# Create a simple health check script since original may not be available
RUN echo '#!/bin/sh \n\
set -e \n\
\n\
# Default backend service name and port \n\
BACKEND_HOST=${BACKEND_HOST:-ai-backend} \n\
BACKEND_PORT=${BACKEND_PORT:-5000} \n\
\n\
echo "Checking if backend service is available at $BACKEND_HOST:$BACKEND_PORT..." \n\
\n\
# Function to check if backend is reachable \n\
check_backend() { \n\
  if command -v nc > /dev/null; then \n\
    nc -z -w2 $BACKEND_HOST $BACKEND_PORT \n\
    return $? \n\
  elif command -v wget > /dev/null; then \n\
    wget --spider -q http://$BACKEND_HOST:$BACKEND_PORT/ \n\
    return $? \n\
  else \n\
    # If no tools available, just try to connect directly \n\
    (echo > /dev/tcp/$BACKEND_HOST/$BACKEND_PORT) >/dev/null 2>&1 \n\
    return $? \n\
  fi \n\
} \n\
\n\
# Wait for backend to become available \n\
count=0 \n\
max_attempts=30 \n\
until check_backend || [ $count -ge $max_attempts ]; do \n\
  echo "Backend service is not available yet. Waiting... ($count/$max_attempts)" \n\
  count=$((count+1)) \n\
  sleep 5 \n\
done \n\
\n\
if [ $count -ge $max_attempts ]; then \n\
  echo "Warning: Backend service did not become available in time." \n\
  echo "The frontend will still start, but some features may not work until the backend is ready." \n\
else \n\
  echo "Backend service is available! Starting the frontend server." \n\
fi \n\
\n\
# Execute the original command \n\
exec "$@"' > /docker-entrypoint.d/30-check-backend.sh

RUN chmod +x /docker-entrypoint.d/30-check-backend.sh

# Copy the build output from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 