#!/bin/bash
# startup.sh - Azure App Service startup command
# Set this in Azure Portal: Configuration > General settings > Startup Command
# Value: bash startup.sh

cd /home/site/wwwroot

# Install dependencies
pip install -r requirements.txt

# Initialize database tables
python -c "from database import create_tables; create_tables()"

# Start FastAPI with Gunicorn (production WSGI server)
gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info
