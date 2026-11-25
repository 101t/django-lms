#!/bin/sh
# Usage: entrypoint.sh web|worker|beat|<any command>
set -e

case "$1" in
  web)
    python manage.py migrate --noinput
    # Creates the first admin from DJANGO_SUPERUSER_USERNAME/_PASSWORD/_EMAIL; harmless once it exists.
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
      python manage.py createsuperuser --noinput >/dev/null 2>&1 || true
    fi
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 \
      --workers "${WEB_CONCURRENCY:-3}" --access-logfile - --forwarded-allow-ips='*'
    ;;
  worker) exec celery -A config worker --loglevel=info ;;
  beat)   exec celery -A config beat --loglevel=info ;;
  *)      exec "$@" ;;
esac
