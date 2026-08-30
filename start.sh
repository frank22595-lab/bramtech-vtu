#!/bin/bash
set -e

echo "=== Running migrations ==="
python manage.py migrate --noinput

echo "=== Seeding catalog (safe to run multiple times) ==="
python manage.py seed_catalog || echo "Seed already done, skipping"

echo "=== Creating superuser + funding mock aggregator ==="
python manage.py setup_production || echo "Setup already done"

echo "=== Starting Django server ==="
exec python manage.py runserver 0.0.0.0:$PORT
