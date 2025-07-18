import os
from fastapi import FastAPI, HTTPException
from debater.utils.settings import Settings
from debater.utils.redis_client import RedisClient


app = FastAPI()
settings = Settings()
redis_client = RedisClient(settings)


@app.get("/")
async def root():
    return {"message": f"Hello World, {settings.mode}"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_healthy = redis_client.health_check()
        return {
            "status": "healthy" if redis_healthy else "degraded",
            "redis": "connected" if redis_healthy else "disconnected",
            "mode": settings.mode
        }
    except Exception as e:
        return {
            "status": "degraded",
            "redis": "error",
            "mode": settings.mode,
            "error": str(e)
        }


@app.get("/test-redis")
async def test_redis():
    """Test redis connection and basic operations"""
    return redis_client.test_connection()
