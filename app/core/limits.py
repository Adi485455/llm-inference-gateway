import asyncio

from app.core.config import settings

llm_semaphore = asyncio.Semaphore(
    settings.max_concurrent_requests
)