import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Convert ?ssl=true into the SSL object PyMySQL expects
connect_args = {}
if DATABASE_URL and "ssl=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?ssl=true", "")
    connect_args = {"ssl": {}}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()