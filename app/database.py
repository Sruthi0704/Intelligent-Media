from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL-encoded password: root@123 -> root%40123
DATABASE_URL = "mysql+pymysql://root:root%40123@localhost:3306/media_pipeline"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
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