from itsdangerous import URLSafeTimedSerializer
from src.core.config import settings

serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)

def generate_approval_token(user_id: str) -> str:
    return serializer.dumps(user_id, salt="approve-teacher")

def verify_approval_token(token: str, max_age: int = 3600) -> str:
    return serializer.loads(token, salt="approve-teacher", max_age=max_age)


def generate_student_approval_token(user_id: str) -> str:
    return serializer.dumps(user_id, salt="approve-student")

def verify_student_approval_token(token: str, max_age: int = 3600) -> str:
    return serializer.loads(token, salt="approve-student", max_age=max_age)