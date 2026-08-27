import os


# Default Superadmin
DEFAULT_SUPERADMIN_NAME = os.getenv('DEFAULT_SUPERADMIN_NAME')
DEFAULT_SUPERADMIN_EMAIL = os.getenv('DEFAULT_SUPERADMIN_EMAIL')
DEFAULT_SUPERADMIN_MSISDN = os.getenv('DEFAULT_SUPERADMIN_MSISDN')
DEFAULT_SUPERADMIN_PASSWORD = os.getenv('DEFAULT_SUPERADMIN_PASSWORD')

# Seeding (see Backend/seed.py). Off by default; the docker-compose .env.example
# turns it on so the portal has sample data to show right after `docker compose up`.
SEED_DEMO_DATA = os.getenv('SEED_DEMO_DATA', 'false').lower() == 'true'


# SECRETS
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_EXPIRY_HOURS = 3


# CORS (browser-facing origins allowed to call this API, e.g. the Next.js frontend)
CORS_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',') if origin.strip()]


# DB
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

SQLALCHEMY_DATABASE_URL_ASYNC = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'


# Logging
MAX_LOG_BYTES = 1 * 1024 * 30 # 30MB
MAX_LOG_BACKUPS = 1

PORTAL_API_LOG_FILE = os.getenv('PORTAL_API_LOG_FILE', '/var/log/jubilee_claims_processing/portal_api.log')
