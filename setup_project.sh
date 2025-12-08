#!/bin/bash

# Django Animal Shelter Registry Setup Script
# This script sets up the complete project structure

echo "🏥 Setting up Django Animal Shelter Registry..."

# Create main project directory structure
mkdir -p shelter-registry
cd shelter-registry

echo "📁 Creating directory structure..."

# Create all necessary directories
mkdir -p shelter_registry
mkdir -p animals/{api,management,templates/animals}
mkdir -p shelter/{management/commands,templates/shelter}
mkdir -p templates/{public,base}
mkdir -p static/{css,js,img}
mkdir -p media/animal_photos
mkdir -p staticfiles
mkdir -p logs
mkdir -p backups

echo "📝 Creating __init__.py files..."

# Create __init__.py files
touch shelter_registry/__init__.py
touch animals/__init__.py
touch animals/api/__init__.py
touch animals/management/__init__.py
touch shelter/__init__.py
touch shelter/management/__init__.py
touch shelter/management/commands/__init__.py

echo "🔧 Creating configuration files..."

# Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production-$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-50)
DB_NAME=shelter_registry
DB_USER=postgres
DB_PASSWORD=shelter_db_password_$(openssl rand -base64 12 | tr -d "=+/")
DB_HOST=db
DB_PORT=5432
EOF

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Backups
backups/*.sql
backups/*.sql.gz

# Logs
logs/*.log
EOF

# Create .dockerignore
cat > .dockerignore << EOF
.git
.gitignore
README.md
Dockerfile
.dockerignore
.env
.env.example
backups/
logs/
.vscode/
.idea/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
Thumbs.db
EOF

echo "🐍 Creating Python files..."

# Note: All the Python files would be created here using the content from artifacts
# For brevity, I'm showing the structure. In practice, you'd copy all the content 
# from the artifacts into their respective files.

echo "✨ Creating basic HTML templates..."

# Create base template
mkdir -p templates/base
cat > templates/base/base.html << 'EOF'
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Animal Shelter Registry{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'animals:animal_list' %}">🏥 Shelter Registry</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'shelter:dashboard' %}">Dashboard</a>
                    <a class="nav-link" href="{% url 'animals:animal_list' %}">Animals</a>
                    <a class="nav-link" href="{% url 'shelter:logout' %}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{% url 'shelter:login' %}">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}
        {% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

echo "🚀 Creating deployment scripts..."

# Create deployment script
cat > deploy.sh << 'EOF'
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
EOF

chmod +x deploy.sh

# Create database backup script
cat > backup_db.sh << 'EOF'
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
EOF

chmod +x backup_db.sh

echo "📚 Creating README..."

cat > README.md << 'EOF'
# Django Animal Shelter Registry

A multi-tenant Django application for managing animal shelters with REST API support.

## Features

- 🏥 Multi-tenant architecture (isolated shelter data)
- 🐕 Complete animal management system
- 📱 REST API for mobile/external integrations
- 👥 Role-based access control (Admin/Employee)
- 🏠 Public adoption pages
- 📸 Photo management
- 🏥 Medical records tracking
- 🐳 Docker containerized deployment

## Quick Start

1. **Setup project:**
   ```bash
   git clone <your-repo>
   cd shelter-registry
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```

3. **Create first shelter:**
   ```bash
   docker-compose exec web python manage.py create_shelter \
     --name "My Shelter" \
     --domain "myshelter.localhost" \
     --email "contact@myshelter.com" \
     --admin-username "admin" \
     --admin-password "secure123" \
     --admin-email "admin@myshelter.com"
   ```

## API Endpoints

- `GET /api/v1/animals/` - List animals
- `POST /api/v1/animals/` - Create animal
- `GET /api/v1/animals/public/` - Public adoption list
- `GET /health/` - Health check

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.
EOF

echo "✅ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy all Python files from the artifacts to their respective locations"
echo "2. Run: ./deploy.sh"
echo "3. Create your first shelter using the management command"
echo "4. Configure your Cloudflare tunnel"
echo ""
echo "📁 Project structure:"
find . -type d | head -20 | sed 's/^/  /'
echo ""
echo "🎉 Happy coding!"