import redis
from debater.utils.settings import Settings


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
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
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
                "set_get": "ok" if value == "test_value" else "failed",
                "url": self.settings.redis_url
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": self.settings.redis_url,
                "url_type": "rediss" if self.settings.redis_url.startswith('rediss://') else "redis",
                "has_upstash": "upstash.io" in self.settings.redis_url
            }