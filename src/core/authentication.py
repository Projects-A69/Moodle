from jose import jwt
import bcrypt

SECRET_KEY = "123"
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME = 60

def create_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.now(timezone.utc)+ timedelta(minutes = TOKEN_EXPIRATION_TIME)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def is_authenticated(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        user = find_by_username(username)
        return user is not None and str(user.id) == str(payload.get("user_id"))
    except Exception:
        return False

def from_token(token: str) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        return find_by_username(username)
    except Exception:
        return None