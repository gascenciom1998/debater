import redis
import json
import uuid
from typing import Optional, List
from debater.utils.settings import Settings
from debater.models.conversation import Conversation, Message, Role


class RedisClient:
    def __init__(self, settings: Settings):
        # Use SSL for external connections (upstash), not for local
        if 'upstash.io' in settings.redis_url or settings.redis_url.startswith('rediss://'):
            self.redis = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                ssl_cert_reqs=None
            )
        else:
            # Local redis without SSL
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)

        self.settings = settings

    def health_check(self) -> bool:
        """Check if redis is accessible"""
        try:
            self.redis.ping()
            return True
        except Exception as e:
            # Log the error but don't fail deployment
            print(f"Redis health check failed: {e}")
            return False

    def test_connection(self) -> dict:
        """Test redis connection and basic operations"""
        try:
            # Test ping
            self.redis.ping()

            # Test set/get
            self.redis.set("test_key", "test_value", ex=60)  # expire in 60 seconds
            value = self.redis.get("test_key")

            return {
                "status": "success",
                "ping": "ok",
                "set_get": "ok" if value == "test_value" else "failed"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID"""
        return str(uuid.uuid4())

    def store_conversation_metadata(self, conversation_id: str, topic: str, bot_position: str, first_message: str) -> None:
        """Store conversation metadata (topic, position, etc.)"""
        key = f"conv_meta:{conversation_id}"
        metadata = {
            "topic": topic,
            "bot_position": bot_position,
            "first_message": first_message
        }
        # Store metadata, expire after 24 hours
        self.redis.setex(key, 86400, json.dumps(metadata))

    def get_conversation_metadata(self, conversation_id: str) -> Optional[dict]:
        """Get conversation metadata"""
        key = f"conv_meta:{conversation_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def add_message(self, conversation_id: str, role: Role, message: str) -> bool:
        """Add a message to conversation using redis list operations"""
        list_key = f"conv_messages:{conversation_id}"

        # Create message object
        message_obj = {
            "role": role.value,
            "message": message
        }

        # Add to end of list
        self.redis.rpush(list_key, json.dumps(message_obj))

        # Set expiry on the list
        self.redis.expire(list_key, 86400)

        # Maintain FIFO: keep only the last 50 messages
        list_length = self.redis.llen(list_key)
        if list_length > 50:
            # Remove oldest messages, keep only the last 50
            self.redis.ltrim(list_key, -50, -1)

        return True

    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation"""
        list_key = f"conv_messages:{conversation_id}"
        messages_data = self.redis.lrange(list_key, 0, -1)

        messages = []
        for msg_data in messages_data:
            msg_dict = json.loads(msg_data)
            messages.append(Message(
                role=Role(msg_dict["role"]),
                message=msg_dict["message"]
            ))

        return messages

    def create_conversation(self, topic: str, bot_position: str, first_message: str) -> Conversation:
        """Create a new conversation"""
        conversation_id = self.generate_conversation_id()

        # Store metadata
        self.store_conversation_metadata(conversation_id, topic, bot_position, first_message)

        # Add first message
        self.add_message(conversation_id, Role.USER, first_message)

        # Return conversation object
        return Conversation(
            conversation_id=conversation_id,
            topic=topic,
            bot_position=bot_position,
            first_message=first_message,
            messages=self.get_conversation_messages(conversation_id)
        )

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get full conversation with metadata and messages"""
        metadata = self.get_conversation_metadata(conversation_id)
        if not metadata:
            return None

        messages = self.get_conversation_messages(conversation_id)

        return Conversation(
            conversation_id=conversation_id,
            topic=metadata["topic"],
            bot_position=metadata["bot_position"],
            first_message=metadata["first_message"],
            messages=messages
        )

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation from redis"""
        meta_key = f"conv_meta:{conversation_id}"
        messages_key = f"conv_messages:{conversation_id}"
        self.redis.delete(meta_key, messages_key)