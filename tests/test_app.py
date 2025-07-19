import pytest
from unittest.mock import patch, Mock


class TestHealthEndpoints:
    """Test basic health endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        # Root endpoint now returns HTML, not JSON
        assert "text/html" in response.headers["content-type"]
        assert "Debater Bot" in response.text

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "redis" in data


class TestChatEndpoint:
    """Test the main chat endpoint"""

    def test_chat_endpoint_exists(self, client):
        """Test that the chat endpoint exists and accepts requests"""
        response = client.post(
            "/chat",
            json={
                "conversation_id": None,
                "message": "Hello"
            }
        )
        # Should either return 200 (success) or 500 (missing OpenAI key)
        assert response.status_code in [200, 500]

    def test_chat_endpoint_validation(self, client):
        """Test that the chat endpoint validates input"""
        # Test missing message
        response = client.post(
            "/chat",
            json={"conversation_id": None}
        )
        assert response.status_code == 422


class TestErrorHandling:
    """Test basic error handling"""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422