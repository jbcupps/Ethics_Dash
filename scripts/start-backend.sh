#!/bin/bash
set -e

# Extract hostname from MongoDB URI
MONGO_HOST=${MONGODB_URI:-$MONGO_URI}
MONGO_HOST=$(echo $MONGO_HOST | sed -n 's/.*@\(.*\):.*/\1/p')

# If extraction failed, use default
if [ -z "$MONGO_HOST" ]; then
  MONGO_HOST="ai-mongo"
  echo "Using default MongoDB host: $MONGO_HOST"
else
  echo "Extracted MongoDB host: $MONGO_HOST"
fi

# Function to check if MongoDB is available using Python
check_mongo() {
  python -c "import pymongo; client = pymongo.MongoClient(host='$MONGO_HOST', port=27017, serverSelectionTimeoutMS=5000); client.server_info(); client.close();"
  return $?
}

# Wait for MongoDB to become available
echo "Waiting for MongoDB ($MONGO_HOST:27017) to start..."
attempt=0
max_attempts=60
retry_interval=2

until check_mongo || [ $attempt -ge $max_attempts ]; do
  attempt=$((attempt+1))
  echo "Waiting for MongoDB (attempt $attempt/$max_attempts)..."
  sleep $retry_interval
done

if [ $attempt -ge $max_attempts ]; then
  echo "Error: MongoDB is not available after $max_attempts attempts."
  echo "MongoDB URI: ${MONGODB_URI:-$MONGO_URI}"
  echo "MongoDB host extracted: $MONGO_HOST"
  echo "Continuing startup anyway..."
else
  echo "MongoDB is available! Starting the backend application."
fi

# Start the Flask application
cd /app
exec python -m backend.app 