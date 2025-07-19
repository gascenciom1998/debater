import os
import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from debater.utils.settings import Settings
from debater.utils.redis_client import RedisClient
from debater.services.ai_topic_detector import AITopicDetector
from debater.services.debate_service import DebateService
from debater.models.conversation import DebateRequest, DebateResponse, Message, Role


app = FastAPI()
settings = Settings()
redis_client = RedisClient(settings)

# Initialize AI services only if API key is available
topic_detector = None
debate_service = None
if settings.openai_api_key:
    topic_detector = AITopicDetector(settings.openai_api_key, settings.ai_model)
    debate_service = DebateService(settings.openai_api_key, settings.ai_model)


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
            "mode": settings.mode,
            "ai_model": settings.ai_model,
            "ai_available": debate_service is not None
        }
    except Exception as e:
        return {
            "status": "degraded",
            "redis": "error",
            "mode": settings.mode,
            "ai_model": settings.ai_model,
            "ai_available": debate_service is not None,
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


@app.post("/test-debate")
async def test_debate_response(topic: str, bot_position: str, conversation_history: str = None):
    """Test AI debate response generation"""
    if not debate_service:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    # Parse conversation history if provided
    history = None
    if conversation_history:
        try:
            history = json.loads(conversation_history)
        except json.JSONDecodeError:
            history = [{"role": "user", "content": conversation_history}]

    response = debate_service.generate_debate_response(topic, bot_position, history)
    return {
        "topic": topic,
        "bot_position": bot_position,
        "conversation_history": history,
        "debate_response": response
    }


@app.post("/test-opening")
async def test_opening_argument(topic: str, bot_position: str):
    """Test AI opening argument generation"""
    if not debate_service:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    response = debate_service.generate_opening_argument(topic, bot_position)
    return {
        "topic": topic,
        "bot_position": bot_position,
        "opening_argument": response
    }


@app.post("/chat", response_model=DebateResponse)
async def chat(request: DebateRequest):
    """
    Main chat endpoint for the Kopi challenge.

    Handles conversation management, topic detection, and persistent debate stance.
    """
    if not debate_service or not topic_detector:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    try:
                        # Check if this is a new conversation
        if not request.conversation_id:
            # New conversation - detect topic and set bot position
            topic, bot_position, user_position = topic_detector.detect_topic_and_position(request.message)

            # Create conversation using Redis client
            conversation = redis_client.create_conversation(topic, bot_position, request.message)
            conversation_id = conversation.conversation_id

            # Generate opening argument
            opening_argument = debate_service.generate_opening_argument(topic, bot_position)

            # Add bot's opening message
            redis_client.add_message(conversation_id, Role.BOT, opening_argument)

            # Get updated messages
            messages = redis_client.get_conversation_messages(conversation_id)

            return DebateResponse(
                conversation_id=conversation_id,
                message=messages
            )

        else:
            # Existing conversation - retrieve and continue
            conversation = redis_client.get_conversation(request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Add user's new message
            redis_client.add_message(request.conversation_id, Role.USER, request.message)

            # Get all messages for context
            all_messages = redis_client.get_conversation_messages(request.conversation_id)

            # Prepare conversation history for AI (use all available messages for better context)
            conversation_history = []
            for msg in all_messages:
                conversation_history.append({
                    "role": msg.role.value,
                    "content": msg.message
                })

            # Generate debate response
            debate_response = debate_service.generate_debate_response(
                conversation.topic,
                conversation.bot_position,
                conversation_history
            )

            # Add bot's response
            redis_client.add_message(request.conversation_id, Role.BOT, debate_response)

                        # Get updated messages and return last 10 (5 most recent from each side)
            updated_messages = redis_client.get_conversation_messages(request.conversation_id)
            last_10_messages = updated_messages[-10:] if len(updated_messages) > 10 else updated_messages

            return DebateResponse(
                conversation_id=request.conversation_id,
                message=last_10_messages
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
