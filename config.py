import os

DATABASE_CONFIG = {
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": os.getenv("POSTGRES_HOST_PORT"),
}
