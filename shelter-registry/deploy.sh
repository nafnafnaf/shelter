#!/bin/bash

echo "🚀 Deploying Shelter Registry..."

# Build and start containers
docker-compose down
docker-compose up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T web python manage.py migrate_schemas --shared
docker-compose exec -T web python manage.py migrate_schemas

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo "📊 Check status with: docker-compose ps"
echo "📝 View logs with: docker-compose logs -f web"
