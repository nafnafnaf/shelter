#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="shelter_registry_backup_$TIMESTAMP.sql"

echo "💾 Creating database backup..."

docker-compose exec -T db pg_dump -U postgres shelter_registry > "$BACKUP_DIR/$BACKUP_FILE"
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "shelter_registry_backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_FILE.gz"
