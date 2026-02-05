import logging
import redis
from config.settings import settings

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client = None
        if settings.ENABLE_REDIS:
            self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info("✅ Redis client initialized")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.client = None

redis_client = RedisManager().client
