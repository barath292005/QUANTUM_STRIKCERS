from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# If POSTGRES_SERVER is default localhost and no active postgres server is running,
# fallback gracefully to a local SQLite database for development & unit testing.
database_url = settings.DATABASE_URL
if "postgresql" in database_url and settings.APP_ENV == "development":
    # Default to lightweight SQLite for dev environment
    database_url = "sqlite:///./weathergpt.db"

connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for obtaining a SQLAlchemy DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
