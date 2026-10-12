import hashlib
import json

from app.core.config import settings
from app.core.redis_client import redis_client


def generate_cache_key(model: str, message: str) -> str:
    request_data = {
        "model": model,
        "message": message,
    }

    serialized = json.dumps(
        request_data,
        sort_keys=True,
        separators=(",", ":"),
    )

    digest = hashlib.sha256(serialized.encode()).hexdigest()

    return f"llm_gateway:cache:{digest}"


async def get_cached_response(key: str):
    return await redis_client.get(key)


async def set_cached_response(key: str, response: str):
    await redis_client.set(
        key,
        response,
        ex=settings.cache_ttl_seconds,
    )