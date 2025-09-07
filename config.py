"""
Configuration module for the IoT Project
Handles environment variables and application settings
"""
import os
from typing import List


def load_env_file(env_file: str = ".env"):
    """Load environment variables from a file"""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self):
        # Load .env file if it exists
        load_env_file()

        # Application Configuration
        self.app_name: str = os.getenv("APP_NAME", "IoT Project")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.environment: str = os.getenv("ENVIRONMENT", "development")

        # Database Configuration
        self.mongodb_url: str = os.getenv(
            "MONGODB_URL", "mongodb://localhost:27017")
        self.database_name: str = os.getenv("DATABASE_NAME", "iot_project")
        self.collection_name: str = os.getenv("COLLECTION_NAME", "sensor_data")

        # Security
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        # CORS Settings
        cors_origins_str = os.getenv("CORS_ORIGINS", '["*"]')
        self.cors_origins: List[str] = self._parse_list(cors_origins_str)
        self.allow_credentials: bool = os.getenv(
            "ALLOW_CREDENTIALS", "true").lower() == "true"

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", "app.log")

        # WebSocket Configuration
        self.websocket_timeout: int = int(os.getenv("WEBSOCKET_TIMEOUT", "60"))

        # Alert Thresholds
        self.weight_threshold_min: int = int(
            os.getenv("WEIGHT_THRESHOLD_MIN", "0"))
        self.weight_threshold_max: int = int(
            os.getenv("WEIGHT_THRESHOLD_MAX", "1000"))

        # Email Configuration
        self.smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.email_username: str = os.getenv("EMAIL_USERNAME", "")
        self.email_password: str = os.getenv("EMAIL_PASSWORD", "")
        self.email_from: str = os.getenv("EMAIL_FROM", "")

    def _parse_list(self, value: str) -> List[str]:
        """Parse a string representation of a list"""
        try:
            # Remove brackets and quotes, then split by comma
            clean_value = value.strip('[]').replace('"', '').replace("'", "")
            if clean_value:
                return [item.strip() for item in clean_value.split(',')]
            return ["*"]
        except:
            return ["*"]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"


# Create global settings instance
settings = Settings()


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
