#!/bin/bash
set -e

echo "🚀 Starting AyurVoice SaaS Deployment Update..."

# Pull latest changes
git pull origin main

# Rebuild and restart containers
echo "📦 Building and starting production containers..."
docker compose -f docker-compose.prod.yml up -d --build

# Run Alembic migrations safely (stamps pre-existing schemas if unrecorded, then upgrades)
echo "🔄 Running database migrations..."
docker compose -f docker-compose.prod.yml run --rm --no-deps backend python -m backend.app.core.migrations

# Prune dangling Docker images to preserve VPS disk space
echo "🧹 Cleaning up dangling images..."
docker image prune -f

echo "✅ AyurVoice SaaS is up and running!"
docker ps --filter "name=ayurvoice"

