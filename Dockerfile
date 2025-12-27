# Dockerfile for Google Cloud Run deployment (React Transcript Tagger)
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --include=dev && npm cache clean --force

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# Build React app for production
RUN npm run build

# Production stage - use Python to serve static files
FROM python:3.11-slim

WORKDIR /app

# Install only what's needed to run Flask
RUN pip install --no-cache-dir flask gunicorn

# Copy built React app from build stage
COPY --from=build /app/build ./build

# Copy backend code
COPY backend/ ./backend/

# Copy server script
COPY server.py .

# Copy transcript files for loading
COPY 12.7.txt 12.8.txt 12.10.txt 12.12.txt ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server.py
ENV FLASK_ENV=production

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Initialize database and load transcripts on first run
# This will be done via a startup script or manually
# For now, we'll let the API handle it on first request

# Run the application
# Cloud Run sets PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 60 --max-requests 1000 --max-requests-jitter 50 server:app

