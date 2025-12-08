# 1. Build and start containers
docker-compose up -d --build

# 2. Run migrations
docker-compose exec web python manage.py migrate_schemas --shared
docker-compose exec web python manage.py migrate_schemas

# 3. Create shelter
docker-compose exec web python manage.py create_shelter \
    --name "My Shelter" \
    --domain "myshelter.localhost" \
    --email "contact@myshelter.com" \
    --admin-username "admin" \
    --admin-password "secure123" \
    --admin-email "admin@myshelter.com"

# 4. Generate QR codes
docker-compose exec web python manage.py generate_qr_codes