#!/bin/sh

set -e

python manage.py migrate

python manage.py collectstatic --noinput

uv run uvicorn weather_alert.asgi:application --host 0.0.0.0 --port 8000
