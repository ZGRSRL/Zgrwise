from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://zgr:zgrpass@db:5432/zgrwise")
_engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

def get_db_session():
    return SessionLocal()