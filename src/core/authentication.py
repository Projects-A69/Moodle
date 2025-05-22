from jose import jwt
from models.models import User
from datetime import datetime, timedelta, timezone
from api.deps import get_current_user
from fastapi import HTTPException

SECRET_KEY = "123"
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 60

def create_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.now(timezone.utc)+ timedelta(minutes = TOKEN_EXPIRATION_TIME)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def is_authenticated(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        user = get_current_user(email)
        return user is not None and str(user.id) == str(payload.get("user_id"))
    except Exception:
        return False

def from_token(token: str) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        return get_current_user(email)
    except Exception:
        return None
    
    
def get_user_or_raise_401(token: str):
    if not is_authenticated(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return from_token(token)

