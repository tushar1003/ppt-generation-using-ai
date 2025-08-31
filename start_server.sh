#!/bin/bash

# PPT Generation API Server Startup Script
# Supports both development and production modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/tusharbhatia/Desktop/Assessment"
VENV_PATH="$PROJECT_DIR/venv"
GUNICORN_CONF="$PROJECT_DIR/gunicorn.conf.py"
WSGI_MODULE="core.wsgi:application"

# Default values
MODE="development"
PORT=8000
WORKERS=""
RELOAD="--reload"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            MODE="production"
            RELOAD=""
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="--workers $2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --production    Run in production mode"
            echo "  --port PORT     Specify port (default: 8000)"
            echo "  --workers N     Number of worker processes"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🚀 Starting PPT Generation API Server${NC}"
echo -e "${YELLOW}Mode: $MODE${NC}"
echo -e "${YELLOW}Port: $PORT${NC}"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${GREEN}✓ Activating virtual environment${NC}"
    source "$VENV_PATH/bin/activate"
else
    echo -e "${RED}✗ Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Install/update dependencies
echo -e "${GREEN}📦 Installing dependencies${NC}"
pip install -r requirements.txt --quiet

# Run migrations
echo -e "${GREEN}🔄 Running database migrations${NC}"
python manage.py migrate --no-input

# Collect static files (if in production)
if [ "$MODE" = "production" ]; then
    echo -e "${GREEN}📁 Collecting static files${NC}"
    python manage.py collectstatic --no-input --clear
fi

# Create media directory if it doesn't exist
mkdir -p media
mkdir -p templates/presentations

# Set environment variables
export DJANGO_SETTINGS_MODULE=core.settings
if [ "$MODE" = "development" ]; then
    export DJANGO_DEBUG=True
else
    export DJANGO_DEBUG=False
fi

# Start server
echo -e "${GREEN}🌟 Starting server...${NC}"

if [ "$MODE" = "development" ]; then
    # Development mode - use Django's development server
    echo -e "${YELLOW}Running in development mode with Django dev server${NC}"
    python manage.py runserver "0.0.0.0:$PORT"
else
    # Production mode - use Gunicorn
    echo -e "${YELLOW}Running in production mode with Gunicorn${NC}"
    
    # Update gunicorn config with custom port
    BIND_ADDRESS="0.0.0.0:$PORT"
    
    gunicorn \
        --config "$GUNICORN_CONF" \
        --bind "$BIND_ADDRESS" \
        $WORKERS \
        $RELOAD \
        "$WSGI_MODULE"
fi
