from typing import Generator
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    if not is_authenticated(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = from_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
