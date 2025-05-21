from sqlalchemy.orm import Session
from src.models.models import User
from typing import Optional

def find_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()