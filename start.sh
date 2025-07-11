#!/bin/bash

# Production startup script for the web application

# Set default values
export FLASK_ENV=${FLASK_ENV:-production}
export WORKERS=${WORKERS:-4}
export PORT=${PORT:-8080}
export HOST=${HOST:-0.0.0.0}

# Start the application with Gunicorn
exec gunicorn \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 60 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    app:app
