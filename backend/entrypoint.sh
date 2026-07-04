#!/bin/sh
set -e

echo "Running Alembic migrations..."
alembic upgrade head

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "Seeding demo data (idempotent)..."
  python -m app.seed
fi

echo "Starting API server..."
exec "$@"
