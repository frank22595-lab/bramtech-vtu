#!/bin/bash
set -e

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Running migrations ==="
python manage.py migrate --noinput

echo "=== Seeding catalog ==="
python manage.py seed_catalog || echo "Seed already done"

echo "=== Running production setup ==="
python manage.py setup_production || echo "Setup already done"

echo "=== Starting Gunicorn ==="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --access-logfile - --error-logfile -
