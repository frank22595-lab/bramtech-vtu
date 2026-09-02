#!/bin/bash
set -e

echo "=== Collecting static ==="
python manage.py collectstatic --noinput --clear

echo "=== Migrating ==="
python manage.py migrate --noinput

echo "=== Seeding ==="
python manage.py seed_catalog || echo "Seed skipped"

echo "=== Setup ==="
python manage.py setup_production || echo "Setup skipped"

echo "=== Reset admin ==="
python manage.py reset_admin

echo "=== Starting Gunicorn ==="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --access-logfile - --error-logfile -
