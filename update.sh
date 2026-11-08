#!/bin/bash
set -e

echo "🚀 Starting AyurVoice SaaS Deployment Update..."

# Pull latest changes
git pull origin main

# Rebuild and restart containers
echo "📦 Building and starting production containers..."
docker compose -f docker-compose.prod.yml up -d --build

# Run Alembic migrations and seed if needed
echo "🔄 Running database migrations..."
docker exec ayurvoice-backend alembic -c backend/alembic.ini upgrade head

# Prune dangling Docker images to preserve VPS disk space
echo "🧹 Cleaning up dangling images..."
docker image prune -f

echo "✅ AyurVoice SaaS is up and running!"
docker ps --filter "name=ayurvoice"

