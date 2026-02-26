import json
import redis

from app.core.config import settings


def push_notification(channel: str, payload: dict) -> None:
    client = redis.from_url(settings.redis_url)
    client.publish(channel, json.dumps(payload))
