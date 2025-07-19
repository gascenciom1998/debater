import os
from fastapi import FastAPI, HTTPException
from debater.utils.settings import Settings
from debater.utils.redis_client import RedisClient
from debater.services.ai_topic_detector import AITopicDetector


app = FastAPI()
settings = Settings()
redis_client = RedisClient(settings)

# Initialize topic detector only if API key is available
topic_detector = None
if settings.openai_api_key:
    topic_detector = AITopicDetector(settings.openai_api_key)


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


@app.post("/test-topic")
async def test_topic_detection(message: str):
    """Test AI topic detection with a message"""
    if not topic_detector:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    topic, bot_position, user_position = topic_detector.detect_topic_and_position(message)
    return {
        "message": message,
        "detected_topic": topic,
        "bot_position": bot_position,
        "user_position": user_position
    }
