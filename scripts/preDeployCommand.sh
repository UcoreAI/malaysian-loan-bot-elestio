#!/bin/bash
set -e

echo "🧹 Cleaning up old containers..."

# Stop and remove old containers
docker stop malaysian_loan_bot postgres_malaysian_loan redis_malaysian_loan nginx_elestio 2>/dev/null || true
docker rm malaysian_loan_bot postgres_malaysian_loan redis_malaysian_loan nginx_elestio 2>/dev/null || true

# Remove orphaned containers
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up unused images
docker image prune -f 2>/dev/null || true

echo "✅ Cleanup completed"