from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.database.session import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator:
    """
    Get a database connection from the connection pool and return it
    to the pool when the request is finished.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Complete this method to get the current user session from the token
def get_current_user(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    pass
