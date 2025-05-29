from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.base import Base
from src.core.config import settings
from src.models.models import User,Admin,Teacher,Student,Course,Tag

engine = create_engine(settings.DATABASE_URL,echo=True,
    pool_pre_ping=True,pool_recycle=1800)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)