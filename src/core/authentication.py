from jose import jwt
import bcrypt
from models.models import User
from datetime import datetime, timedelta, timezone
from api.deps import find_by_email

SECRET_KEY = "123"
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 60

def create_token(user: User) -> str:
    payload = {
        "user_id": user.id, #user.id can't be found, this needs change i think 
        "email": user.email,
        "exp": datetime.now(timezone.utc)+ timedelta(minutes = TOKEN_EXPIRATION_TIME)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def is_authenticated(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        user = find_by_email(email)
        return user is not None and str(user.id) == str(payload.get("user_id")) #here too
    except Exception:
        return False

def from_token(token: str) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        return find_by_email(email)
    except Exception:
        return None