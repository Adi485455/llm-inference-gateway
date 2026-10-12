from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_provider import (
    GroqProvider,
    LLMProviderError,
)

router = APIRouter(prefix="/v1", tags=["Chat"])

provider = GroqProvider()


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    try:
        generated_text = await provider.generate(request.message)

        return ChatResponse(
            model=provider.model,
            response=generated_text,
        )

    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc