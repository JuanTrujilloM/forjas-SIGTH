#!/usr/bin/env bash
# Render's free disk is wiped on every restart, so each boot rebuilds the demo from scratch
set -euo pipefail

python manage.py migrate --noinput

# the demo commands refuse to run without DEBUG; the server itself keeps DEBUG=False
DEBUG=True python manage.py seed_demo_employees --replace
DEBUG=True python manage.py seed_demo_users --replace

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}" --workers 2
