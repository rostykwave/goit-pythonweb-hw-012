import os

class Config:
    DB_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://username:password@localhost/contacts_db"
    )
    JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
    JWT_ALGORITHM = "HS256"  
    JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "3600"))
    
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Contact Manager") 
    MAIL_STARTTLS = bool(os.getenv("MAIL_STARTTLS", "True")) 
    MAIL_SSL_TLS = bool(os.getenv("MAIL_SSL_TLS", "False")) 
    USE_CREDENTIALS = bool(os.getenv("USE_CREDENTIALS", "True")) 
    VALIDATE_CERTS = bool(os.getenv("VALIDATE_CERTS", "True")) 
    
    CLOUDINARY_NAME = os.getenv("CLOUDINARY_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

config = Config