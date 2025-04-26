FROM python:3.9-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    pymongo \
    python-dotenv \
    dash \
    dash-bootstrap-components \
    anthropic \
    openai \
    google-generativeai

# Copy requirements.txt if you have one
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy startup script
COPY scripts/start-backend.sh /app/
RUN chmod +x /app/start-backend.sh

# Copy application code
COPY backend /app/backend
COPY documents /app/documents

# Set environment variables
ENV PYTHONPATH=/app

# Start the application with startup script
CMD ["/app/start-backend.sh"] 