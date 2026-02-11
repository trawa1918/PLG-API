#!/bin/sh
set -eu

SECRET_FILE="${DJANGO_SECRET_KEY_FILE:-/data/django_secret_key}"

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  if [ -f "$SECRET_FILE" ]; then
    export DJANGO_SECRET_KEY="$(cat "$SECRET_FILE")"
  else
    mkdir -p "$(dirname "$SECRET_FILE")"
    export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    printf "%s" "$DJANGO_SECRET_KEY" > "$SECRET_FILE"
    chmod 600 "$SECRET_FILE" || true
  fi
fi

exec "$@"