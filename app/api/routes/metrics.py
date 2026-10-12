from fastapi import APIRouter, Depends

from app.core.metrics import metrics
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/admin",
    tags=["Monitoring"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/metrics")
async def get_metrics():
    return await metrics.snapshot()