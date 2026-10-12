import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import verify_api_key
from app.core.limits import llm_semaphore
from app.core.metrics import metrics

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.cache import (
    generate_cache_key,
    get_cached_response,
    set_cached_response,
)
from app.services.llm_provider import (
    GroqProvider,
    LLMProviderError,
)

router = APIRouter(prefix="/v1", tags=["Chat"])
provider = GroqProvider()
logger = logging.getLogger(__name__)


@router.post(
    "/chat/completions",
    response_model=ChatResponse,
    dependencies=[Depends(verify_api_key)],
)
async def chat_completion(request: ChatRequest):
    start = perf_counter()
    await metrics.increment("total_requests")

    try:
        cache_key = generate_cache_key(
            provider.model,
            request.message,
        )

        cached_response = await get_cached_response(cache_key)

        if cached_response is not None:
            logger.info("LLM cache hit")
            await metrics.increment("cache_hits")

            elapsed = perf_counter() - start
            await metrics.record_latency(elapsed)
            return ChatResponse(
                model=provider.model,
                response=cached_response,
            )
        
        logger.info("LLM cache miss")
        await metrics.increment("cache_misses")
        async with llm_semaphore:
            generated_text = await provider.generate(request.message)

        await set_cached_response(
            cache_key,
            generated_text,
        )


        logger.info(
            "LLM request completed in %.3f seconds",
            perf_counter() - start,
        )
        await metrics.record_latency(perf_counter() - start)


        return ChatResponse(
            model=provider.model,
            response=generated_text,
        )

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected gateway error")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gateway temporarily unavailable",
        ) from exc