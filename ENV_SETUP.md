# Environment Variables Configuration

This project uses environment variables for configuration management. This allows you to easily switch between different environments (development, production) and keep sensitive information secure.

## Quick Start

1. **Copy the environment template:**

   ```bash
   # For development
   python manage_env.py use --env .env.development

   # For production
   python manage_env.py use --env .env.production
   ```

2. **Edit the `.env` file** with your specific values:

   ```bash
   # Update database credentials, secret keys, etc.
   ```

3. **Start your application:**
   ```bash
   docker-compose up -d
   ```

## Environment Files

- `.env.development` - Template for development environment
- `.env.production` - Template for production environment
- `.env` - Active environment file (created by copying one of the templates)

## Important Environment Variables

### Database Configuration

- `MONGODB_URL` - MongoDB connection string
- `DATABASE_NAME` - Database name
- `COLLECTION_NAME` - Collection name for sensor data

### Security

- `SECRET_KEY` - **MUST CHANGE IN PRODUCTION** - Used for security features
- `MONGO_INITDB_ROOT_USERNAME` - MongoDB root username
- `MONGO_INITDB_ROOT_PASSWORD` - **MUST CHANGE IN PRODUCTION** - MongoDB root password

### Application Settings

- `ENVIRONMENT` - Set to `development` or `production`
- `DEBUG` - Enable debug mode (`true`/`false`)
- `LOG_LEVEL` - Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

### Email Configuration (for alerts)

- `EMAIL_USERNAME` - Email account username
- `EMAIL_PASSWORD` - Email account password
- `EMAIL_FROM` - From email address

## Usage in Code

```python
from config import settings

# Access configuration
print(f"App running on {settings.host}:{settings.port}")
print(f"Database: {settings.database_name}")
print(f"Environment: {settings.environment}")

# Check environment
if settings.is_production:
    print("Running in production mode")
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Change default passwords** in production
3. **Generate strong secret keys** for production
4. **Use environment-specific configurations**
5. **Limit CORS origins** in production

## Managing Environment Files

Use the provided script to manage environment files:

```bash
# List available environment files
python manage_env.py list

# Switch to development environment
python manage_env.py use --env .env.development

# Switch to production environment
python manage_env.py use --env .env.production
```

## Docker Environment Variables

When using Docker Compose, environment variables are automatically loaded from the `.env` file. You can also override them:

```bash
# Override specific variables
MONGODB_URL=mongodb://external-mongo:27017 docker-compose up

# Use different environment file
cp .env.production .env
docker-compose up
```
