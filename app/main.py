from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="A lightweight gateway for LLM inference requests.",
)

app.include_router(health_router)
app.include_router(chat_router)