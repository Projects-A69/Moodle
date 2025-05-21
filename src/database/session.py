from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from src.core.config import settings
from src.models.models import User,Admin,Teacher,Student,Course,Tag

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)