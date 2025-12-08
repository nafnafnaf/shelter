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
