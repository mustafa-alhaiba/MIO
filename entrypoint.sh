#!/bin/bash
set -e

echo "Waiting for PostgreSQL database to start..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started successfully."

if [[ "$1" == "gunicorn" ]]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"