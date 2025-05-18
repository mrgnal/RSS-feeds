#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate

echo "Starting development server..."
exec python manage.py runserver 0.0.0.0:80