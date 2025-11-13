from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from pwdlib import PasswordHash
from app.core.config import settings
from app.core.redis import redis_client

pwd_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc) 
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def blacklist_token(token: str, expires_in: int):
    """
    Blacklist a token by adding it to Redis with an expiry.
    """
    print(redis_client.keys())
    redis_client.setex(f"blacklist:{token}", expires_in, "blacklisted")




def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted.
    """
    return redis_client.exists(f"blacklist:{token}") == 1
    

def verify_access_token(token: str) -> Optional[int]:
    try:
        if is_token_blacklisted(token):
            return None
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except Exception as e:
        return None
    


