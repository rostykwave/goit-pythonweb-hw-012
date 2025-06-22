import os

class Config:
    """
    Application configuration class.
    
    Loads configuration from environment variables with sensible defaults.
    Used for database connection, JWT authentication, email service, and cloud storage.
    """
    
    DB_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://username:password@localhost/contacts_db"
    )
    """str: Database connection URL using asyncpg driver for PostgreSQL."""
    
    JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
    """str: Secret key for JWT token signing and verification."""
    
    JWT_ALGORITHM = "HS256"
    """str: Algorithm used for JWT token encoding/decoding."""
    
    JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "3600"))
    """int: JWT token expiration time in seconds (default: 1 hour)."""
    
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    """str: SMTP username for email service."""
    
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    """str: SMTP password for email service."""
    
    MAIL_FROM = os.getenv("MAIL_FROM")
    """str: Default sender email address."""
    
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    """str: SMTP server hostname."""
    
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    """int: SMTP server port (default: 587 for STARTTLS)."""
    
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Contact Manager")
    """str: Display name for email sender."""
    
    MAIL_STARTTLS = bool(os.getenv("MAIL_STARTTLS", "True"))
    """bool: Enable STARTTLS for email connection."""
    
    MAIL_SSL_TLS = bool(os.getenv("MAIL_SSL_TLS", "False"))
    """bool: Enable SSL/TLS for email connection."""
    
    USE_CREDENTIALS = bool(os.getenv("USE_CREDENTIALS", "True"))
    """bool: Use credentials for email authentication."""
    
    VALIDATE_CERTS = bool(os.getenv("VALIDATE_CERTS", "True"))
    """bool: Validate SSL certificates for email connection."""
    
    CLOUDINARY_NAME = os.getenv("CLOUDINARY_NAME")
    """str: Cloudinary cloud name for image storage."""
    
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    """str: Cloudinary API key for authentication."""
    
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    """str: Cloudinary API secret for authentication."""

    REDIS_HOST: str = "localhost"
    """str: Redis server hostname (default: localhost)."""
    
    REDIS_PORT: int = 6379
    """int: Redis server port (default: 6379)."""
    
    REDIS_PASSWORD: str | None = None
    """str | None: Redis server password (default: None for no authentication)."""
    
    REDIS_DB: int = 0
    """int: Redis database number (default: 0)."""
    
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    """str: Complete Redis connection URL constructed from host, port, and database."""
    
    CACHE_EXPIRE_TIME: int = 900  # 15 minutes
    """int: Cache expiration time in seconds (default: 900 seconds = 15 minutes)."""

config = Config()
"""Config: Global configuration instance."""