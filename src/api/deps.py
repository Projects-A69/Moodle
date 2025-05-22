from typing import Generator
from fastapi import Depends, HTTPException,Header
from src.core.authentication import from_token, is_authenticated
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


def get_current_user(token: str = Header(...), db: Session = Depends(get_db)):
    if not is_authenticated(db,token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = from_token(db,token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

