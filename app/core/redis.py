import redis
from app.core.config import settings

#Redis configuration
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,#use in case of multiple layers
    decode_responses=True
)