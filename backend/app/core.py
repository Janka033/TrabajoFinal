import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _build_db_url_from_env() -> str | None:
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")
    if all([host, port, user, name]):
        pwd = password or ""
        # PyMySQL driver for MySQL
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}"
    return None


DATABASE_URL = os.getenv("DATABASE_URL") or _build_db_url_from_env()

# Fallback a SQLite si no se define DATABASE_URL ni variables MySQL
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./ci.db"

engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
