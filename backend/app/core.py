import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback a SQLite si no se define DATABASE_URL
# En SQLite, usa un archivo local en el workspace del runner.
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./ci.db"

# Si usas SQLite, conviene 'check_same_thread' para FastAPI
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()