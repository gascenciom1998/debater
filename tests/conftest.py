import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from debater.app import app
from debater.utils.settings import Settings


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    # Set required environment variables for testing
    import os
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["MODE"] = "testing"
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return Settings(
        app_name="debater",
        mode="testing",
        redis_url="redis://localhost:6379",
        openai_api_key="test-key",
        ai_model="gpt-4-turbo"
    )


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.set.return_value = True
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.rpush.return_value = 1
    mock_redis.expire.return_value = True
    mock_redis.llen.return_value = 0
    mock_redis.lrange.return_value = []
    return mock_redis


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a test response"
    return mock_response


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing"""
    return {
        "topic": "Climate Change",
        "bot_position": "Human activities are the primary cause of climate change",
        "user_position": "Climate change is natural",
        "messages": [
            {"role": "user", "message": "Convince me that human activities cause climate change"},
            {"role": "bot", "message": "The evidence clearly shows that human activities are the primary driver of climate change."}
        ]
    }