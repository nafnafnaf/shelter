# Test 1: Can we connect to the database from the web container?
docker exec shelter_web python manage.py dbshell -c "\l"

# Test 2: What password does the database actually expect?
docker exec shelter_db psql -U postgres -c "SELECT 1;"

# Test 3: Try connecting with the credentials from .env
docker exec shelter_web python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='shelter_registry',
        user='postgres',
        password='opensuse',
        host='db',
        port='5432'
    )
    print('✓ Connection successful!')
    conn.close()
except Exception as e:
    print('✗ Connection failed:', e)
"

# Test 4: Check what environment variables are actually loaded
docker exec shelter_web env | grep -E "DB_"

#Check the password on the DB
# Check docker-compose.yml database configuration
grep -A 10 "postgres:" docker-compose.yml

# Or check the database environment
docker exec shelter_db env | grep POSTGRES_PASSWORD



#####
docker exec shelter_db psql -U postgres -d shelter_registry -c "\d animals_animal" | head -30
### CREATE SUPERUSER
docker exec -it shelter_web python manage.py createsuperuser
