import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from services.database import create_user, get_user_by_username, get_user_by_email, get_user_by_id

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def register_user(username: str, email: str, password: str) -> dict:
    if get_user_by_username(username):
        return {"success": False, "error": "用户名已存在"}

    if get_user_by_email(email):
        return {"success": False, "error": "邮箱已被注册"}

    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)

    if create_user(user_id, username, email, hashed_password):
        user = get_user_by_id(user_id)
        return {
            "success": True,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
                "is_active": bool(user["is_active"])
            }
        }
    return {"success": False, "error": "创建用户失败"}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    if not user["is_active"]:
        return None
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"]
    }


def get_user_info(user_id: str) -> Optional[dict]:
    user = get_user_by_id(user_id)
    if not user:
        return None
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
        "is_active": bool(user["is_active"])
    }
