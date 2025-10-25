import redis.asyncio as redis
from fastapi import Request
from app.core.settings import settings

def init_redis_connection():
    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis