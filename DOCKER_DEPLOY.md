# Docker Deployment Guide

Simple Docker deployment guide for your IoT project with CORS properly configured.

## Quick Start

### 1. Environment Setup
Copy and configure your environment file:
```bash
copy .env.production .env
```

Edit `.env` with your settings:
- Update `MONGO_INITDB_ROOT_PASSWORD` with a strong password
- Update `SECRET_KEY` with a strong secret key
- Configure `CORS_ORIGINS` with your client URLs

### 2. Build and Deploy
```bash
# Build and start all services
docker-compose up -d --build

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Your Application
- **Web Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## CORS Configuration

CORS is properly configured in your FastAPI application. Update the `CORS_ORIGINS` in your `.env` file:

```env
# For local development
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:8000"]

# For production with specific domains
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# For development allowing all origins (NOT recommended for production)
CORS_ORIGINS=["*"]
```

### Adding Your Client IP
If you're accessing from another device on your network:
```env
CORS_ORIGINS=["http://localhost:8000","http://192.168.1.100:8000","http://your-server-ip:8000"]
```

## Production Deployment

### 1. Update Environment Variables
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=your_super_secure_secret_key_here
MONGO_INITDB_ROOT_PASSWORD=your_strong_mongodb_password
```

### 2. Secure CORS Settings
```env
CORS_ORIGINS=["https://yourdomain.com"]
ALLOW_CREDENTIALS=true
```

### 3. Deploy with SSL (Optional)
For production with SSL, you can use a reverse proxy like Nginx or Traefik.

## Management Commands

### Starting Services
```bash
docker-compose up -d
```

### Stopping Services
```bash
docker-compose down
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f mongo
```

### Rebuilding After Changes
```bash
docker-compose down
docker-compose up -d --build
```

### Database Management
```bash
# Access MongoDB shell
docker exec -it iot-mongo mongosh

# Backup database
docker exec iot-mongo mongodump --out /data/backup

# View database files
docker exec iot-mongo ls -la /data/db
```

## Troubleshooting

### CORS Errors
If you're getting CORS errors:

1. **Check your CORS_ORIGINS** in `.env`
2. **Make sure the client URL matches exactly** (including protocol and port)
3. **Restart the container** after changing CORS settings:
   ```bash
   docker-compose restart app
   ```

### Common CORS Issues
- **Wrong protocol**: `http://` vs `https://`
- **Wrong port**: Make sure port matches your client
- **Missing trailing slash**: Some clients add `/` automatically
- **Subdomain issues**: `www.domain.com` vs `domain.com`

### Connection Issues
```bash
# Check if containers are running
docker-compose ps

# Check container logs
docker-compose logs app

# Check network connectivity
docker network ls
docker network inspect iot-project_iot-network
```

### Database Issues
```bash
# Check MongoDB status
docker exec iot-mongo mongosh --eval "db.adminCommand('ping')"

# Check database connection from app
docker-compose logs app | grep -i mongo
```

## Environment Variables Reference

### Required
- `MONGO_INITDB_ROOT_PASSWORD` - MongoDB root password
- `SECRET_KEY` - JWT secret key
- `CORS_ORIGINS` - Allowed origins for CORS

### Optional
- `PORT` - Application port (default: 8000)
- `MONGO_PORT` - MongoDB port (default: 27017)
- `DATABASE_NAME` - Database name (default: iot_project)
- `ENVIRONMENT` - Environment (development/production)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)

## Health Monitoring

Your application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-07T12:00:00Z",
  "database": "connected"
}
```

Use this endpoint for monitoring tools or load balancers.
